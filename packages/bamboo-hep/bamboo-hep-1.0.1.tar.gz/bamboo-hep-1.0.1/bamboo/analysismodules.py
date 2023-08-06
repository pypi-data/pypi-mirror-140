"""
Minimally, ``bambooRun`` needs a class with a constructor that takes a single argument
(the list of command-line arguments that it does not recognize as its own), and a
``run`` method  that takes no arguments.
:py:mod:`bamboo.analysismodules` provides more interesting base classes, starting from
:py:class:`~bamboo.analysismodules.AnalysisModule`, which implements a large part of
the common functionality for loading samples and distributing worker tasks.
:py:class:`~bamboo.analysismodules.HistogramsModule` specializes this further
for modules that output stack histograms, and
:py:class:`~bamboo.analysismodules.NanoAODHistoModule` supplements this
with loading the decorations for NanoAOD, and merging of the counters for generator weights etc.

.. note:: When defining a base class that should also be usable
   for other things than only making plots or only making skims
   (e.g. both of these) it should not inherit from
   :py:class:`~bamboo.analysismodules.HistogramsModule` or
   :py:class:`~bamboo.analysismodules.SkimmerModule`
   (but the concrete classes should); otherwise a concrete class
   may end up inheriting from both (at which point the method
   resolution order will decide whether it behaves as a skimmer
   or a plotter, and the result may not be obvious).

   A typical case should look like this:

   .. code-block:: python

      class MyBaseClass(NanoAODModule):
          ...  # define addArgs, prepareTree etc.
      class MyPlotter(MyBaseClass, HistogramsModule):
          ...
      class MySkimmer(MyBaseClass, SkimmerModule):
          ...

"""
import argparse
import logging
import os.path
import resource
from collections import defaultdict
from functools import partial
from itertools import chain
from timeit import default_timer as timer

from . import utils as utils
from .analysisutils import (addLumiMask, getAFileFromAnySample,
                            parseAnalysisConfig, readEnvConfig)

logger = logging.getLogger(__name__)


def reproduceArgv(args, group):
    # Reconstruct the module-specific arguments (to pass them to the worker processes later on)
    assert isinstance(group, argparse._ArgumentGroup)
    argv = []
    for action in group._group_actions:
        if isinstance(action, argparse._StoreTrueAction):
            if getattr(args, action.dest):
                argv.append(action.option_strings[0])
        elif isinstance(action, argparse._AppendAction):
            items = getattr(args, action.dest)
            if items:
                for item in items:
                    argv.append(f"{action.option_strings[0]}={item}")
        elif isinstance(action, argparse._StoreAction):
            val = getattr(args, action.dest)
            if isinstance(val, list):
                argv.append(f"{action.option_strings[0]}=" + " ".join(str(v) for v in val))
            elif val is not None:
                argv.append(f"{action.option_strings[0]}={val}")
        else:
            raise RuntimeError(f"Reconstruction of action {action} not supported")
    return argv


def parseRunRange(rrStr):
    return tuple(int(t.strip()) for t in rrStr.split(","))


def parseEras(eraStr):
    if ":" in eraStr:
        eraMode, eras = eraStr.split(":")
        return (eraMode, list(eras.split(",")))
    else:
        if eraStr in ("all", "combined", "split"):
            return (eraStr, None)
        else:
            return ("all", list(eraStr.split(",")))


class AnalysisModule:
    """ Base analysis module

    Adds common infrastructure for parsing analysis config files
    and running on a batch system, with customization points for
    concrete classes to implement
    """
    CustomSampleAttributes = ["db", "split", "files", "run_range", "certified_lumi_file"]

    def __init__(self, args):
        """ Constructor

        set up argument parsing, calling :py:meth:`~bamboo.analysismodules.AnalysisModule.addArgs`
        and :py:meth:`~bamboo.analysismodules.AnalysisModule.initialize`

        :param args: list of command-line arguments that are not parsed by ``bambooRun``
        """
        parser = argparse.ArgumentParser(description=(
            "Run an analysis, i.e. process the samples in an analysis description file with a module "
            "(subclass of bamboo.analysismodules.AnalysisModule). "
            "There are three modes, specified by the --distributed option: "
            "if unspecified (or 'sequential'), one program processes all samples and collects the results; "
            "--distributed=driver does the same, but launches worker tasks "
            "(the same program with --distributed=worker, therefore some of the options only apply "
            "to 'driver' or 'worker' mode, or have a different interpretation) "
            "to process the samples, for instance on a batch system "
            "(depending on the settings in the --envConfig file)."))
        parser.add_argument("-m", "--module", type=str, default="bamboo.analysismodules:AnalysisModule",
                            help="Module to run (format: modulenameOrPath[:classname])")
        parser.add_argument("-v", "--verbose", action="store_true", help="Run in verbose mode")
        parser.add_argument("--distributed", type=str,
                            help="Role in distributed mode", default="sequential",
                            choices=["sequential", "parallel", "worker", "driver", "finalize"])
        parser.add_argument(
            "input", nargs="*",
            help="Input: analysis description yml file (driver mode) or files to process (worker mode)")
        parser.add_argument("-o", "--output", type=str, default=".",
                            help="Output directory (driver mode) or file (worker mode) name")
        parser.add_argument("--interactive", "-i", action="store_true",
                            help="Interactive mode (initialize to an IPython shell for exploration)")
        parser.add_argument("--maxFiles", type=int, default=-1,
                            help=("Maximum number of files to process per sample "
                                  "(all by default, 1 may be useful for tests)"))
        parser.add_argument("-t", "--threads", type=int,
                            help="Enable implicit multithreading, specify number of threads to launch")
        parser.add_argument("--print-frequency", type=int, default=12000,
                            help=("Frequency for printing progress messages "
                                  "(to disable, a negative value can be passed)"))
        parser.add_argument("--git-policy", type=str, choices=["testing", "committed", "tagged", "pushed"],
                            help="Required git state for the config and module repository")
        driver = parser.add_argument_group(
            "non-worker mode only (--distributed=driver, finalize, or unspecified) optional arguments")
        driver.add_argument("--envConfig", type=str,
                            help=("Config file to read computing environment configuration from "
                                  "(batch system, storage site etc.)"))
        driver.add_argument("--onlyprepare", action="store_true",
                            help=("Only run preparation step, to quickly check the validity for all inputs "
                                  "(meaningless in distributed mode)"))
        driver.add_argument("--onlypost", action="store_true",
                            help="Only run postprocessing step on previous results")
        driver.add_argument("--eras", type=parseEras, default=("all", None),
                            help=("Select eras to consider, and which plots to make "
                                  "(format: '[all|split|combined]:[era1,era2...]')"))
        worker = parser.add_argument_group("worker mode only (--distributed=worker) arguments")
        worker.add_argument("--treeName", type=str, default="Events", help="Tree name (default: Events)")
        worker.add_argument("--runRange", type=parseRunRange, help="Run range (format: 'firstRun,lastRun')")
        worker.add_argument("--certifiedLumiFile", type=str,
                            help="(local) path of a certified lumi JSON file")
        worker.add_argument("--sample", type=str,
                            help="Sample name (as in the samples section of the analysis configuration)")
        worker.add_argument("--input", action="append", dest="filelists",
                            help="File with the list of files to read")
        worker.add_argument("--anaConfig", type=str, default=None,
                            help="Analysis description yml file provided to the driver")
        worker.add_argument("--versions-file", type=str, default=None,
                            help="Versions file to compare with")
        specific = parser.add_argument_group("module-specific arguments")
        self.addArgs(specific)
        self._specificArgsGroup = specific
        self.args = parser.parse_args(args)
        self._envConfig = None
        self._analysisConfig = None
        self._sampleFilesResolver = None
        self._gitPolicy = None
        self.initialize()

    def addArgs(self, parser):
        """
        Hook for adding module-specific argument parsing (receives an argument group),
            parsed arguments are available in ``self.args`` afterwards
        """
        pass

    @property
    def specificArgv(self):
        return reproduceArgv(self.args, self._specificArgsGroup)

    def initialize(self):
        """ Hook for module-specific initialization (called from the constructor after parsing arguments) """
        pass

    @property
    def inputs(self):
        inputs = list(self.args.input)
        if self.args.distributed == "worker" and self.args.filelists:
            for ifl in self.args.filelists:
                with open(ifl) as iflf:
                    inputs += [ln.strip() for ln in iflf if len(ln.strip()) > 0]
        return inputs

    @property
    def envConfig(self):
        if self._envConfig is None:
            self._envConfig = readEnvConfig(self.args.envConfig)
        return self._envConfig

    @property
    def analysisConfigName(self):
        if self.args.distributed == "worker":
            return self.args.anaConfig
        else:
            return self.args.input[0]

    @property
    def analysisConfig(self):
        if self._analysisConfig is None:
            self._analysisConfig = parseAnalysisConfig(self.analysisConfigName)
            self.customizeAnalysisCfg(self._analysisConfig)
        return self._analysisConfig

    @property
    def sampleFilesResolver(self):
        from .analysisutils import sample_resolveFiles
        cfgDir = os.path.dirname(utils.labspath(self.analysisConfigName))
        resolver = partial(
            sample_resolveFiles,
            dbCache=self.analysisConfig.get("dbcache"), envConfig=self.envConfig, cfgDir=cfgDir)
        if self.args.maxFiles <= 0:
            return resolver
        else:
            def maxFilesResolver(smpName, smpConfig, maxFiles=-1, resolve=None):
                inputFiles = resolve(smpName, smpConfig)
                if maxFiles > 0 and maxFiles < len(inputFiles):
                    logger.warning(
                        f"Only processing first {maxFiles:d} of {len(inputFiles):d} "
                        f"files for sample {smpName}")
                    inputFiles = inputFiles[:maxFiles]
                return inputFiles
            return partial(maxFilesResolver, maxFiles=self.args.maxFiles, resolve=resolver)

    @property
    def gitPolicy(self):
        if self._gitPolicy is None:
            if self.args.git_policy:
                self._gitPolicy = self.args.git_policy
            elif self.envConfig and "git" in self.envConfig and "policy" in self.envConfig["git"]:
                self._gitPolicy = self.envConfig["git"]["policy"]
            else:
                self._gitPolicy = "testing"
        return self._gitPolicy

    def getATree(self, fileName=None, sampleName=None, config=None):
        """
        Retrieve a representative TTree, e.g. for defining the plots or interactive inspection,
            and a dictionary with metadatas
        """
        if self.args.distributed == "worker":
            from .root import gbl
            tup = gbl.TChain(self.args.treeName)
            if not tup.Add(self.inputs[0], 0):
                raise OSError(f"Could not open file {self.inputs[0]}")
            return tup, "", {}
        else:
            if len(self.args.input) != 1:
                raise RuntimeError(
                    "Main process (driver, finalize, or non-distributed) needs exactly one "
                    "argument (analysis description YAML file)")
            analysisCfg = (config if config is not None else self.analysisConfig)
            if fileName and sampleName:
                sampleCfg = analysisCfg["samples"][sampleName]
            else:
                sampleName, sampleCfg, fileName = getAFileFromAnySample(
                    analysisCfg["samples"], resolveFiles=self.sampleFilesResolver)
            logger.debug(f"getATree: using a file from sample {sampleName} ({fileName})")
            from .root import gbl
            tup = gbl.TChain(analysisCfg.get("tree", "Events"))
            if not tup.Add(fileName, 0):
                raise OSError(f"Could not open file {fileName}")
            return tup, sampleName, sampleCfg

    def customizeAnalysisCfg(self, analysisCfg):
        """
        Hook to modify the analysis configuration before jobs are created
            (only called in driver or non-distributed mode)
        """
        pass

    def run(self):
        """ Main method

        Depending on the arguments passed, this will:

        * if ``-i`` or ``--interactive``, call :py:meth:`~bamboo.analysismodules.AnalysisModule.interact`
          (which could do some initialization and start an IPython shell)
        * if ``--distributed=worker`` call :py:meth:`~bamboo.analysismodules.AnalysisModule.processTrees`
          with the appropriate input, output, treename, lumi mask and run range
        * if ``--distributed=driver`` or not given (sequential mode): parse the analysis configuration file,
          construct the tasks with :py:meth:`~bamboo.analysismodules.AnalysisModule.getTasks`, run them
          (on a batch cluster or in the same process with
          :py:meth:`~bamboo.analysismodules.AnalysisModule.processTrees`),
          and finally call :py:meth:`~bamboo.analysismodules.AnalysisModule.postProcess` with the results.
        """
        from .workflow import run_interact, run_worker, run_notworker
        if self.args.interactive:
            run_interact(self)
        else:
            if self.args.distributed == "worker":
                run_worker(self)
            else:
                run_notworker(self)

    def getTasks(self, analysisCfg, resolveFiles=None, **extraOpts):
        """ Get tasks from analysis configs (and args), called in for driver or sequential mode

        :returns: a list of :py:class:`~bamboo.analysismodules.SampleTask` instances
        """
        from .workflow import SampleTask
        tasks = []
        sel_eras = analysisCfg["eras"].keys()
        if self.args.eras[1]:
            sel_eras = list(era for era in sel_eras if era in self.args.eras[1])
        for sName, sConfig in analysisCfg["samples"].items():
            opts = dict(extraOpts)
            if "certified_lumi_file" in sConfig:
                opts["certifiedLumiFile"] = sConfig.get("certified_lumi_file")
            if "run_range" in sConfig:
                opts["runRange"] = ",".join(str(rn) for rn in sConfig.get("run_range"))
            opts["sample"] = sName
            if "era" not in sConfig or sConfig["era"] in sel_eras:
                tasks.append(SampleTask(
                    sName, outputFile=f"{sName}.root", kwargs=opts,
                    config=sConfig, resolver=resolveFiles))
        return tasks

    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        """ Do postprocessing on the results of the tasks, if needed

        should be implemented by concrete modules

        :param taskList: ``(inputs, output), kwargs`` for the tasks (list, string, and dictionary)
        :param config: parsed analysis configuration file
        :param workdir: working directory for the current run
        :param resultsdir: path with the results files
        """
        pass


class HistogramsModule(AnalysisModule):
    """ Base histogram analysis module """
    def __init__(self, args):
        """ Constructor

        Defines a ``plotList`` member variable, which will store a list of plots
        (the result of :py:meth:`~bamboo.analysismodules.HistogramsModule.definePlots`,
        which will be called after :py:meth:`~bamboo.analysismodules.HistogramsModule.prepareTree`).
        The :py:meth:`~bamboo.analysismodules.AnalysisModule.postProcess` method specifies
        what to do with the results.
        """
        super().__init__(args)
        self.plotList = []
        self.plotDefaults = {}

    def addArgs(self, parser):
        super().addArgs(parser)
        parser.add_argument("--plotIt", type=str, default="plotIt",
                            help="plotIt executable to use (default is taken from $PATH)")

    def initialize(self):
        """ initialize """
        if self.args.distributed == "worker" and len(self.inputs) == 0:
            raise RuntimeError("Worker task needs at least one input file")

    def makeBackendAndPlotList(  # for lack of a better name
            self, inputFiles, tree=None, certifiedLumiFile=None, runRange=None,
            sample=None, sampleCfg=None, inputFileLists=None):
        """
        Prepare and plotList definition (internal helper)

        :param inputFiles: input file names
        :param tree: key name of the tree inside the files
        :param certifiedLumiFile: lumi mask json file name
        :param runRange: run range to consider (for efficiency of the lumi mask)
        :param sample: sample name (key in the samples block of the configuration file)
        :param sampleCfg: that sample's entry in the configuration file
        :param inputFileLists: names of files with the input files
            (optional, to avoid rewriting if this already exists)

        :returns: the backend and plot list (which can be `None` if run in
            onlyprepare" mode)
        """
        from .root import gbl
        tup = gbl.TChain(tree)
        for fName in inputFiles:
            if not tup.Add(fName, 0):
                raise OSError(f"Could not open file {fName}")
        tree, noSel, backend, runAndLS = self.prepareTree(tup, sample=sample, sampleCfg=sampleCfg)
        if self.args.onlyprepare:
            return backend, None
        if certifiedLumiFile:
            noSel = addLumiMask(noSel, certifiedLumiFile, runRange=runRange, runAndLS=runAndLS)
        if hasattr(backend, "inputFileLists"):  # compiled
            backend.inputFileLists = inputFileLists

        start = timer()
        plotList = self.definePlots(tree, noSel, sample=sample, sampleCfg=sampleCfg)
        end = timer()
        maxrssmb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        logger.info(
            f"{len(plotList):d} plots defined for {sample} in {end - start:.2f}s, max RSS: {maxrssmb:.2f}MB")

        # make a list of suggested nuisance parameters
        systNuis = set()
        for varn in backend.allSysts:
            for suff in ("up", "down"):
                if varn.endswith(suff):
                    varn = varn[:-len(suff)]
            systNuis.add(varn)
        if systNuis:
            logger.info("Systematic shape variations impacting any plots: {}".format(
                ", ".join(sorted(systNuis))))

        return backend, plotList

    # makeBackendAndPlotList customisation points

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        """ Create decorated tree, selection root (noSel), backend, and (run,LS) expressions

        should be implemented by concrete modules

        :param tree: decorated tree
        :param sample: sample name (as in the samples section of the analysis configuration file)
        :param sampleCfg: that sample's entry in the configuration file
        """
        return tree, None, None, None

    def definePlots(self, tree, noSel, sample=None, sampleCfg=None):
        """ Main method: define plots on the trees (for a give systematic variation)

        should be implemented by concrete modules, and return a list of
        :py:class:`bamboo.plots.Plot` objects.
        The structure (name, binning) of the histograms should not depend on the sample, era,
        and the list should be the same for all values
        (the weights and systematic variations associated with weights or collections
        may differ for data and different MC samples, so the actual set of histograms
        will not be identical).

        :param tree: decorated tree
        :param noSel: base selection
        :param sample: sample name (as in the samples section of the analysis configuration file)
        :param sampleCfg: that sample's entry in the configuration file
        """
        return []  # plot list

    def mergeCounters(self, outF, infileNames, sample=None):
        """ Merge counters

        should be implemented by concrete modules

        :param outF: output file (TFile pointer)
        :param infileNames: input file names
        :param sample: sample name
        """
        pass

    def readCounters(self, resultsFile):
        """ Read counters from results file

        should be implemented by concrete modules, and return a dictionary with
        counter names and the corresponding sums

        :param resultsFile: TFile pointer to the results file
        """
        return dict()

    def getPlotList(self, fileHint=None, sampleHint=None, resultsdir=None, config=None):
        """
        Helper method for postprocessing: construct the plot list

        The path (and sample name) of an input file can be specified,
        otherwise the results directory is searched for a skeleton tree.
        Please note that in the latter case, the skeleton file is arbitrary
        (in practice it probably corresponds to the first sample encountered
        when running in sequential or ``--distributed=driver`` mode), so if
        the postprocessing depends on things that are different between
        samples, one needs to be extra careful to avoid surprises.

        :param fileHint: name of an input file for one of the samples
        :param sampleHint: sample name for the input file passed in ``fileHint``
        :param resultsdir: directory with the produced results files
            (mandatory if no ``fileHint`` and ``sampleHint`` are passed)
        :param config: analysis config (to override the default - optional)
        """
        if config is None:
            config = self.analysisConfig
        if fileHint is not None and sampleHint is not None:
            pass
        elif resultsdir is not None:
            try:
                import os
                prefix = "__skeleton__"
                suffix = ".root"
                skelFn = next(fn for fn in os.listdir(resultsdir)
                              if fn.startswith(prefix) and fn.endswith(suffix))
                fileHint = os.path.join(resultsdir, skelFn)
                sampleHint = skelFn[len(prefix):-len(suffix)]
            except StopIteration:
                raise RuntimeError(f"No skeleton file found in {resultsdir}")
            if sampleHint not in config["samples"]:
                raise RuntimeError(
                    f"Found a skeleton file for sample {sampleHint}, which is not in the list of samples.\n"
                    "This is probably due to customisation of the configuration before postprocessing.\n"
                    "Please rename the skeleton, reorder the samples to prevent this from happening, "
                    "or insert\n"
                    ">>> if not self.plotList:\n"
                    ">>>     self.plotList = self.getPlotList(resultsdir=resultsdir, config=config)\n"
                    "before modifying the config when overriding the postprocess method")
        else:
            raise RuntimeError(
                "Either the results directory, or an input file and corresponding sample name, "
                "needs to be specified")
        tup, smpName, smpCfg = self.getATree(fileName=fileHint, sampleName=sampleHint, config=config)
        tree, noSel, backend, runAndLS = self.prepareTree(tup, sample=smpName, sampleCfg=smpCfg)
        return self.definePlots(tree, noSel, sample=smpName, sampleCfg=smpCfg)

    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        """ Postprocess: run plotIt

        The list of plots is created if needed (from a representative file,
        this enables rerunning the postprocessing step on the results files),
        and then plotIt is executed
        """
        if not self.plotList:
            self.plotList = self.getPlotList(resultsdir=resultsdir, config=config)
        from .plots import Plot, DerivedPlot, CutFlowReport
        plotList_cutflowreport = [ap for ap in self.plotList if isinstance(ap, CutFlowReport)]
        plotList_plotIt = [ap for ap in self.plotList
                           if (isinstance(ap, Plot) or isinstance(ap, DerivedPlot))
                           and len(ap.binnings) == 1]
        eraMode, eras = self.args.eras
        if eras is None:
            eras = list(config["eras"].keys())
        if plotList_cutflowreport:
            from .analysisutils import printCutFlowReports
            printCutFlowReports(
                config, plotList_cutflowreport, workdir=workdir, resultsdir=resultsdir,
                readCounters=self.readCounters, eras=(eraMode, eras), verbose=self.args.verbose)
        if plotList_plotIt:
            from .analysisutils import writePlotIt, runPlotIt
            cfgName = os.path.join(workdir, "plots.yml")
            writePlotIt(
                config, plotList_plotIt, cfgName, eras=eras, workdir=workdir, resultsdir=resultsdir,
                readCounters=self.readCounters, plotDefaults=self.plotDefaults,
                vetoFileAttributes=self.__class__.CustomSampleAttributes)
            runPlotIt(
                cfgName, workdir=workdir, plotIt=self.args.plotIt, eras=(eraMode, eras),
                verbose=self.args.verbose)


class NanoAODModule(AnalysisModule):
    """
    A :py:class:`~bamboo.analysismodules.AnalysisModule` extension for NanoAOD,
        adding decorations and merging of the counters
    """
    def isMC(self, sampleName):
        return not any(sampleName.startswith(pd) for pd in (
            "BTagCSV", "BTagMu", "Charmonium", "DisplacedJet", "DoubleEG", "DoubleMuon",
            "DoubleMuonLowMass", "EGamma", "FSQJet1", "FSQJet2", "FSQJets", "HTMHT", "HeavyFlavour",
            "HighEGJet", "HighMultiplicity", "HighPtLowerPhotons", "IsolatedBunch", "JetHT", "MET",
            "MinimumBias", "MuOnia", "MuonEG", "NoBPTX", "SingleElectron", "SingleMuon",
            "SinglePhoton", "Tau", "ZeroBias"))

    def prepareTree(self, tree, sample=None, sampleCfg=None, description=None, backend=None):
        """ Add NanoAOD decorations, and create an RDataFrame backend

        In addition to the arguments needed for the base class
        :py:meth:`~bamboo.analysismodules.AnalysisModule.prepareTree`` method,
        a description of the tree, and settings for reading systematic variations
        or corrections from alternative branches, or calculating these on the fly,
        should be passed, such that the decorations can be constructed accordingly.

        :param description: description of the tree format, and configuration for
            reading or calculating systematic variations and corrections,
            a :py:class:`~bamboo.treedecorators.NanoAODDescription` instance
            (see also :py:meth:`bamboo.treedecorators.NanoAODDescription.get`)
        """
        from .treedecorators import decorateNanoAOD
        t = decorateNanoAOD(tree, description=description)
        from .dataframebackend import getBackend
        be, noSel = getBackend(
            t, name=backend, nThreads=self.args.threads)
        return t, noSel, be, (t.run, t.luminosityBlock)

    def mergeCounters(self, outF, infileNames, sample=None):
        """ Merge the ``Runs`` trees """
        from .root import gbl
        cruns = gbl.TChain("Runs")
        for fn in infileNames:
            cruns.Add(fn)
        outF.cd()
        runs = cruns.CloneTree()
        runs.Write("Runs")

    def readCounters(self, resultsFile):
        """ Sum over each leaf of the (merged) ``Runs`` tree (except ``run``) """
        runs = resultsFile.Get("Runs")
        from .root import gbl
        if (not runs) or (not isinstance(runs, gbl.TTree)):
            raise RuntimeError(f"No tree with name 'Runs' found in {resultsFile.GetName()}")
        sums = dict()
        runs.GetEntry(0)
        for lv in runs.GetListOfLeaves():
            lvn = lv.GetName()
            if lvn != "run":
                if lv.GetLeafCount():
                    lvcn = lv.GetLeafCount().GetName()
                    if lvcn in sums:
                        del sums[lvcn]
                    sums[lvn] = [lv.GetValue(i) for i in range(lv.GetLeafCount().GetValueLong64())]
                else:
                    sums[lvn] = lv.GetValue()
        for entry in range(1, runs.GetEntries()):
            runs.GetEntry(entry)
            for cn, vals in sums.items():
                if hasattr(vals, "__iter__"):
                    entryvals = getattr(runs, cn)
                    # warning and workaround (these should be consistent for all NanoAODs in a sample)
                    if len(vals) != len(entryvals):
                        logger.error(
                            f"Runs tree: array of sums {cn} has a different length in entry "
                            f"{entry:d}: {len(entryvals):d} (expected {len(vals):d})")
                    for i in range(min(len(vals), len(entryvals))):
                        vals[i] += entryvals[i]
                else:
                    sums[cn] += getattr(runs, cn)
        return sums


class NanoAODHistoModule(NanoAODModule, HistogramsModule):
    """
    A :py:class:`~bamboo.analysismodules.HistogramsModule` for NanoAOD,
        with decorations and merging of counters from
        :py:class:`~bamboo.analysismodules.NanoAODModule`
    """
    def __init__(self, args):
        super().__init__(args)


class SkimmerModule(HistogramsModule):
    """
    Base skimmer module

    Left for backwards-compatibility, please use a
    :py:class:`~bamboo.analysismodules.HistogramsModule` that defines one or more
    :py:class:`bamboo.plots.Skim` products instead.
    """
    def addArgs(self, parser):
        super().addArgs(parser)
        parser.add_argument(
            "--keepOriginalBranches", action="store_true",
            help="Keep all original branches (in addition to those defined by the module)")
        parser.add_argument("--maxSelected", type=int, default=-1,
                            help="Maximum number of accepted events (default: -1 for all)")
        parser.add_argument("--outputTreeName", type=str, default="Events",
                            help="Name of the output tree")

    def definePlots(self, tree, noSel, sample=None, sampleCfg=None):
        from .plots import Skim
        finalSel, brToKeep = self.defineSkimSelection(tree, noSel, sample=sample, sampleCfg=sampleCfg)
        return [
            Skim(
                self.args.outputTreeName, brToKeep, finalSel, maxSelected=self.args.maxSelected,
                keepOriginal=(Skim.KeepAll if self.args.keepOriginalBranches else None)

            )
        ]

    def defineSkimSelection(self, tree, noSel, sample=None, sampleCfg=None):
        """ Main method: define a selection for the skim

        should be implemented by concrete modules, and return a
        :py:class:`bamboo.plots.Selection` object

        :param tree: decorated tree
        :param noSel: base selection
        :param sample: sample name (as in the samples section of the analysis configuration file)
        :param sampleCfg: that sample's entry in the configuration file

        :returns: the skim :py:class:`bamboo.plots.Selection`, and a map ``{ name: expression }``
            of branches to store (to store all the branches of the original tree in addition,
            pass --keepOriginalBranches to bambooRun; individual branches can be added
            with an entry ``name: None`` entry)
        """
        return noSel, {}


class NanoAODSkimmerModule(NanoAODModule, SkimmerModule):
    """
    A :py:class:`~bamboo.analysismodules.SkimmerModule` for NanoAOD,
        with decorations and merging of counters from
        :py:class:`~bamboo.analysismodules.NanoAODModule`
    """
    def __init__(self, args):
        super().__init__(args)


class DataDrivenContribution:
    """
    Configuration helper class for data-driven contributions

    An instance is constructed for each contribution in any of the scenarios by
    the :py:meth:`bamboo.analysismodules.DataDrivenBackgroundAnalysisModule.initialize`
    method, with the name and configuration dictionary found in YAML file.
    The :py:meth:`~bamboo.analysismodules.DataDrivenContribution.usesSample`:,
    :py:meth:`~bamboo.analysismodules.DataDrivenContribution.replacesSample`: and
    :py:meth:`~bamboo.analysismodules.DataDrivenContribution.modifiedSampleConfig`:
    methods can be customised for other things than using the data samples
    to estimate a background contribution.
    """
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.uses = config.get("uses", [])
        self.replaces = config.get("replaces", [])

    def usesSample(self, sampleName, sampleConfig):
        """ Check if this contribution uses a sample (name or group in 'uses') """
        return sampleName in self.uses or sampleConfig.get("group") in self.uses

    def replacesSample(self, sampleName, sampleConfig):
        """ Check if this contribution replaces a sample (name or group in 'replaces') """
        return sampleName in self.replaces or sampleConfig.get("group") in self.replaces

    def modifiedSampleConfig(self, sampleName, sampleConfig, lumi=None):
        """
        Construct the sample configuration for the reweighted counterpart of a sample

        The default implementation assumes a data sample and turns it into a MC sample
        (the luminosity is set as ``generated-events`` to avoid changing the normalisation).
        """
        modCfg = dict(sampleConfig)
        if sampleConfig.get("group").lower() == "data":
            modCfg.update({
                "type": "mc",
                "generated-events": lumi,
                "cross-section": 1.,
                "group": self.name
            })
        else:
            modCfg["group"] = self.name
        return modCfg


class DataDrivenBackgroundAnalysisModule(AnalysisModule):
    """
    :py:class:`~bamboo.analysismoduldes.AnalysisModule` with support for data-driven backgrounds

    A number of contributions can be defined, each based on a list of samples or
    groups needed to evaluate the contribution (typically just data) and a list
    of samples or groups that should be left out when making the plot with
    data-driven contributions.
    The contributions should be defined in the analysis YAML file, with a block
    ``datadriven`` (at the top level) that could look as follows:

    .. code-block:: yaml

     datadriven:
       chargeMisID:
         uses: [ data ]
         replaces: [ DY ]
       nonprompt:
         uses: [ data ]
         replaces: [ TTbar ]

    The ``--datadriven`` command-line switch then allows to specify a scenario
    for data-driven backgrounds, i.e. a list of data-driven contributions to
    include (``all`` and ``none`` are also possible, the latter is the default
    setting).
    The parsed contributions are available as ``self.datadrivenContributions``,
    and the scenarios (each list is a list of contributions) as
    ``self.datadrivenScenarios``.
    """
    def addArgs(self, parser):
        super().addArgs(parser)
        parser.add_argument(
            "--datadriven", action="append", help=(
                "Scenarios for data-driven backgrounds ('all' for all available in yaml, "
                "'none' for everything from MC (default), or a comma-separated list "
                "of contributions; several can be specified)"))

    def initialize(self):
        super().initialize()
        ddConfig = self.analysisConfig.get("datadriven", dict())
        if not self.args.datadriven:
            scenarios = [[]]
        elif not ddConfig:
            raise RuntimeError(
                "--datadriven argument passed, but no 'datadriven' top-level block "
                "was found in the analysis YAML configuration file")
        else:
            scenarios = []
            for arg in self.args.datadriven:
                if arg.lower() == "all":
                    sc = tuple(sorted(ddConfig.keys()))
                    logger.info("--datadriven=all selected contributions {}".format(", ".join(sc)))
                elif arg.lower() == "none":
                    sc = tuple()
                else:
                    sc = tuple(sorted(arg.split(",")))
                    if any(st not in ddConfig for st in sc):
                        raise RuntimeError("Unknown data-driven contribution(s): {}".format(
                            ", ".join(st for st in sc if st not in ddConfig)))
                if sc not in scenarios:
                    scenarios.append(sc)
            if not scenarios:
                raise RuntimeError(
                    f"No data-driven scenarios, please check the arguments "
                    f"({self.args.datadriven}) and config ({str(ddConfig)})")
        self.datadrivenScenarios = scenarios
        self.datadrivenContributions = {
            contribName: DataDrivenContribution(contribName, config)
            for contribName, config in ddConfig.items()
            if any(contribName in scenario for scenario in scenarios)
        }
        if self.datadrivenContributions:
            logger.info("Requested data-driven scenarios: {}; selected contributions: {}".format(
                ", ".join("+".join(contrib for contrib in scenario)
                          for scenario in self.datadrivenScenarios),
                ",".join(self.datadrivenContributions.keys())))
        else:
            logger.info("No data-driven contributions selected")


class DataDrivenBackgroundHistogramsModule(DataDrivenBackgroundAnalysisModule, HistogramsModule):
    """
    :py:class:`~bamboo.analysismoduldes.HistogramsModule` with support for data-driven backgrounds

    see the :py:class:`~bamboo.analysismoduldes.DataDrivenBackgroundAnalysisModule`
    class for more details about configuring data-driven backgrounds, and the
    :py:class:`~bamboo.plots.SelectionWithDataDriven` class for ensuring the
    necessary histograms are filled correctly.
    :py:class:`~bamboo.analysismoduldes.HistogramsModule` writes
    the histograms for the data-driven contributions to different files.
    This one runs ``plotIt`` for the different scenarios.
    """
    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        if not self.plotList:
            self.plotList = self.getPlotList(resultsdir=resultsdir, config=config)
        from .plots import Plot, DerivedPlot, CutFlowReport
        plotList_cutflowreport = [ap for ap in self.plotList if isinstance(ap, CutFlowReport)]
        plotList_plotIt = [ap for ap in self.plotList
                           if (isinstance(ap, Plot) or isinstance(ap, DerivedPlot))
                           and len(ap.binnings) == 1]
        eraMode, eras = self.args.eras
        if eras is None:
            eras = list(config["eras"].keys())
        from .analysisutils import printCutFlowReports
        for sc, _scPlots in self.getPlotsByDatadrivenScenario(plotList_cutflowreport).items():
            config_sc = self.configWithDatadrivenSamples(config, sc)
            printCutFlowReports(
                config_sc, plotList_cutflowreport, suffix="_".join(sc),
                workdir=workdir, resultsdir=resultsdir, eras=(eraMode, eras),
                readCounters=self.readCounters, verbose=self.args.verbose)
        from .analysisutils import writePlotIt, runPlotIt
        for sc, scPlots in self.getPlotsByDatadrivenScenario(plotList_plotIt).items():
            scName = "_".join(chain(["plots"], sc))
            cfgName = os.path.join(workdir, f"{scName}.yml")
            config_sc = self.configWithDatadrivenSamples(config, sc)
            # TODO possible improvement: cache counters (e.g. by file name)
            #      - needs a change in readCounters interface
            writePlotIt(
                config_sc, scPlots, cfgName,
                eras=eras, workdir=workdir, resultsdir=resultsdir,
                readCounters=self.readCounters, plotDefaults=self.plotDefaults,
                vetoFileAttributes=self.__class__.CustomSampleAttributes)
            runPlotIt(
                cfgName, plotsdir=scName, eras=(eraMode, eras),
                workdir=workdir, plotIt=self.args.plotIt,
                verbose=self.args.verbose)

    def getPlotsByDatadrivenScenario(self, plotList):
        from .plots import SelectionWithSub
        # - step 1: group per max-available scenario (combination of data-driven contributions
        #           - not the same as configured scenarios, since this one is per-plot)
        plots_by_availSc = defaultdict(list)
        for p in plotList:
            pContribs = SelectionWithSub.getSubsForPlot(p, requireActive=False, silent=True)
            plots_by_availSc[tuple(sorted(pContribs))].append(p)
        # - step 2: collect plots for actual scenarios (avoiding adding them twice)
        plots_by_scenario = defaultdict(dict)
        for sc in self.datadrivenScenarios:
            for avSc, avPlots in plots_by_availSc.items():
                plots_by_scenario[tuple(dd for dd in sc if dd in avSc)].update({p.name: p for p in avPlots})
        return {avSc: list(avPlots.values()) for avSc, avPlots in plots_by_scenario.items()}

    def configWithDatadrivenSamples(self, config, scenario):
        # Modified samples: first remove replaced ones
        modSamples = {
            smp: smpCfg for smp, smpCfg in config["samples"].items()
            if not any(self.datadrivenContributions[contrib].replacesSample(smp, smpCfg)
                       for contrib in scenario)}
        # Then add data-driven contributions
        for contribName in scenario:
            contrib = self.datadrivenContributions[contribName]
            for smp, smpCfg in config["samples"].items():
                if contrib.usesSample(smp, smpCfg):
                    if "era" in smpCfg:
                        lumi = config["eras"][smpCfg["era"]]["luminosity"]
                    else:
                        lumi = sum(eraCfg["luminosity"] for eraCfg in config["eras"].values())
                    modSamples[f"{smp}{contribName}"] = contrib.modifiedSampleConfig(smp, smpCfg, lumi=lumi)
        config_sc = dict(config)  # shallow copy
        config_sc["samples"] = modSamples
        return config_sc
