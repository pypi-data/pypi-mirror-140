"""
Helpers for integrating bamboo in analysis workflows (git and workflow management tools)
    and improving reproducibility
"""
import dataclasses
import datetime
import enum
import logging
import os.path
import resource
import shutil
import subprocess
import urllib.parse
from collections import defaultdict
from functools import partial
from itertools import chain
from timeit import default_timer as timer

from . import utils as utils
from .analysismodules import parseRunRange

logger = logging.getLogger(__name__)


def modAbsPath(modArg):
    # Put absolute path if module is specified by file
    mod_clName = None
    if ":" in modArg:
        modArg, mod_clName = modArg.split(":")
    if os.path.isfile(modArg):
        modArg = utils.labspath(modArg)
    if mod_clName:
        modArg = ":".join((modArg, mod_clName))
    return modArg


def _callGit(args, cwd=None, stderr=None):
    return subprocess.check_output(["git"] + args, cwd=cwd, stderr=stderr).decode().strip()


hasGit = shutil.which("git") is not None
if not hasGit:
    logger.error("No git executable found")
else:
    gitVersionStr = subprocess.check_output(["git", "--version"]).decode().strip()
    logger.debug(f"Found GIT: {gitVersionStr}")
    import packaging.version
    gitVersion = packaging.version.parse(gitVersionStr.split()[2])
    if gitVersion < packaging.version.parse("2.5"):
        logger.warning(
            "The git version is below 2.5, please consider installing "
            "a more recent version to take advantage of worktrees")


class NotGitTrackedException(Exception):
    def __init__(self, path, message):
        self.path = path
        super().__init__(message)


def splitGitWorkdir(filePath):
    """ Find the top-level directory, relative path, and .git directory for a file """
    filePath = utils.labspath(os.path.expanduser(filePath))
    fDir = os.path.dirname(utils.labspath(filePath))
    if not hasGit:
        raise NotGitTrackedException(
            filePath, f"Cannot check git status of {filePath} (no git executable found)")
    try:
        cdUp = _callGit(["rev-parse", "--show-cdup"], cwd=fDir, stderr=subprocess.DEVNULL)
        topLevel = os.path.normpath(os.path.join(fDir, cdUp))
    except subprocess.CalledProcessError as ex:
        if ex.returncode == 128:
            raise NotGitTrackedException(
                filePath, f"File {filePath} is not in a git repository") from None
        raise
    fileRelPath = os.path.relpath(filePath, topLevel)
    logger.debug(f"Repository for file {filePath}: {topLevel}, relative path: {fileRelPath}")
    return topLevel, fileRelPath


def getRemotes(workdir):
    remotes = _callGit(["remote"], cwd=workdir).split()
    remInfo = {}
    for remName in remotes:
        try:
            remInfo[remName] = {
                "url": _callGit(["remote", "get-url", remName],
                                cwd=workdir, stderr=subprocess.DEVNULL),
                "url_push": _callGit(["remote", "get-url", "--push", remName],
                                     cwd=workdir, stderr=subprocess.DEVNULL)
            }
        except subprocess.CalledProcessError:  # git below 2.7
            remInfo[remName] = {
                "url": _callGit(["config", "--get", f"remote.{remName}.url"], cwd=workdir)
            }
    return remInfo


@dataclasses.dataclass
class GitVersionInfo:
    is_dirty: bool = False
    version: str = ""
    sha1: str = ""
    git_common: str = ""
    remotes: dict = dataclasses.field(default_factory=dict)
    tag: str = ""
    tag_remotes: list = dataclasses.field(default_factory=list)
    remote_branches: list = dataclasses.field(default_factory=list)
    untracked_files: list = dataclasses.field(default_factory=list)

    def asDict(self):
        return dataclasses.asdict(self)

    class Status(enum.IntEnum):
        DIRTY = 0
        LOCALCOMMIT = 1
        COMMIT = 2
        LOCALTAG = 3
        TAG = 4

    @property
    def status(self):
        if self.is_dirty:
            return GitVersionInfo.Status.DIRTY
        elif self.version == self.tag:
            if self.tag_remotes:
                return GitVersionInfo.Status.TAG
            else:
                return GitVersionInfo.Status.LOCALTAG
        else:
            if self.remote_branches:
                return GitVersionInfo.Status.COMMIT
            else:
                return GitVersionInfo.Status.LOCALCOMMIT

    POLICY_MIN = {
        "testing": Status.DIRTY,
        "committed": Status.LOCALCOMMIT,
        "tagged": Status.LOCALTAG,
        "pushed": Status.TAG,
    }

    @staticmethod
    def forDir(workdir, withRemote=True):
        callGit = partial(_callGit, cwd=workdir)
        inst = GitVersionInfo()
        inst.sha1 = callGit(["rev-parse", "--verify", "--short", "HEAD"])
        inst.version = callGit(["describe", "--tags", "--always", "--dirty"])
        if "-dirty" in inst.version:
            inst.is_dirty = True
        logger.debug(f"Version: {inst.version}, short hash: {inst.sha1}")
        gitCommon = callGit(["rev-parse", "--git-common-dir"])
        if gitCommon == "--git-common-dir":  # git below 2.5
            gitCommon = os.path.join(_callGit(["rev-parse", "--show-toplevel"],
                                              cwd=workdir, stderr=subprocess.DEVNULL), ".git")
        if not os.path.isabs(gitCommon):
            gitCommon = os.path.normpath(os.path.join(workdir, gitCommon))
        elif os.path.realpath(workdir) != workdir:  # symlinks in workdir, use them
            pWD, pGC = utils.realcommonpath(workdir, gitCommon)
            gitCommon = os.path.join(pWD, os.path.relpath(gitCommon, pGC))
        inst.git_common = gitCommon
        if withRemote:
            inst.remotes = {
                remNm: remInfo for remNm, remInfo in getRemotes(workdir).items()
                if urllib.parse.urlparse(remInfo["url"]).scheme}  # exclude local clones
            tags = callGit(["tag", "-l"]).split()
            tag = inst.version.split("-")[0]
            if tag in tags:  # set and find on remotes
                inst.tag = tag
                for remNm in inst.remotes:
                    try:
                        lst = callGit(["ls-remote", "--tags", remNm, tag], stderr=subprocess.DEVNULL)
                        if lst:
                            remHash = lst.split()[0]
                            locHash = callGit(["rev-parse", tag])
                            if remHash != locHash:
                                logger.error(
                                    f"Tag {tag} has a different hash on remote "
                                    f"({remHash} vs {locHash})! Please fix")
                            else:
                                inst.tag_remotes.append(remNm)
                    except subprocess.CalledProcessError:
                        logger.error(f"Could not check if tag {tag} is on remote {remNm}")
                if inst.tag_remotes:
                    logger.debug(f"Tag {tag} found in remote(s): {', '.join(inst.tag_remotes)}")
            # search for the commit on remote
            inst.remote_branches = [remBr.strip() for remBr in callGit(
                ["branch", "--remotes", "--no-color", "--contains", inst.sha1]).split()]
            if inst.remote_branches:
                logger.debug(
                    f"Commit {inst.sha1} found in remote branches: {', '.join(inst.remote_branches)}")
            # check for untracked
            untracked = callGit(["ls-files", "--others", "--exclude-standard"]).split()
            if untracked:
                if len(untracked) > 10:
                    logger.warning(f"{len(untracked):d} untracked files found in {workdir}")
                else:
                    logger.warning(f"Untracked files found in {workdir}: {', '.join(untracked)}")
                inst.untracked_files = list(untracked)
        return inst

    def check(self, what="", policy="pushed"):
        if what:
            what = f" for {what}"
        if self.status == GitVersionInfo.Status.DIRTY:
            logger.error(
                f"Your working tree{what} is dirty! "
                "Please commit, tag, and push for reproducible results")
        elif self.status == GitVersionInfo.Status.LOCALCOMMIT:
            logger.warning(
                f"Please tag and/or push commit {self.sha1}{what} "
                "for results that are reproducible beyond your local repository")
        elif self.status == GitVersionInfo.Status.COMMIT:
            logger.warning(
                f"Running with commit {self.sha1}{what}. "
                "Please tag (and push) for better traceability")
        elif self.status == GitVersionInfo.Status.LOCALTAG:
            logger.warning(
                f"Running with tag {self.tag}{what}. "
                "Please push for better traceability")
        elif self.status == GitVersionInfo.Status.TAG:
            logger.info(f"Running with tag {self.tag}{what}")
        if self.status < GitVersionInfo.POLICY_MIN[policy]:
            raise RuntimeError(
                f"Git status {self.status.name}{what} failed git policy '{policy}'")

# ############################################# #
# An experiment: externalize AnalysisModule.run #
# ############################################# #


def buildVersions(mod, withRemote=True, checkPolicy=None):
    """ Make a version dictionary """
    import pkg_resources
    versions = {"bamboo_version": pkg_resources.get_distribution("bamboo-hep").version}
    modFile = mod.args.module.split(":")[0]
    try:
        import importlib
        spec = importlib.util.find_spec(modFile)
        modFile = spec.origin
    except Exception:
        pass  # actually a file then
    from .workflow import splitGitWorkdir, GitVersionInfo, NotGitTrackedException
    try:
        cfgwdir, cfgFRel = splitGitWorkdir(mod.analysisConfigName)
        cfgVers = GitVersionInfo.forDir(cfgwdir, withRemote=withRemote)
        if cfgFRel in cfgVers.untracked_files:
            cfgVers.is_dirty = True
    except NotGitTrackedException:
        logger.error(
            f"Configuration file {mod.analysisConfigName} is not in a git repository, "
            "version tracking will not work")
        cfgwdir = None
        cfgFRel = utils.labspath(os.path.expanduser(mod.analysisConfigName))  # fallback
        cfgVers = GitVersionInfo(version="unknown-dirty", is_dirty=True)
    versions["config_version"] = cfgVers.asDict()
    modVers = None
    try:
        modwdir, modFRel = splitGitWorkdir(modFile)
        if cfgwdir == modwdir:
            modVers = cfgVers
            versions["module_version"] = versions["config_version"]
            if modFRel in cfgVers.untracked_files and not versions["config_version"]["is_dirty"]:
                versions["config_version"]["is_dirty"] = True
        else:
            modVers = GitVersionInfo.forDir(modwdir, withRemote=withRemote)
            if modFRel in modVers.untracked_files:
                modVers.is_dirty = True
            versions["module_version"] = modVers.asDict()
    except NotGitTrackedException:
        modFRel = utils.labspath(os.path.expanduser(modFile))  # fallback
        try:
            import inspect
            modPkg = inspect.getmodule(mod).__package__
            modVers = GitVersionInfo(
                git_common=modPkg, version=pkg_resources.get_distribution(modPkg).version)
            logger.warning(
                f"Module {modFile} is not in a git repository, "
                f"using package {modPkg} version {modVers.version} instead")
        except ValueError:
            modVers = GitVersionInfo(version="unknown-dirty", is_dirty=True)
            logger.error(
                f"Module {modFile} is not in a git repository, "
                "version tracking will not work")
        versions["module_version"] = modVers.asDict()
    versions["bambooRun_args"] = [
        # not keeping other options that do not influence the results
        f"--module={modFRel}:{mod.__class__.__name__}",
        cfgFRel,
    ] + mod.specificArgv
    if checkPolicy is None:
        checkPolicy = mod.gitPolicy
    if checkPolicy:
        if cfgVers == modVers:
            cfgVers.check(what="config and module", policy=checkPolicy)
        else:
            cfgVers.check(what="config", policy=checkPolicy)
            if isinstance(modVers, GitVersionInfo):
                cfgVers.check(what="module", policy=checkPolicy)
    return versions


def compareVersions(stored, current):
    isSame = True
    if stored["bamboo_version"] != current["bamboo_version"]:
        logger.warning(
            f"bamboo versions differ: stored {stored['bamboo_version']}, "
            f"now running {current['bamboo_version']}")
        isSame = False
    if stored["bambooRun_args"][0] != current["bambooRun_args"][0]:
        logger.error(
            f"Different bamboo module (stored {stored['bambooRun_args'][0]}, "
            f"now running {current['bambooRun_args'][0]})! This is almost certainly wrong")
        isSame = False
    if stored["bambooRun_args"][1] != current["bambooRun_args"][1]:
        logger.error(
            f"Different analysis config (stored {stored['bambooRun_args'][1]}, "
            f"now running {current['bambooRun_args'][1]})! This is almost certainly wrong")
        isSame = False
    if (len(stored["bambooRun_args"]) != len(current["bambooRun_args"]) or not
            all(sArg == cArg for sArg, cArg in zip(
                stored["bambooRun_args"][2:], current["bambooRun_args"][2:]))):
        logger.warning(
            f"Different module-specific arguments (stored '{' '.join(stored['bambooRun_args'][2:])}', "
            f"now running '{', '.join(current['bambooRun_args'][2:])}'. This is suspicious")
        isSame = False
    if stored["module_version"].get("git_common"):
        if stored["module_version"]["git_common"] != current["module_version"].get("git_common"):
            logger.error(
                f"Module from different repository (stored {stored['module_version']['git_common']}, "
                f"now running {current['module_version'].get('git_common')}). Be very careful")
            isSame = False
    if stored["module_version"]["version"] != current["module_version"]["version"]:
        logger.error(
            f'Module from different version (stored {stored["module_version"]["version"]}, '
            f'now running {current["module_version"]["version"]}). Be careful')
        isSame = False
    if stored["config_version"].get("git_common"):
        if stored["config_version"]["git_common"] != current["config_version"].get("git_common"):
            logger.error(
                f"config from different repository (stored {stored['config_version']['git_common']}, "
                f"now running {current['config_version'].get('git_common')}). Be very careful")
            isSame = False
    if stored["config_version"]["version"] != current["config_version"]["version"]:
        logger.error(
            f'Config from different version (stored {stored["config_version"]["version"]}, '
            f'now running {current["config_version"]["version"]}). Be careful')
        isSame = False
    return isSame


class SampleTask:
    """ Information about work to be done for single sample (input and output file, parameters etc.) """
    def __init__(self, name, inputFiles=None, outputFile=None, kwargs=None, config=None, resolver=None):
        self.name = name
        self._inputFiles = inputFiles
        self.outputFile = outputFile
        self.kwargs = kwargs
        self.config = config
        self._resolver = resolver

    @property
    def inputFiles(self):
        if self._inputFiles is None:
            self._inputFiles = self._resolver(self.name, self.config)
        return self._inputFiles


def downloadCertifiedLumiFiles(tasks, workdir="."):
    """ download certified lumi files (if needed) and replace in args """
    certifLumiFiles = {tsk.kwargs["certifiedLumiFile"]
                       for tsk in tasks if "certifiedLumiFile" in tsk.kwargs}
    # download if needed
    clf_downloaded = dict()
    for clfu in certifLumiFiles:
        purl = urllib.parse.urlparse(clfu)
        if purl.scheme in ("http", "https"):
            fname = os.path.join(workdir, purl.path.split("/")[-1])
            if os.path.exists(fname):
                logger.warning(f"File {fname} exists, it will not be downloaded again from {clfu}")
            else:
                subprocess.check_call(["wget", f"--directory-prefix={workdir}", clfu],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            clf_downloaded[clfu] = utils.labspath(fname)
    # update args
    for tsk in tasks:
        if "certifiedLumiFile" in tsk.kwargs:
            clf = tsk.kwargs["certifiedLumiFile"]
            if clf in clf_downloaded:
                tsk.kwargs["certifiedLumiFile"] = clf_downloaded[clf]

    return set(clf_downloaded.keys())


def getBatchDefaults(backend):
    if backend == "slurm":
        return {
            "sbatch_time": "0-01:00",
            "sbatch_memPerCPU": "2048",
            "stageoutFiles": ["*.root"],
            "sbatch_chdir": utils.getlcwd(),
            "sbatch_additionalOptions": ["--export=ALL"],
        }
    elif backend == "htcondor":
        return {"cmd": {
            "universe": "vanilla",
            "+MaxRuntime": f"{20*60:d}",  # 20 minutes
            "getenv": "True",
        }}


def run_interact(mod):
    """
    Interactively inspect a decorated input tree

    Available variables: ``tree`` (decorated tree), ``tup`` (raw tree),
    ``noSel`` (root selection), ``backend``, ``runAndLS`` (e.g. ``(runExpr, lumiBlockExpr)``)
    (the inputs for the lumi mask), and ``op`` (:py:mod:`bamboo.treefunctions`).
    """
    tup, smpName, smpCfg = mod.getATree()
    tree, noSel, backend, runAndLS = mod.prepareTree(tup, sample=smpName, sampleCfg=smpCfg)
    import bamboo.treefunctions as op  # noqa: F401
    import IPython
    IPython.start_ipython(argv=[], user_ns=locals())


def processOne(mod, inputFiles, outputFile, tree=None, certifiedLumiFile=None, runRange=None,
               sample=None, sampleCfg=None, inputFileLists=None):
    """
    Process inputs for one sample at a time (old processTrees), from inputs to histograms and skims

    More in detail, this will load the inputs,
    call :py:meth:`~bamboo.analysismodules.HistogramsModule.prepareTree`,
    add a lumi mask if requested,
    call :py:meth:`~bamboo.analysismodules.HistogramsModule.definePlots`,
    run over all files, and write the produced histograms to the output file.

    :param inputFiles: input file names
    :param outputFile: output file name
    :param tree: key name of the tree inside the files
    :param certifiedLumiFile: lumi mask json file name
    :param runRange: run range to consider (for efficiency of the lumi mask)
    :param sample: sample name (key in the samples block of the configuration file)
    :param sampleCfg: that sample's entry in the configuration file
    :param inputFileLists: names of files with the input files
        (optional, to avoid rewriting if this already exists)
    """
    backend, plotList = mod.makeBackendAndPlotList(
        inputFiles, tree=tree, certifiedLumiFile=certifiedLumiFile, runRange=runRange,
        sample=sample, sampleCfg=sampleCfg, inputFileLists=inputFileLists)
    if mod.args.onlyprepare:
        return

    logger.info("Start backend graph construction")
    start = timer()
    backend.buildGraph(plotList)
    end = timer()
    maxrssmb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    logger.info(f"Backend graph construction done in {end - start:.2f}s, max RSS: {maxrssmb:.2f}MB")
    from .dataframebackend import FullyCompiledBackend
    if mod.args.print_frequency > 0:
        if isinstance(backend, FullyCompiledBackend):
            logger.warning("Progress printing when using the compiled backend is disabled for now")
        else:
            backend.addDependency(headers="printprogress.h")
            from .root import gbl
            mod._progressPrinter = gbl.rdfhelpers.PrintProgress.addToNode(
                backend.rootDF, mod.args.print_frequency,
                (mod.args.threads if mod.args.threads else 1))

    logger.info("Starting to fill plots (and skims)")
    start = timer()
    backend.runGraph()
    end = timer()
    maxrssmb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    stats = backend.writeResults(plotList, outputFile, partial(  # reorder args for partial
        (lambda outF, inFN=None, smp=None, merge=None: merge(outF, inFN, sample=smp)),
        inFN=inputFiles, smp=sample, merge=mod.mergeCounters))
    logger.info(
        f"Plots finished in {end - start:.2f}s, max RSS: {maxrssmb:.2f}MB. "
        f"{stats['nHistos']:d} histograms, {stats['nSkims']:d} skims"
        + (f", {stats['nDDHistos']:d} histograms for associated selections"
           if stats["nDDHistos"] else "")
    )

    mod.plotList = plotList  # for postprocessing


def run_worker(mod):
    """ Run as a worker: process inputs and save everything to an output file """
    args = mod.args
    if (not args.output.endswith(".root")) or os.path.isdir(args.output):
        raise RuntimeError("Output for worker processes needs to be a ROOT file")
    if args.versions_file:
        import yaml
        with open(args.versions_file) as storedVersF:
            storedVersions = yaml.load(storedVersF, yaml.SafeLoader)
        versionsDict = buildVersions(mod, withRemote=False, checkPolicy="committed")
        if not compareVersions(storedVersions, versionsDict):
            raise RuntimeError("Code version differs from submitted")
    inputFiles = mod.inputs
    inputFileLists = None
    if args.maxFiles > 0 and args.maxFiles < len(inputFiles):
        logger.warning(f"Only processing first {args.maxFiles:d} of {len(inputFiles):d} files")
        inputFiles = inputFiles[:args.maxFiles]
    else:
        inputFileLists = args.filelists
    logger.info(
        f"Worker processing sample {args.sample} with module {args.module}. "
        f"Inputs: {inputFiles}, tree: {args.treeName}, output: {args.output}, "
        f"certifiedLumiFile={args.certifiedLumiFile}, runRange={args.runRange}")
    if args.anaConfig:
        sampleCfg = mod.analysisConfig["samples"][args.sample]
    else:
        sampleCfg = None
    processOne(
        mod, inputFiles, args.output, tree=args.treeName,
        certifiedLumiFile=args.certifiedLumiFile, runRange=args.runRange,
        sample=args.sample, sampleCfg=sampleCfg, inputFileLists=inputFileLists
    )


def run_notworker(mod):
    if len(mod.args.input) != 1:
        raise RuntimeError(
            "Main process (driver or non-distributed) needs exactly one argument "
            "(analysis description YAML file)")
    anaCfgName = mod.args.input[0]
    workdir = mod.args.output
    # write or check versions
    versionsDict = buildVersions(mod)
    versFile = os.path.join(workdir, "version.yml")
    if os.path.isfile(versFile):
        import yaml
        with open(versFile) as storedVersF:
            storedVersions = yaml.load(storedVersF, yaml.SafeLoader)
        compareVersions(storedVersions, versionsDict)
    # customise analysis config, get tasks
    analysisCfg = mod.analysisConfig
    tasks = mod.getTasks(
        analysisCfg, tree=analysisCfg.get("tree", "Events"),
        resolveFiles=(mod.sampleFilesResolver if not mod.args.onlypost else None))
    resultsdir = os.path.join(workdir, "results")
    if mod.args.onlypost:
        if os.path.exists(resultsdir):
            aProblem = False
            for tsk in tasks:
                fullOutName = os.path.join(resultsdir, tsk.outputFile)
                if not os.path.exists(fullOutName):
                    logger.error(f"Output file for {tsk.name} not found ({fullOutName})")
                    aProblem = True
            if aProblem:
                logger.error(f"Not all output files were found, cannot perform post-processing")
                return
        else:
            logger.error(
                f"Results directory {resultsdir} does not exist, cannot perform post-processing")
            return
    elif mod.args.distributed == "finalize":
        tasks_notfinalized = [tsk for tsk in tasks
                              if not os.path.exists(os.path.join(resultsdir, tsk.outputFile))]
        if not tasks_notfinalized:
            logger.info(
                f"All output files were found, so no finalization was redone. "
                "If you merged the outputs of partially-done MC samples "
                "please remove them from {resultsdir} and rerun to pick up the rest.")
        else:
            def cmdMatch(ln, smpNm):
                return f" --sample={smpNm} " in ln or ln.endswith(f" --sample={smpNm}")
            from .batch import getBackend
            batchBackend = getBackend(mod.envConfig["batch"]["backend"])
            batchDir = os.path.join(workdir, "batch")
            outputs, id_noOut = batchBackend.findOutputsForCommands(
                batchDir, {tsk.name: partial(cmdMatch, smpNm=tsk.name) for tsk in tasks_notfinalized})
            if id_noOut:
                logger.error(
                    "Missing outputs for subjobs {}, so no postprocessing will be run".format(
                        ", ".join(str(sjId) for sjId in id_noOut)))
                if hasattr(batchBackend, "getResubmitCommand"):
                    resubCommand = " ".join(batchBackend.getResubmitCommand(batchDir, id_noOut))
                    logger.info(f"Resubmit with '{resubCommand}' (and possibly additional options)")
                return
            aProblem = False
            for tsk in tasks_notfinalized:
                nExpected, tskOut = outputs[tsk.name]
                if not tskOut:
                    logger.error(f"No output files for sample {tsk.name}")
                    aProblem = True
                tskOut_by_name = defaultdict(list)
                for fn in tskOut:
                    tskOut_by_name[os.path.basename(fn)].append(fn)
                for outFileName, outFiles in tskOut_by_name.items():
                    if nExpected != len(outFiles):
                        logger.error(
                            f"Not all jobs for {tsk.name} produced an output file {outFileName} "
                            f"({len(outFiles):d}/{nExpected:d} found), cannot finalize")
                        aProblem = True
                    else:
                        haddCmd = ["hadd", "-f", os.path.join(resultsdir, outFileName)] + outFiles
                        import subprocess
                        try:
                            logger.debug(
                                "Merging outputs for sample {} with {}".format(
                                    tsk.name, " ".join(haddCmd)))
                            subprocess.check_call(haddCmd, stdout=subprocess.DEVNULL)
                        except subprocess.CalledProcessError:
                            logger.error("Failed to run {}".format(" ".join(haddCmd)))
                            aProblem = True
            if aProblem:
                logger.error(
                    "Could not finalize all tasks so no post-processing will be run "
                    "(rerun in verbose mode for the full list of directories and commands)")
                return
            else:
                logger.info("All tasks finalized")
    elif not tasks:
        logger.warning("No tasks defined, skipping to postprocess")
    else:  # need to run tasks
        downloadCertifiedLumiFiles(tasks, workdir=workdir)
        if os.path.exists(resultsdir):
            logger.warning(
                f"Output directory {resultsdir} exists, previous results may be overwritten")
        else:
            os.makedirs(resultsdir)
        if os.path.isfile(versFile):
            logger.warning(
                f"Overwriting {versFile}, but if not all results are overwritten "
                "the version will not be consistent")
            versionsDict["overwritten"] = True
        import yaml
        with open(versFile, "w") as versF:
            yaml.dump(versionsDict, versF)
        # store one "skeleton" tree (for more efficient "onlypost" later on
        aTask = tasks[0]
        aFileName = aTask.inputFiles[0]
        from .root import gbl
        aFile = gbl.TFile.Open(aFileName)
        if not aFile:
            logger.warning(f"Could not open file {aFileName}, no skeleton tree will be saved")
        else:
            treeName = analysisCfg.get("tree", "Events")
            aTree = aFile.Get(treeName)
            if not aTree:
                logger.warning(
                    f"Could not get {treeName} from file {aFileName}, no skeleton tree will be saved")
            else:
                outfName = os.path.join(
                    resultsdir, "__skeleton__{}.root".format(aTask.kwargs["sample"]))
                outf = gbl.TFile.Open(outfName, "RECREATE")
                if "/" in treeName:
                    outf.mkdir("/".join(treeName.split("/")[:-1])).cd()
                _ = aTree.CloneTree(1)  # copy header and a single event
                outf.Write()
                outf.Close()
                logger.debug(f"Skeleton tree written to {outfName}")
        # run all tasks
        if mod.args.distributed == "sequential":
            for task in tasks:
                output = os.path.join(resultsdir, task.outputFile)
                logger.info(
                    f"Sequential mode: processing sample {task.kwargs['sample']} "
                    + f"with module {mod.args.module}."
                    + " ({}, {}, {}".format(
                        task.inputFiles, output,
                        ", ".join(f"{k}={v}" for k, v in task.kwargs.items())
                    ))
                if "runRange" in task.kwargs:
                    task.kwargs["runRange"] = parseRunRange(task.kwargs["runRange"])
                processOne(mod, task.inputFiles, output, sampleCfg=task.config, **task.kwargs)
            if mod.args.onlyprepare:
                logger.info(f"Only doing preparation, so no results, and skipping postprocessing")
                return
        elif mod.args.distributed == "parallel":
            from .root import gbl
            if not hasattr(gbl.ROOT.RDF, "RunGraphs"):
                raise RuntimeError("Parallel running of multiple RDF graphs requires "
                                   "ROOT::RDF::RunGraphs (v6.24/00 or higher)")
            from .dataframebackend import DebugDataframeBackend, FullyCompiledBackend
            beTasks = []
            for task in tasks:
                if "runRange" in task.kwargs:
                    task.kwargs["runRange"] = parseRunRange(task.kwargs["runRange"])
                backend, plotList = mod.makeBackendAndPlotList(
                    task.inputFiles, sampleCfg=task.config, **task.kwargs)
                if isinstance(backend, DebugDataframeBackend):
                    raise RuntimeError("DebugDataframeBackend graphs cannot be in parallel")
                elif isinstance(backend, FullyCompiledBackend):
                    # for compiled, an option could be to return the 'parallelizable' part
                    # from buildGraph, such that compilation can be done in parallel / on batch
                    raise RuntimeError("FullyCompiledBackend cannot be used in parallel (yet)")
                if plotList:
                    beTasks.append((task, backend, plotList))
            if mod.args.onlyprepare:
                logger.info(f"Only doing preparation, so no results, and skipping postprocessing")
                return
            logger.info(f"Start backend graph construction for {len(tasks):d} tasks")
            for task, backend, plotList in beTasks:
                start = timer()
                backend.buildGraph(plotList)
                end = timer()
                maxrssmb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
                logger.info(f"Backend graph construction for {task.name} done "
                            f"in {end - start:.2f}s, max RSS: {maxrssmb:.2f}MB")
            logger.info("Starting to fill plots (and skims)")
            from .dataframebackend import ProductHandle, SkimTreeHandle, HistoND
            someResults = gbl.std.vector["ROOT::RDF::RResultHandle>"]()
            for _, backend, _ in beTasks:  # find at least one RResultPtr per graph
                for p in chain.from_iterable(backend.products.values()):
                    if p.product is not None and p.product is not ProductHandle.NoResult:
                        if isinstance(p, SkimTreeHandle) and p.product.result is not None:
                            someResults.push_back(p.product.result)
                            break
                        elif isinstance(p, HistoND) and not isinstance(p, gbl.TH1):
                            someResults.push_back(p.product)
                            break
            start = timer()
            gbl.ROOT.RDF.RunGraphs(someResults)
            end = timer()
            logger.info(f"Plots finished in {end - start:.2f}s, max RSS: {maxrssmb:.2f}MB.")
            for task, backend, plotList in beTasks:
                stats = backend.writeResults(
                    plotList, os.path.join(resultsdir, task.outputFile), partial(
                        (lambda outF, inFN=None, smp=None, merge=None: merge(outF, inFN, sample=smp)),
                        inFN=task.inputFiles, smp=task.name, merge=mod.mergeCounters))
                logger.info(f"{task.name}: {stats['nHistos']:d} histograms, {stats['nSkims']:d} skims"
                            + (f", {stats['nDDHistos']:d} histograms for associated selections"
                               if stats["nDDHistos"] else ""))
                mod.plotList = plotList  # for postprocessing
        elif mod.args.distributed == "driver":
            # construct the list of tasks
            from .batch import (splitInChunks, writeFileList, SplitAggregationTask,
                                HaddAction, format_runtime, getBackend)
            commArgs = ([
                "bambooRun",
                f"--module={modAbsPath(mod.args.module)}",
                "--distributed=worker",
                f"--anaConfig={utils.labspath(anaCfgName)}"] + ([
                    f"--versions-file={utils.labspath(versFile)}"]
                    if mod.gitPolicy != "testing" else [])
                + mod.specificArgv
                + (["--verbose"] if mod.args.verbose else [])
                + ([f"-t {mod.args.threads}"] if mod.args.threads else [])
            )
            beTasks = []
            for tsk in tasks:
                split = 1
                if tsk.config and "split" in tsk.config:
                    split = tsk.config["split"]
                if split >= 0:
                    # at least 1 (no splitting), at most the numer of arguments (one job per input)
                    chunks = splitInChunks(
                        tsk.inputFiles, nChunks=max(1, min(split, len(tsk.inputFiles))))
                else:  # at least 1 (one job per input), at most the number of arguments (no splitting)
                    chunks = splitInChunks(
                        tsk.inputFiles, chunkLength=max(1, min(-split, len(tsk.inputFiles))))
                cmds = []
                os.makedirs(os.path.join(workdir, "infiles"), exist_ok=True)
                for i, chunk in enumerate(chunks):
                    cfn = os.path.join(workdir, "infiles", "{}_in_{:d}.txt".format(
                        tsk.kwargs["sample"], i))
                    writeFileList(chunk, cfn)
                    cmds.append(" ".join(
                        [str(a) for a in commArgs]
                        + [f"--input={utils.labspath(cfn)}", f"--output={tsk.outputFile}"]
                        + [f"--{key}={value}" for key, value in tsk.kwargs.items()]
                    ))
                beTasks.append(SplitAggregationTask(
                    cmds, finalizeAction=HaddAction(cmds, outDir=resultsdir, options=["-f"])))
            # submit to backend
            backend = mod.envConfig["batch"]["backend"]
            batchBackend = getBackend(backend)
            defaultBatchOpts = getBatchDefaults(backend)
            # make sure we request N CPUs/job when using N threads
            if mod.args.threads:
                batchBackend.configCPUReq(defaultBatchOpts, mod.args.threads)
            clusJobs = batchBackend.jobsFromTasks(
                beTasks, workdir=os.path.join(workdir, "batch"),
                batchConfig=mod.envConfig.get(backend), configOpts=defaultBatchOpts)
            for j in clusJobs:
                j.submit()
            logger.info(
                "The status of the batch jobs will be periodically checked, "
                "and the outputs merged if necessary. "
                "If only few jobs (or the monitoring loop) fail, "
                "it may be more efficient to resubmit or rerun them manually "
                "and (if necessary) merge the outputs and produce the final results "
                "either by rerunning with --driver=finalize, or manually, "
                "using the commands that will be printed if any jobs fail, "
                "and by rerunning with the --onlypost option.")
            clusMon = batchBackend.makeTasksMonitor(
                clusJobs, beTasks, interval=int(mod.envConfig["batch"].get("update", 120)))
            collectResult = clusMon.collect()  # wait for batch jobs to finish and finalize

            if any(not tsk.failedCommands for tsk in beTasks):
                # Print time report (possibly more later)
                logger.info("Average runtime for successful tasks (to further tune job splitting):")
                for tsk in beTasks:
                    if not tsk.failedCommands:
                        totTime = sum((next(
                            clus for clus in clusJobs if cmd in clus.commandList).getRuntime(cmd)
                            for cmd in tsk.commandList), datetime.timedelta())
                        nTasks = len(tsk.commandList)
                        smpName = next(arg for arg in tsk.commandList[0].split()
                                       if arg.startswith("--sample=")).split("=")[1]
                        logger.info(
                            f" - {smpName}: {format_runtime(totTime/nTasks)} "
                            f"({nTasks:d} jobs, total: {format_runtime(totTime)})")

            if not collectResult["success"]:
                # Print missing hadd actions to be done when (if) those recovery jobs succeed
                haddCmds = list(chain.from_iterable(tsk.finalizeAction.getActions()
                                for tsk in beTasks if tsk.failedCommands and tsk.finalizeAction))
                logger.error(
                    "Finalization commands to be run are:\n{}".format(
                        "\n".join(" ".join(cmd) for cmd in haddCmds)))
                logger.error(
                    "Since there were failed jobs, I'm not doing the postprocessing step. "
                    "After performing recovery actions (see above) you may run me again "
                    "with the --distributed=finalize (to merge) "
                    "or --onlypost (if merged manually) option instead.")
                return
    try:
        mod.postProcess(tasks, config=analysisCfg, workdir=workdir, resultsdir=resultsdir)
    except Exception as ex:
        logger.exception(ex)
        logger.error(
            "Exception in postprocessing. "
            "If the worker job results (e.g. histograms) were correctly produced, "
            "you do not need to resubmit them, and may recover "
            "by running with the --onlypost option instead.")
