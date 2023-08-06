""" The :py:mod:`bamboo.analysisutils` module bundles a number of more
specific helper methods that use the tree decorators and integrate with
other components, connect to external services, or are factored out of the
classes in :py:mod:`bamboo.analysismodules` to facilitate reuse.
"""
import copy
import logging
import os.path
import subprocess
import urllib.parse
import warnings

import yaml

logger = logging.getLogger(__name__)

_SAMADhi_found = False
try:
    from cp3_llbb.SAMADhi.SAMADhi import Sample, SAMADhiDB
    _SAMADhi_found = True
except ImportError:
    pass

bamboo_cachedir = os.path.join(os.getenv(
    "XDG_CACHE_HOME", os.path.join(os.path.expanduser("~"), ".cache")), "bamboo")


def addLumiMask(sel, jsonName, runRange=None, runAndLS=None, name="goodlumis"):
    """ Refine selection with a luminosity block filter

    Typically applied directly to the root selection (for data).
    runAndLS should be a tuple of expressions with the run number and luminosity block ID.
    The run range is used to limit the part of the JSON file to consider,
    see the LumiMask helper class for details.
    """
    from . import treefunctions as op
    if runAndLS is None:
        raise RuntimeError(
            "Cannot construct a filter for the good lumi blocks without accessors "
            "(backend.create(..., runAndLS=XXX)), tree->(run, LS)")
    lumiSel = op.define(
        "LumiMask", 'const auto <<name>> = LumiMask::fromJSON("{}"{});'.format(
            jsonName, (", {:d}, {:d}".format(*runRange) if runRange is not None else "")))
    return sel.refine(name, cut=lumiSel.accept(*runAndLS))


def _dasLFNtoPFN(lfn, dasConfig):
    localPFN = os.path.join(dasConfig["storageroot"], lfn.lstrip("/"))
    if dasConfig.get("checklocalfiles", False) and "xrootdredirector" in dasConfig:
        if os.path.isfile(localPFN):
            return localPFN
        else:
            xrootdPFN = "root://{redirector}//{lfn}".format(redirector=dasConfig["xrootdredirector"], lfn=lfn)
            logger.warning(f"PFN {localPFN} not available, falling back to xrootd with {xrootdPFN}")
            return xrootdPFN
    else:
        return localPFN


def sample_resolveFiles(smpName, smpCfg, dbCache=None, envConfig=None, cfgDir="."):
    import os.path
    listfile = None
    if "files" in smpCfg and str(smpCfg["files"]) == smpCfg["files"]:
        listfile = (smpCfg["files"] if os.path.isabs(smpCfg["files"])
                    else os.path.join(cfgDir, smpCfg["files"]))
    if "db" in smpCfg and dbCache is not None:
        if listfile:  # warn if old entry and files are still there
            logger.warning(
                f"'dbcache' specified at file level and both 'db' and 'files: {listfile}' "
                "at config level. The last one will be ignored "
                "(without 'db' the list from the text file will be used)")
        if not os.path.isabs(dbCache):
            dbCache = os.path.join(cfgDir, dbCache)
        if not os.path.exists(dbCache):
            import os
            os.makedirs(dbCache)
        listfile = os.path.join(dbCache, f"{smpName}.txt")
    # read cache, if it's there
    fromFile, cacheID = [], None
    if listfile and os.path.isfile(listfile):
        with open(listfile) as smpF:
            for ln in smpF:
                if ln.startswith("#"):
                    if cacheID is None:
                        cacheID = ln.lstrip("#").strip()
                    # first commented line, ignore any others
                elif ln.strip():
                    fromFile.append(ln.strip())
        if len(fromFile) == 0:
            raise RuntimeError(f"No file names read from {listfile}")

    files = []
    if "db" in smpCfg:
        if isinstance(smpCfg["db"], str):
            newCacheID = smpCfg["db"]
            dbEntries = [smpCfg["db"]]
        else:
            newCacheID = ";;".join(smpCfg["db"])
            dbEntries = smpCfg["db"]
        if newCacheID == cacheID:
            files = fromFile
        else:  # do queries
            for dbEntry in dbEntries:  # convert to list if string
                if ":" not in dbEntry:
                    raise RuntimeError(
                        "'db' entry should be of the format 'protocol:location', "
                        "e.g. 'das:/SingleMuon/Run2016E-03Feb2017-v1/MINIAOD'")
                protocol, dbLoc = dbEntry.split(":")
                if protocol == "das":
                    dasConfig = envConfig["das"]
                    dasQuery = f"file dataset={dbLoc}"
                    logger.debug(f"Querying DAS: '{dasQuery}'")
                    try:
                        entryFiles = [
                            _dasLFNtoPFN(lfn, dasConfig)
                            for lfn in [
                                ln.strip() for ln in subprocess.check_output(
                                    ["dasgoclient", "-query", dasQuery],
                                    stderr=subprocess.STDOUT
                                ).decode().split()] if len(lfn) > 0]
                    except subprocess.CalledProcessError as ex:
                        raise RuntimeError(
                            f"Error from \"{' '.join(ex.cmd)}\": "
                            f"{ex.output.decode().strip()}") from None
                    files += entryFiles
                    if len(entryFiles) == 0:
                        raise RuntimeError(f"No files found with DAS query {dasQuery}")
                elif protocol == "samadhi":
                    if not _SAMADhi_found:
                        raise RuntimeError(
                            f"SAMADhi could not be found, cannot resolve '{dbEntry}'. "
                            "Please install the SAMADhi library "
                            "(see https://github.com/cp3-llbb/SAMADhi) "
                            "if you want to use the database to locate samples")
                    samaCred = "~/.samadhi"
                    if "SAMADhi" in envConfig and "credentials" in envConfig["SAMADhi"]:
                        samaCred = envConfig["SAMADhi"]["credentials"]
                    with SAMADhiDB(credentials=samaCred):
                        if dbLoc.isnumeric():
                            descr = f"id {dbLoc}"
                            sample = Sample.get_or_none(Sample.id == int(dbLoc))
                        else:
                            descr = f"name '{dbLoc}'"
                            sample = Sample.get_or_none(Sample.name == dbLoc)
                        if not sample:
                            raise RuntimeError(f"Could not find sample with {descr} in SAMADhi")
                        entryFiles = [f.pfn for f in sample.files]
                        if len(entryFiles) == 0:
                            raise RuntimeError(f"No files found with SAMADhi {descr}")
                    files += entryFiles
                else:
                    raise RuntimeError(f"Unsupported protocol in '{dbEntry}': {protocol}")
            if listfile:
                with open(listfile, "w") as listF:
                    listF.write(f"# {newCacheID}\n")
                    listF.write("\n".join(files))
    elif "files" not in smpCfg:
        raise RuntimeError(f"Cannot load files for {smpName}: neither 'db' nor 'files' specified")
    elif listfile:
        files = fromFile
    else:  # list in yml
        files = [(fn if os.path.isabs(fn) or urllib.parse.urlparse(fn).scheme != ""
                  else os.path.join(cfgDir, fn)) for fn in smpCfg["files"]]
    return files


class YMLIncludeLoader(yaml.SafeLoader):
    """
    Custom yaml loading to support including config files.
        Use `!include (file)` to insert content of `file` at that position.
    """

    def __init__(self, stream):
        super().__init__(stream)
        self._root = os.path.split(stream.name)[0]

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename) as f:
            return yaml.load(f, YMLIncludeLoader)


YMLIncludeLoader.add_constructor('!include', YMLIncludeLoader.include)


def parseAnalysisConfig(anaCfgName):
    with open(anaCfgName) as anaCfgF:
        analysisCfg = yaml.load(anaCfgF, YMLIncludeLoader)
    return analysisCfg


def getAFileFromAnySample(samples, resolveFiles=None, cfgDir="."):
    """ Helper method: get a file from any sample (minimizing the risk of errors)

    Tries to find any samples with:
    - a list of files
    - a cache file
    - a SAMADhi path
    - a DAS path

    If successful, a single read / query is sufficient to retrieve a file
    """
    # list of files -> return 1st
    for smpNm, smpCfg in samples.items():
        if ("files" in smpCfg) and (str(smpCfg["files"]) != smpCfg["files"]):
            return (smpNm, smpCfg,
                    (smpCfg["files"][0]
                     if (os.path.isabs(smpCfg["files"][0])
                         or urllib.parse.urlparse(smpCfg["files"][0]).scheme)
                     else os.path.join(cfgDir, smpCfg["files"][0])))
    # try to get them from a cache file or database (ordered by less-to-more risky)
    failed_names = set()
    for method, condition in [
            (" from cache file", (
                lambda smpCfg: "files" in smpCfg and isinstance(smpCfg["files"], str))),
            (" from SAMADhi", (
                lambda smpCfg: ("db" in smpCfg and (smpCfg["db"]
                                if isinstance(smpCfg["db"], str)
                                else smpCfg["db"][0]).startswith("samadhi:")))),
            (" from DAS", (
                lambda smpCfg: ("db" in smpCfg and (smpCfg["db"]
                                if isinstance(smpCfg["db"], str)
                                else smpCfg["db"][0]).startswith("das:")))),
            ("", (lambda smpCfg: True))]:
        for smpNm, smpCfg in samples.items():
            if smpNm not in failed_names and condition(smpCfg):
                try:
                    files = resolveFiles(smpNm, smpCfg)
                    return smpNm, smpCfg, files[0]
                except Exception as ex:
                    failed_names.add(smpNm)
                    logger.warning(f"Problem while resolving files for {smpNm}{method}: {ex!s}")

    raise RuntimeError(
        "Failed to resolve a file from any sample "
        "(see the warnings above for more information)")


def readEnvConfig(explName=None):
    """ Read computing environment config file (batch system, storage site etc.)

    For using a batch cluster, the [batch] section should have a 'backend' key,
    and there should be a section with the name of the backend (slurm, htcondor...),
    see bamboo.batch_<backend> for details.
    The storage site information needed to resolve the PFNs for datasets retrieved from DAS
    should be specified under the [das] section (sitename and storageroot).
    """
    import os
    from configparser import ConfigParser

    def readFromFile(name):
        cfgp = ConfigParser()
        cfgp.optionxform = str
        cfgp.read(name)
        cfg = {sName: dict(cfgp[sName]) for sName in cfgp.sections()}
        return cfg

    xdgCfg = os.getenv("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
    toTry = ["bamboo.ini", "bamboorc", os.path.join(xdgCfg, "bamboorc")]
    if explName:
        toTry.insert(0, explName)
    for iniName in toTry:
        if os.path.exists(iniName) and os.path.isfile(iniName):
            try:
                res = readFromFile(iniName)
                logger.info(f"Read config from file {iniName}")
                return res
            except Exception as ex:
                logger.warning(f"Problem reading config file {iniName}: {ex}")
    logger.error(
        "No valid environment config file found, please copy one from the .ini files "
        "from the examples directory to ~/.config/bamboorc, or pass the --envConfig option")


_yieldsTexPreface = "\n".join(
    f"% {ln}" for ln in r"""Yields table generated automatically by bamboo (same as plotIt).
Needed packages:
   \usepackage{booktabs}

Use the following if building a CMS document

\makeatletter
\newcommand{\thickhline}{%
    \noalign {\ifnum 0=`}\fi \hrule height .08em
    \futurelet \reserved@a \@xhline
}
\newcommand{\thinhline}{%
    \noalign {\ifnum 0=`}\fi \hrule height .05em
    \futurelet \reserved@a \@xhline
}
\makeatother
\newcommand{\toprule}{\noalign{\vskip0pt}\thickhline\noalign{\vskip.65ex}}
\newcommand{\midrule}{\noalign{\vskip.4ex}\thinhline\noalign{\vskip.65ex}}
\newcommand{\bottomrule}{\noalign{\vskip.4ex}\thickhline\noalign{\vskip0pt}}
""".split("\n"))


def _texProcName(procName):
    if "$" in procName:
        procName = procName.replace("_", "\\_")
    if "#" in procName:  # assume ROOT LaTeX
        procName = "${}$".format(procName.replace("#", "\\"))
    return procName


def _makeYieldsTexTable(
        report, samples, entryPlots, stretch=1.5, orientation="v", align="c",
        yieldPrecision=1, ratioPrecision=2):
    if orientation not in ("v", "h"):
        raise RuntimeError(f"Unsupported table orientation: {orientation} (valid: 'h' and 'v')")
    import plotit.plotit
    from plotit.plotit import Stack
    import numpy as np
    from itertools import repeat

    def getHist(smp, plot):
        try:
            h = smp.getHist(plot)
            h.contents  # check
            return h
        except KeyError:
            return None

    def colEntriesFromCFREntryHists(report, entryHists, precision=1, showUncert=True):
        stacks_t = []
        colEntries = []
        for entries in report.titles.values():
            s_entries = []
            for eName in entries:
                eh = entryHists[eName]
                if eh is not None:
                    if (not isinstance(eh, Stack)) or eh.entries:
                        s_entries.append(eh)
            st_t = Stack(entries=s_entries)
            if s_entries:
                uncert = (fr" \pm {{:.{precision}f}}".format(np.sqrt(st_t.sumw2 + st_t.syst2)[1])
                          if showUncert else "")
                colEntries.append(f"${{0:.{precision:d}f}}{{1}}$".format(st_t.contents[1], uncert))
                stacks_t.append(st_t)
            else:
                colEntries.append("---")
                stacks_t.append(None)
        return stacks_t, colEntries

    smp_signal = [smp for smp in samples if smp.cfg.type == "SIGNAL"]
    smp_mc = [smp for smp in samples if smp.cfg.type == "MC"]
    smp_data = [smp for smp in samples if smp.cfg.type == "DATA"]
    sepStr = "|l|"
    smpHdrs = []
    titles = list(report.titles.keys())
    entries_smp = []
    stTotMC, stTotData = None, None
    if smp_signal:
        sepStr += "|"
        for sigSmp in smp_signal:
            _, colEntries = colEntriesFromCFREntryHists(
                report, {eName: getHist(sigSmp, p) for eName, p in entryPlots.items()},
                precision=yieldPrecision)
            sepStr += f"{align}|"
            smpHdrs.append(f"{_texProcName(sigSmp.cfg.yields_group)} {sigSmp.cfg.cross_section:f}pb")
            entries_smp.append(colEntries)
    if smp_mc:
        sepStr += "|"
        for mcSmp in smp_mc:
            stTotMC, colEntries = colEntriesFromCFREntryHists(
                report, {eName: getHist(mcSmp, p) for eName, p in entryPlots.items()},
                precision=yieldPrecision)
            sepStr += f"{align}|"
            if isinstance(mcSmp, plotit.plotit.Group):
                smpHdrs.append(_texProcName(mcSmp.name))
            else:
                smpHdrs.append(_texProcName(mcSmp.cfg.yields_group))
            entries_smp.append(colEntries)
        if len(smp_mc) > 1:
            sepStr += f"|{align}|"
            smpHdrs.append("Tot. MC")
            stTotMC, colEntries = colEntriesFromCFREntryHists(
                report,
                {eName: Stack(entries=[h for h in (getHist(smp, p) for smp in smp_mc) if h])
                 for eName, p in entryPlots.items()},
                precision=yieldPrecision)
            entries_smp.append(colEntries)
    if smp_data:
        sepStr += f"|{align}|"
        smpHdrs.append("Data")
        stTotData, colEntries = colEntriesFromCFREntryHists(
            report,
            {eName: Stack(entries=[h for h in (getHist(smp, p) for smp in smp_data) if h])
             for eName, p in entryPlots.items()},
            precision=0, showUncert=False)
        entries_smp.append(colEntries)
    if smp_data and smp_mc:
        sepStr += f"|{align}|"
        smpHdrs.append("Data/MC")
        colEntries = []
        import numpy.ma as ma
        for stData, stMC in zip(stTotData, stTotMC):
            if stData is not None and stMC is not None:
                dtCont = stData.contents
                mcCont = ma.array(stMC.contents)
                ratio = dtCont / mcCont
                ratioErr = (
                    np.sqrt(mcCont**2 * stData.sumw2 + dtCont**2 * (stMC.sumw2 + stMC.syst2))
                    / mcCont**2)
                if mcCont[1] != 0.:
                    colEntries.append(r"${{0:.{0}f}} \pm {{1:.{0}f}}$".format(
                        ratioPrecision).format(ratio[1], ratioErr[1]))
                else:
                    colEntries.append("---")
            else:
                colEntries.append("---")
        entries_smp.append(colEntries)
    c_bySmp = entries_smp
    c_byHdr = [[smpEntries[i] for smpEntries in entries_smp] for i in range(len(titles))]
    if orientation == "v":
        rowHdrs = titles  # selections
        colHdrs = ["Cat."] + smpHdrs  # samples
        c_byRow = c_byHdr
        c_byCol = c_bySmp
    else:  # horizontal
        sepStr = "|l|{}|".format("|".join(repeat(align, len(titles))))
        rowHdrs = smpHdrs  # samples
        colHdrs = ["Cat."] + titles  # selections
        c_byRow = c_bySmp
        c_byCol = c_byHdr
    if entries_smp:
        colWidths = ([max(len(rh) for rh in rowHdrs) + 1]
                     + [max(len(hdr), max(len(c) for c in col)) + 1
                        for hdr, col in zip(colHdrs[1:], c_byCol)])
        return "\n".join([
            f"\\renewcommand{{\\arraystretch}}{{{stretch}}}",
            f"\\begin{{tabular}}{{ {sepStr} }}",
            "    \\hline",
            "    {} \\\\".format(" & ".join(h.ljust(cw) for cw, h in zip(colWidths, colHdrs))),
            "    \\hline"] + [
                "    {} \\\\".format(" & ".join(en.rjust(cw) for cw, en in zip(colWidths, [rh] + rowEntries)))
                for rh, rowEntries in zip(rowHdrs, c_byRow)
        ] + [
            "    \\hline",
            "\\end{tabular}"
        ])


def printCutFlowReports(
        config, reportList, workdir=".", resultsdir=".", suffix=None,
        readCounters=lambda f: -1., eras=("all", None), verbose=False):
    """
    Print yields to the log file, and write a LaTeX yields table for each

    Samples can be grouped (only for the LaTeX table) by specifying the
    ``yields-group`` key (overriding the regular ``groups`` used for plots).
    The sample (or group) name to use in this table should be specified
    through the ``yields-title`` sample key.

    In addition, the following options in the ``plotIt`` section of
    the YAML configuration file influence the layout of the LaTeX yields table:

    - ``yields-table-stretch``: ``\\arraystretch`` value, 1.15 by default
    - ``yields-table-align``: orientation, ``h`` (default), samples in rows,
        or ``v``, samples in columns
    - ``yields-table-text-align``: alignment of text in table cells (default: ``c``)
    - ``yields-table-numerical-precision-yields``: number of digits after
        the decimal point for yields (default: 1)
    - ``yields-table-numerical-precision-ratio``: number of digits after
        the decimal point for ratios (default: 2)
    """
    eraMode, eras = eras
    if not eras:  # from config if not specified
        eras = list(config["eras"].keys())

    # helper: print one bamboo.plots.CutFlowReport.Entry
    def printEntry(entry, printFun=logger.info, recursive=True, genEvents=None):
        if entry.nominal is not None:
            effMsg = ""
            if entry.parent:
                sumPass = entry.nominal.GetBinContent(1)
                sumTotal = (entry.parent.nominal.GetBinContent(1)
                            if entry.parent.nominal is not None else 0.)
                if sumTotal != 0.:
                    effMsg = f", Eff={sumPass/sumTotal:.2%}"
                    if genEvents:
                        effMsg += f", TotalEff={sumPass/genEvents:.2%}"
            printFun(
                f"Selection {entry.name}: N={entry.nominal.GetEntries()}, "
                f"SumW={entry.nominal.GetBinContent(1)}{effMsg}")
        if recursive:
            for c in entry.children:
                printEntry(c, printFun=printFun, recursive=recursive, genEvents=genEvents)

    # retrieve results files, get generated events for each sample
    from .root import gbl
    resultsFiles = dict()
    generated_events = dict()
    for smp, smpCfg in config["samples"].items():
        if "era" not in smpCfg or smpCfg["era"] in eras:
            resF = gbl.TFile.Open(os.path.join(resultsdir, f"{smp}.root"))
            resultsFiles[smp] = resF
            genEvts = None
            if "generated-events" in smpCfg:
                if isinstance(smpCfg["generated-events"], str):
                    genEvts = readCounters(resF)[smpCfg["generated-events"]]
                else:
                    genEvts = smpCfg["generated-events"]
            generated_events[smp] = genEvts
    has_plotit = None
    try:
        import plotit.plotit  # noqa: F401
        has_plotit = True
    except ImportError:
        has_plotit = False
    from bamboo.plots import EquidistantBinning as EqB

    class YieldPlot:
        def __init__(self, name):
            self.name = name
            self.plotopts = dict()
            self.axisTitles = ("Yield",)
            self.binnings = [EqB(1, 0., 1.)]

    for report in reportList:
        smpReports = {smp: report.readFromResults(resF) for smp, resF in resultsFiles.items()}
        # debug print
        for smp, smpRep in smpReports.items():
            if smpRep.printInLog:
                logger.info(f"Cutflow report {report.name} for sample {smp}")
                for root in smpRep.rootEntries():
                    printEntry(root, genEvents=generated_events[smp])
        # save yields.tex (if needed)
        if any(len(cb) > 1 or tt != cb[0] for tt, cb in report.titles.items()):
            if not has_plotit:
                logger.error(f"Could not load plotit python library, no TeX yields tables for {report.name}")
            else:
                yield_plots = [YieldPlot(f"{report.name}_{eName}")
                               for tEntries in report.titles.values()
                               for eName in tEntries]
                out_eras = []
                if len(eras) > 1 and eraMode in ("all", "combined"):
                    nParts = [report.name]
                    if suffix:
                        nParts.append(suffix)
                    out_eras.append(("{}.tex".format("_".join(nParts)), eras))
                if len(eras) == 1 or eraMode in ("split", "all"):
                    for era in eras:
                        nParts = [report.name]
                        if suffix:
                            nParts.append(suffix)
                        nParts.append(era)
                        out_eras.append(("{}.tex".format("_".join(nParts)), [era]))
                for outName, iEras in out_eras:
                    pConfig, samples, plots, _, _ = loadPlotIt(
                        config, yield_plots, eras=iEras,
                        workdir=workdir, resultsdir=resultsdir, readCounters=readCounters)
                    tabBlock = _makeYieldsTexTable(
                        report, samples,
                        {p.name[len(report.name) + 1:]: p for p in plots},
                        stretch=pConfig.yields_table_stretch,
                        orientation=pConfig.yields_table_align,
                        align=pConfig.yields_table_text_align,
                        yieldPrecision=pConfig.yields_table_numerical_precision_yields,
                        ratioPrecision=pConfig.yields_table_numerical_precision_ratio)
                    if tabBlock:
                        with open(os.path.join(workdir, outName), "w") as ytf:
                            ytf.write("\n".join((_yieldsTexPreface, tabBlock)))
                        logger.info(
                            "Yields table for era(s) {} was written to {}".format(
                                ",".join(iEras), os.path.join(workdir, outName)))
                    else:
                        logger.warning(f"No samples for era(s) {','.join(iEras)}, so no yields.tex")


def plotIt_files(samplesDict, resultsdir=".", eras=None, readCounters=lambda f: -1., vetoAttributes=None):
    files = dict()
    for smpName, smpCfg in samplesDict.items():
        if smpCfg.get("era") in eras:
            resultsName = f"{smpName}.root"
            smpOpts = (dict(smpCfg) if vetoAttributes is None
                       else {k: v for k, v in smpCfg.items() if k not in vetoAttributes})
            isMC = (smpCfg.get("group") != "data")
            if "type" not in smpOpts:
                smpOpts["type"] = ("mc" if isMC else "data")
            if isMC:
                if "cross-section" not in smpCfg:
                    logger.warning(f"Sample {smpName} is of type MC, but no cross-section specified")
                smpOpts["cross-section"] = smpCfg.get("cross-section", 1.)
                from .root import gbl
                resultsFile = gbl.TFile.Open(os.path.join(resultsdir, resultsName))
                if "generated-events" not in smpCfg:
                    logger.error(
                        f"No key 'generated-events' found for MC sample {smpName}, "
                        "normalization will be wrong")
                elif isinstance(smpCfg["generated-events"], str):
                    counters = readCounters(resultsFile)
                    if smpCfg["generated-events"] not in counters:
                        raise RuntimeError(
                            f"Counter with name \"{smpCfg['generated-events']}\" not found "
                            f"for sample {smpName}")
                    smpOpts["generated-events"] = counters[smpCfg["generated-events"]]
                else:
                    smpOpts["generated-events"] = smpCfg["generated-events"]
            files[resultsName] = smpOpts
    return files


plotit_plotdefaults = {
    "x-axis": lambda p: f"{p.axisTitles[0]}",
    "x-axis-range": lambda p: [p.binnings[0].minimum, p.binnings[0].maximum]
}


def plotIt_plots(plotList, plotDefaults=None):
    plotit_plots = dict()
    for plot in plotList:
        plotOpts = dict(plotit_plotdefaults)
        if plotDefaults is not None:
            plotOpts.update(plotDefaults)
        plotOpts.update(plot.plotopts)
        plotOpts = {k: (v(plot) if callable(v) else v) for k, v in plotOpts.items()}
        plotit_plots[plot.name] = plotOpts
    return plotit_plots


def plotIt_config(config, root=".", eras=None):
    plotitCfg = copy.deepcopy(config.get("plotIt", {"configuration": {}}))
    plotitCfg["configuration"].update({
        "root": root,
        "eras": eras,
        "luminosity": {era: config["eras"][era]["luminosity"] for era in eras}
    })
    return plotitCfg


def savePlotItConfig(cfgName, plotitCfg, filesCfg, plotsCfg):
    fullCfg = copy.deepcopy(plotitCfg)
    fullCfg["files"] = filesCfg
    fullCfg["plots"] = plotsCfg
    with open(cfgName, "w") as plotitFile:
        yaml.dump(fullCfg, plotitFile)


def _plotIt_configFilesAndPlots(
        config, plotList, eras=None, workdir=".", resultsdir=".",
        readCounters=lambda f: -1., vetoFileAttributes=None, plotDefaults=None):
    # helper method, to avoid overlap between writePlotIt and loadPlotIt
    # base: copy from plotIt block, add root and translate eras/lumi
    plotitCfg = plotIt_config(config, root=os.path.relpath(resultsdir, workdir), eras=eras)
    # samples -> files: read sum of weights from results
    filesCfg = plotIt_files(
        config["samples"], resultsdir=resultsdir, eras=eras,
        readCounters=readCounters, vetoAttributes=vetoFileAttributes)
    # plots: add default style options
    plotDefaults_cmb = plotitCfg.get("plotdefaults", {})
    if plotDefaults:
        plotDefaults_cmb.update(plotDefaults)
    plotsCfg = plotIt_plots(plotList, plotDefaults=plotDefaults_cmb)
    return plotitCfg, filesCfg, plotsCfg


def writePlotIt(
        config, plotList, outName, eras=None, workdir=".", resultsdir=".",
        readCounters=lambda f: -1., vetoFileAttributes=None, plotDefaults=None):
    """
    Combine creation and saving of a plotIt config file

    for convenience inside a :py:class:`~bamboo.analysismodules.HistogramsModule`,
    the individual parts are also available in :py:mod:`bamboo.analysisutils`.

    :param config: parsed analysis configuration. Only the ``configuration`` (if present)
        and ``eras`` sections (to get the luminosities) are read.
    :param plotList: list of plots to convert
        (``name`` and ``plotopts``, combined with the default style)
    :param outName: output YAML config file name
    :param eras: valid era list
    :param workdir: output directory
    :param resultsdir: directory with output ROOT files with histograms
    :param readCounters: method to read the sum of event weights from an output file
    :param vetoFileAttributes: list of per-sample keys that should be ignored
        (those specific to the bamboo part, e.g. job splitting and DAS paths)
    :param plotDefaults: plot defaults to add (added to those from
        ``config["plotIt"]["plotdefaults"]``, with higher precedence if present in both)
    """
    if eras is None:
        eras = list(config["eras"].keys())
    plotitCfg, filesCfg, plotsCfg = _plotIt_configFilesAndPlots(
        config, plotList, eras=eras, workdir=workdir, resultsdir=resultsdir,
        readCounters=readCounters, vetoFileAttributes=vetoFileAttributes, plotDefaults=plotDefaults)
    # write
    savePlotItConfig(outName, plotitCfg, filesCfg, plotsCfg)


def loadPlotIt(
        config, plotList, eras=None, workdir=".", resultsdir=".",
        readCounters=lambda f: -1., vetoFileAttributes=None, plotDefaults=None):
    """
    Load the plotit configuration with the plotIt python library

    The plotIt YAML file writing and parsing is skipped in this case
    (to write the file, the :py:func:`~bamboo.analysisutils.writePlotIt` method
    should be used, with the same arguments).

    :param config: parsed analysis configuration. Only the ``configuration``
        (if present) and ``eras`` sections (to get the luminosities) are read.
    :param plotList: list of plots to convert
        (``name`` and ``plotopts``, combined with the default style)
    :param eras: list of eras to consider
        (``None`` for all that are in the config)
    :param workdir: output directory
    :param resultsdir: directory with output ROOT files with histograms
    :param readCounters: method to read the sum of event weights from an output file
    :param vetoFileAttributes: list of per-sample keys that should be ignored
        (those specific to the bamboo part, e.g. job splitting and DAS paths)
    :param plotDefaults: plot defaults to add (added to those from
        ``config["plotIt"]["plotdefaults"]``, with higher precedence if present in both)
    """
    if eras is None:
        eras = list(config["eras"].keys())
    try:
        from plotit.config import (loadConfiguration, loadFiles, loadGroups,
                                   loadPlots, loadSystematics, loadLegend)
        from plotit.plotit import resolveFiles, samplesFromFilesAndGroups
    except ImportError as ex:
        raise RuntimeError(f"Could not load plotit python library ({ex!r})")
    # generate dictionaries
    plotitCfg, filesCfg, plotsCfg = _plotIt_configFilesAndPlots(
        config, plotList, eras=eras, workdir=workdir, resultsdir=resultsdir,
        readCounters=readCounters, vetoFileAttributes=vetoFileAttributes, plotDefaults=plotDefaults)
    # parse in (py)plotit format
    configuration = loadConfiguration(plotitCfg["configuration"])
    cFiles = loadFiles(filesCfg)
    cGroups = loadGroups(plotitCfg.get("groups"), files=cFiles)
    plots = loadPlots(plotsCfg)
    systematics = loadSystematics(plotitCfg.get("systematics"), configuration=configuration)
    legend = loadLegend(plotitCfg.get("legend"))
    # resolve, select, group, and sort the files -> samples
    files = resolveFiles(cFiles, configuration, systematics=systematics, histodir=workdir)
    samples = samplesFromFilesAndGroups(files, cGroups, eras=eras)
    return configuration, samples, plots, systematics, legend


def runPlotIt(cfgName, workdir=".", plotsdir="plots", plotIt="plotIt", eras=("all", None), verbose=False):
    """
    Run plotIt

    :param cfgName: plotIt YAML config file name
    :param workdir: working directory
        (also the starting point for finding the histograms files, ``--i`` option)
    :param plotsdir: name of the plots directory inside workdir
        (``plots``, by default)
    :param plotIt: path of the ``plotIt`` executable
    :param eras: ``(mode, eras)``, mode being one of ``"split"``, ``"combined"``, or ``"all"``
        (both of the former), and eras a list of era names, or ``None`` for all
    :param verbose: print the plotIt command being run
    """
    eraMode, eras = eras
    out_extraOpts = []
    if len(eras) > 1 and eraMode in ("all", "combined"):
        out_extraOpts.append((os.path.join(workdir, plotsdir), []))
    if len(eras) == 1 or eraMode in ("split", "all"):
        for era in eras:
            out_extraOpts.append((os.path.join(workdir, f"{plotsdir}_{era}"), ["-e", era]))
    for plotsdir, extraOpts in out_extraOpts:
        if os.path.exists(plotsdir):
            logger.warning(f"Directory '{plotsdir}' already exists, previous plots will be overwritten")
        else:
            os.makedirs(plotsdir)
        try:
            plotItLog = os.path.join(plotsdir, "out.log")
            plotItArgs = [plotIt, "-i", workdir, "-o", plotsdir, "-y"] + extraOpts + [cfgName]
            if verbose:
                logger.debug("Running command `{}`, with logfile {}".format(" ".join(plotItArgs), plotItLog))
            with open(plotItLog, "w") as logFile:
                subprocess.check_call(plotItArgs, stdout=logFile)
            logger.info(f"plotIt output is available in {plotsdir}")
        except subprocess.CalledProcessError as ex:
            logger.error(
                "Command '{}' failed with exit code {}\n{}".format(
                    " ".join(ex.cmd), ex.returncode, ex.output))


def _getJESUncertaintySources(
        sources, jecDBCache, jec, jetType, regroupTag="",
        uncertaintiesFallbackJetType=None, session=None):
    if sources == "Merged":
        try:
            plf = jecDBCache.getPayload(
                jec, "UncertaintySources", jetType,
                prefix=f"Regrouped{regroupTag}_", session=session)
        except ValueError as ex:
            if uncertaintiesFallbackJetType is not None:
                plf = jecDBCache.getPayload(
                    jec, "UncertaintySources", uncertaintiesFallbackJetType,
                    prefix=f"Regrouped{regroupTag}_", session=session)
                logger.info(f"{ex!s}, falling back to {uncertaintiesFallbackJetType} uncertainties ({plf})")
            else:
                raise ex
    else:
        plf = jecDBCache.getPayload(jec, "UncertaintySources", jetType, session=session)
    if sources in ("All", "Merged"):
        readSources = []
        with open(plf) as jesUncF:
            for ln in jesUncF:
                ln = ln.strip()
                if ln.startswith("[") and ln.endswith("]"):
                    readSources.append(ln[1:-1])
        logger.debug(f"Found {len(readSources):d} JES uncertainty sources in {plf}: {', '.join(readSources)}")
        sources = readSources
    return plf, sources


def _enableCalcSystematics(variProxy, enableSystematics=None, default=True, name=""):
    if enableSystematics is None:
        if default:
            def enableSystematics(x):
                return True
        else:
            def enableSystematics(x):
                return False
    elif (not callable(enableSystematics)) and hasattr(enableSystematics, "__contains__"):
        enableSystematics = enableSystematics.__contains__
    all_enabled = set()
    all_avail = set()
    for attN, opWithSyst in variProxy.brMapMap[variProxy.withSystName].items():
        enable = []
        for vari in variProxy._available(attN):
            if vari != "nominal":
                all_avail.add(vari)
                vari_c = vari
                if vari.endswith("up"):
                    vari_c = vari[:-2]
                elif vari.endswith("down"):
                    vari_c = vari[:-4]
                if enableSystematics(vari) or enableSystematics(vari_c):
                    enable.append(vari)
        if enable or opWithSyst.variations:
            opWithSyst.variations = tuple(enable)  # fine, just (re)created by _initFromCalc
            all_enabled.update(enable)
    if all_enabled:
        logger.debug("Enabled systematic variations for {}: {}".format(
            name, " ".join(all_enabled)))
    if len(all_enabled) != len(all_avail):
        logger.debug("Disabled systematic variations for {}: {}".format(
            name, " ".join(all_avail.difference(all_enabled))))


# jet mass scale
# W-tagging PUPPI softdrop JMS values: https://twiki.cern.ch/twiki/bin/view/CMS/JetWtagging
# 2016 values
fatjet_jmsValues = {
    "2016": [1.00, 1.0094, 0.9906],  # nominal, up, down
    "2017": [0.982, 0.986, 0.978],
    # Use 2017 values for 2018 until 2018 are released
    "2018": [0.982, 0.986, 0.978],
}
# jet mass resolution: https://twiki.cern.ch/twiki/bin/view/CMS/JetWtagging
fatjet_jmrValues = {  # nominal, up, down
    "2016": [1.0, 1.2, 0.8],
    "2017": [1.09, 1.14, 1.04],
    # Use 2017 values for 2018 until 2018 are released
    "2018": [1.09, 1.14, 1.04],
}
# JMS&JMR SD corr in tau21DDT region: https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetWtagging#tau21DDT_0_43
fatjet_gmsValues_tau21DDT = {
    "2016": [1.014, 1.021, 1.007],
    "2017": [0.983, 0.99, 0.976],
    "2018": [1.000, 1.010, 0.990]  # tau21DDT < 0.43 WP
}
fatjet_gmrValues_tau21DDT = {
    "2016": [1.086, 1.176, 0.996],
    "2017": [1.080, 1.161, 0.999],
    "2018": [1.124, 1.208, 1.040]
}
# PUPPI scale and resolutions
fatjet_puppi_msd_params = {
    "gen": "1.0062610283313527+(-1.061605139842829*((x*0.07999000770091785)^-1.2045376937033758))",
    "reco_cen": (1.0930197734452352, -0.00015006788774298745, 3.4486611503791434e-07,
                 -2.681003093847412e-10, 8.674402290776817e-14, -1.0011358570698617e-17),
    "reco_fwd": (1.2721151537214315, -0.0005716403627542301, 8.372894123074334e-07,
                 -5.204332049858346e-10, 1.4537520981877012e-13, -1.5038869243803616e-17),
    "resol_cen": (1.092735080341856, 4.142622682579229e-05, -1.3736805733597026e-07,
                  1.2295818250625584e-10, -4.197075395161288e-14, 4.923792745086088e-18),
    "resol_fwd": (1.1649278339374347, -0.00012678902807057208, 1.0594037344842974e-07,
                  6.072087019460118e-12, -1.992427482862693e-14, 3.644006510237158e-18)
}


def configureJets(
        variProxy, jetType, jec=None, jecLevels="default", smear=None,
        useGenMatch=True, genMatchDR=0.2, genMatchDPt=3.,
        jesUncertaintySources=None, regroupTag="", uncertaintiesFallbackJetType=None,
        splitJER=False, addHEM2018Issue=False, enableSystematics=None,
        subjets=None, mcYearForFatJets=None, isTau21DDT=False, jms=None, jmr=None, gms=None, gmr=None,
        cachedir=None, mayWriteCache=False, isMC=False, backend=None, uName=""):
    """ Reapply JEC, set up jet smearing, or prepare JER/JES uncertainties collections

    :param variProxy: jet variations proxy, e.g. ``tree._Jet``
    :param jetType: jet type, e.g. AK4PFchs
    :param smear: tag of resolution (and scalefactors) to use for smearing
        (no smearing is done if unspecified)
    :param jec: tag of the new JEC to apply, or for the JES uncertainties
        (pass an empty list to jecLevels to produce only the latter without reapplying the JEC)
    :param jecLevels: list of JEC levels to apply (if left out the recommendations are used:
        L1FastJet, L2Relative, L3Absolute, and also L2L3Residual for data)
    :param jesUncertaintySources: list of jet energy scale uncertainty sources (see the
        `JECUncertaintySources twiki <https://twiki.cern.ch/twiki/bin/viewauth/CMS/JECUncertaintySources>`_),
        ``"All"``, or ``"Merged"``, for all regrouped uncertainties
        (in which case ``regroupTag`` can be specified)
    :param regroupTag: version of the regrouped uncertainties to use
    :param uncertaintiesFallbackJetType: jet type from which to use the (regrouped) JES uncertainties
        if those for jetType are not found (e.g. AK4PFchs, see
        `JME HN <https://hypernews.cern.ch/HyperNews/CMS/get/jes/988/1.html>`_)
    :param enableSystematics: filter systematics variations to enable
        (collection of names or callable that takes the variation name;
        default: all that are available for MC, none for data)

    :param useGenMatch: use matching to generator-level jets for resolution smearing
    :param genMatchDR: DeltaR for generator-level jet matching
        (half the cone size is recommended, default is 0.2)
    :param genMatchDPt: maximal relative PT difference
        (in units of the resolution) between reco and gen jet
    :param splitJER: vary the JER uncertainty independently in six kinematic bins (see the
        `JER uncertainty twiki
        <https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution#Run2_JER_uncertainty_correlation>`_)
    :param addHEM2018Issue: add a JES uncertainty for the HEM issue in 2018 (see
        `this hypernews post <https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/2000.html>`_)
    :param subjets: subjets proxy (``tree.SubJet``)
    :param mcYearForFatJets: data-taking year for fat jet parameters
        ((softdrop) mass scale and resolution, these should not be passed for data).
        They can also be passed explicitly, see the following parameters.
        If none are passed, no jet mass scale corrections are applied.
    :param isTau21DDT: if used in combinaton with mcYearForFatJets,
        will use different values for the softdrop mass.
        Warning: differently from nanoAOD-Tools, these will be propagated to the JEC uncertainties,
        and this combination of settings has not been validated.
        Please check carefully if you need to use this.
    :param jms: jet mass scale correction (nominal, up, down), for fat jets
    :param jmr: jet mass resolution (nominal, up, down), for fat jets
    :param gms: jet groomed mass scale correction (nominal, up, down), for fat jets,
        same as ``jms`` by default
    :param gmr: jet groomed mass resolution (nominal, up, down), for fat jets,
        same as ``jmr`` by default
    :param cachedir: alternative root directory to use for the txt files cache,
        instead of ``$XDG_CACHE_HOME/bamboo`` (usually ``~/.cache/bamboo``)
    :param mayWriteCache: flag to indicate if this task is allowed to write to the cache status file
        (set to False for worker tasks to avoid corruption due to concurrent writes)

    :param isMC: MC or not
    :param backend: backend pointer
        (returned from :py:meth:`~bamboo.analysismodules.HistogramsModule.prepareTree`)
    :param uName: [deprecated, ignored]
        unique name for the correction calculator (sample name is a safe choice)
    """
    if uName != "":
        warnings.warn("Passing uName to configureJets"
                      "is not necessary anymore (and ignored), please update",
                      DeprecationWarning)
    from . import treefunctions as op  # first to load default headers/libs, if still needed
    from .treefunctions import _to, _tp  # treeoperations and treeproxies
    from itertools import repeat
    isFat = jetType.startswith("AK8")
    aJet = variProxy.orig[0]
    if isFat and subjets is None:
        evt = variProxy._parent
        subjets = evt.SubJet
    args = [getattr(aJet, comp).op.arg for comp in ("pt", "eta", "phi", "mass", "rawFactor", "area")]
    if isFat:
        args.append(aJet.msoftdrop.op.arg)
        args += [getattr(aJet, f"subJet{iSJ:d}").idx.op.arg for iSJ in range(1, 3)]
        args += [getattr(subjets[0], comp).op.arg for comp in ("pt", "eta", "phi", "mass")]
    args.append(aJet.jetId.op.arg)
    args.append(_to.GetColumn("Float_t", "fixedGridRhoFastjetAll"))
    if isMC:
        evt = variProxy._parent
        args.append((evt.run << 20) + (evt.luminosityBlock << 10) + evt.event + 1 + op.static_cast("unsigned",
                    op.switch(op.rng_len(variProxy.orig) != 0, variProxy.orig[0].eta / .01, op.c_float(0.))))
        aGJet = evt.GenJet[0]
        if isFat:
            aGJet = evt.GenJetAK8[0]
        args += [getattr(aGJet, comp).op.arg for comp in ("pt", "eta", "phi", "mass")]
        if isFat:
            aGSJet = evt.SubGenJetAK8[0]
            args += [getattr(aGSJet, comp).op.arg for comp in ("pt", "eta", "phi", "mass")]
    else:
        args.append(_tp.makeConst(0, "unsigned"))  # no seed
        args += list(repeat(_to.ExtVar(
            "ROOT::VecOps::RVec<float>", "ROOT::VecOps::RVec<float>{}"),
            (8 if isFat else 4)))
    # fill configuration
    from CMSJMECalculators import config as calcConfigs
    config = (calcConfigs.JetVariations() if not isFat else calcConfigs.FatJetVariations())
    if smear is not None or jec is not None:
        from CMSJMECalculators.jetdatabasecache import JetDatabaseCache, sessionWithResponseChecks
        with sessionWithResponseChecks() as session:
            if smear is not None:
                jrDBCache = JetDatabaseCache(
                    "JRDatabase", repository="cms-jet/JRDatabase",
                    cachedir=cachedir, mayWrite=mayWriteCache, session=session)
                config.ptResolution = jrDBCache.getPayload(smear, "PtResolution", jetType,
                                                           session=session)
                config.ptResolutionSF = jrDBCache.getPayload(smear, "SF", jetType, session=session)
                config.splitJER = splitJER
                config.useGenMatch = useGenMatch
                config.genMatchDR = genMatchDR
                config.genMatchDPt = genMatchDPt
                if isFat:
                    if jmr is not None or mcYearForFatJets is not None:
                        if jmr is None:
                            jmr = fatjet_jmrValues[mcYearForFatJets]
                        config.jmr = jmr
                        if gmr is None:
                            if isTau21DDT:
                                gmr = fatjet_gmrValues_tau21DDT[mcYearForFatJets]
                            else:
                                gmr = jmr
                        config.gmr = gmr
                    elif gmr is not None:  # groomed only, explicitly passed
                        config.gmr = gmr
            if jec is not None:
                if jecLevels == "default":
                    # "L3Absolute" left out because it is dummy according to
                    # https://twiki.cern.ch/twiki/bin/view/CMS/IntroToJEC#Mandatory_Jet_Energy_Corrections
                    if jec.endswith("_DATA"):
                        jecLevels = ["L1FastJet", "L2Relative", "L2L3Residual"]
                    elif jec.endswith("_MC"):
                        # "L2L3Residual" could be added, but it is dummy for MC according to
                        # https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetCorApplication  # noqa: B950
                        jecLevels = ["L1FastJet", "L2Relative"]
                    else:
                        raise ValueError(
                            f"JEC tag {jec} does not end with '_DATA' or '_MC', "
                            "so the levels cannot be guessed. "
                            "Please specify the JEC levels explicitly")
                jecDBCache = JetDatabaseCache(
                    "JECDatabase", repository="cms-jet/JECDatabase",
                    cachedir=cachedir, mayWrite=mayWriteCache, session=session)
                if jecLevels:
                    config.jec = [
                        jecDBCache.getPayload(jec, jLev, jetType, session=session)
                        for jLev in jecLevels]
                config.addHEM2018Issue = addHEM2018Issue
                if jesUncertaintySources:
                    plf, jesUncertaintySources = _getJESUncertaintySources(
                        jesUncertaintySources, jecDBCache, jec, jetType,
                        uncertaintiesFallbackJetType=uncertaintiesFallbackJetType,
                        regroupTag=regroupTag, session=session)
                    config.jesUncertainties = [(src, plf) for src in jesUncertaintySources]
    if jec is None:
        if jecLevels and jecLevels != "default":
            logger.error("JEC levels specified, but no JEC tag; no correction will be done")
        if jesUncertaintySources:
            logger.error("JES uncertainty specified, but no JEC tag; none will be evaluated")
    if isFat:
        if jms is not None or mcYearForFatJets is not None:
            if jms is not None:
                if not hasattr(jms, "__iter__"):
                    jms = (jms, 1., 1.)
            else:
                jms = fatjet_jmsValues[mcYearForFatJets]
            config.jms = jms
            if gms is not None:
                if not hasattr(gms, "__iter__"):
                    gms = (gms, 1., 1.)
            else:
                if isTau21DDT:
                    gms = fatjet_gmsValues_tau21DDT[mcYearForFatJets]
                else:
                    gms = jms
            config.gms = gms
        elif gms is not None:  # groomed only, explicitly passed
            config.gms = gms
        # PUPPI
        config.puppiGenFormula = fatjet_puppi_msd_params["gen"]
        config.puppi_reco_cen = fatjet_puppi_msd_params["reco_cen"]
        config.puppi_reco_for = fatjet_puppi_msd_params["reco_fwd"]
        config.puppi_resol_cen = fatjet_puppi_msd_params["resol_cen"]
        config.puppi_resol_for = fatjet_puppi_msd_params["resol_fwd"]

    # define calculator and initialize
    from .root import loadJMESystematicsCalculators, gbl
    loadJMESystematicsCalculators(backend=backend)
    jetcalcName = backend.symbol(f"const auto <<name>> = {config.cppConstruct};")
    variProxy._initCalc(op.extVar(config.calcClass, jetcalcName),
                        calcHandle=getattr(gbl, jetcalcName), args=args)
    variProxy._initFromCalc()
    _enableCalcSystematics(variProxy, enableSystematics=enableSystematics, default=isMC, name="Jet")


def configureType1MET(
        variProxy, jec=None, smear=None, isT1Smear=False,
        useGenMatch=True, genMatchDR=0.2, genMatchDPt=3.,
        jesUncertaintySources=None, regroupTag="",
        splitJER=False, addHEM2018Issue=False, enableSystematics=None,
        cachedir=None, mayWriteCache=False, isMC=False, backend=None, uName=""):
    """ Reapply JEC, set up jet smearing, or prepare JER/JES uncertainties collections

    :param variProxy: MET variations proxy, e.g. ``tree._MET``
    :param smear: tag of resolution (and scalefactors) to use for smearing
        (no smearing is done if unspecified)
    :param isT1Smear: T1Smear (smeared as nominal, all variations with respect to that) if True,
        otherwise T1 (JES variations with respect to the unsmeared MET,
        jerup and jerdown variations are nominally smeared)
    :param jec: tag of the new JEC to apply, or for the JES uncertainties
    :param jesUncertaintySources: list of jet energy scale uncertainty sources (see the
        `JECUncertaintySources twiki <https://twiki.cern.ch/twiki/bin/viewauth/CMS/JECUncertaintySources>`_),
        ``"All"``, or ``"Merged"``, for all regrouped uncertainties
        (in which case ``regroupTag`` can be specified)
    :param regroupTag: version of the regrouped uncertainties to use
    :param enableSystematics: filter systematics variations to enable
        (collection of names or callable that takes the variation name;
        default: all that are available for MC, none for data)

    :param useGenMatch: use matching to generator-level jets for resolution smearing
    :param genMatchDR: DeltaR for generator-level jet matching
        (half the cone size is recommended, default is 0.2)
    :param genMatchDPt: maximal relative PT difference
        (in units of the resolution) between reco and gen jet
    :param splitJER: vary the JER uncertainty independently in six kinematic bins (see the
        `JER uncertainty twiki
        <https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution#Run2_JER_uncertainty_correlation>`_)
    :param addHEM2018Issue: add a JES uncertainty for the HEM issue in 2018 (see
        `this hypernews post <https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/2000.html>`_)
    :param cachedir: alternative root directory to use for the txt files cache,
        instead of ``$XDG_CACHE_HOME/bamboo`` (usually ``~/.cache/bamboo``)
    :param mayWriteCache: flag to indicate if this task is allowed to write to the cache status file
        (set to False for worker tasks to avoid corruption due to concurrent writes)

    :param be: backend pointer
    :param uName: [deprecated, ignored]
        unique name for the correction calculator (sample name is a safe choice)
    :param isMC: MC or not
    """
    if uName != "":
        warnings.warn("Passing uName to configureType1MET"
                      "is not necessary anymore (and ignored), please update",
                      DeprecationWarning)
    isFixEE2017 = variProxy.orig.pt.op.name.startswith("METFixEE2017_")
    isPuppi = ("Puppi" in variProxy.orig.pt.op.name)
    from . import treefunctions as op  # first to load default headers/libs, if still needed
    from .treefunctions import _to, _tp  # treeoperations and treeproxies
    from itertools import repeat
    evt = variProxy._parent
    jets = evt._Jet.orig if hasattr(evt, "_Jet") else evt.Jet[0]
    args = [getattr(jets[0], comp).op.arg for comp in (
        "pt", "eta", "phi", "mass", "rawFactor", "area", "muonSubtrFactor", "neEmEF", "chEmEF")]
    if addHEM2018Issue:
        if isFixEE2017:
            raise RuntimeError(
                "You can either use the EE 2017 fix, or the 2018 HEM issue variation, "
                "but not both at a time, for the MET")
        args.append(jets[0].jetId.op.arg)
    else:
        if not isFixEE2017:
            args.append(_to.ExtVar("ROOT::VecOps::RVec<int>", "ROOT::VecOps::RVec<int>{}"))
    args.append(_to.GetColumn("Float_t", "fixedGridRhoFastjetAll"))
    evt = variProxy._parent
    if isMC:
        args.append((evt.run << 20) + (evt.luminosityBlock << 10) + evt.event + 1 + op.static_cast(
            "unsigned", op.switch(op.rng_len(jets) != 0, jets[0].eta / .01, op.c_float(0.))))
        aGJet = evt.GenJet[0]
        args += [getattr(aGJet, comp).op.arg for comp in ("pt", "eta", "phi", "mass")]
    else:
        args.append(_tp.makeConst(0, "unsigned"))  # no seed
        args += list(repeat(_to.ExtVar("ROOT::VecOps::RVec<float>", "ROOT::VecOps::RVec<float>{}"), 4))
    if isPuppi:
        args += [evt.RawPuppiMET.phi, evt.RawPuppiMET.pt]
    else:
        args += [evt.RawMET.phi, evt.RawMET.pt]
    args += [variProxy.orig.MetUnclustEnUpDeltaX, variProxy.orig.MetUnclustEnUpDeltaY]
    aT1Jet = evt.CorrT1METJet[0]
    args += [getattr(aT1Jet, comp).op.arg for comp in (
        "rawPt", "eta", "phi", "area", "muonSubtrFactor")]
    args += [getattr(aT1Jet, comp).op.arg if hasattr(aT1Jet, comp)
             else _to.ExtVar("ROOT::VecOps::RVec<float>", "ROOT::VecOps::RVec<float>{}")
             for comp in ("neEmEF", "chEmEF")]
    if isFixEE2017:
        args += [evt.MET.phi, evt.MET.pt, variProxy.orig.phi, variProxy.orig.pt]
    # fill configuration
    from CMSJMECalculators import config as calcConfigs
    config = (calcConfigs.METVariations() if not isFixEE2017
              else calcConfigs.FixEE2017METVariations())
    jetType = "AK4PFchs"
    if smear is not None or jec is not None:
        from CMSJMECalculators.jetdatabasecache import JetDatabaseCache, sessionWithResponseChecks
        with sessionWithResponseChecks() as session:
            if smear is not None:
                jrDBCache = JetDatabaseCache(
                    "JRDatabase", repository="cms-jet/JRDatabase",
                    cachedir=cachedir, mayWrite=mayWriteCache, session=session)
                config.ptResolution = jrDBCache.getPayload(smear, "PtResolution", jetType,
                                                           session=session)
                config.ptResolutionSF = jrDBCache.getPayload(smear, "SF", jetType, session=session)
                config.splitJER = splitJER
                config.useGenMatch = useGenMatch
                config.genMatchDR = genMatchDR
                config.genMatchDPt = genMatchDPt
                config.isT1SmearedMET = isT1Smear
            if jec is not None:
                jecLevels_L1 = ["L1FastJet"]
                # "L3Absolute" left out because it is dummy according to
                # https://twiki.cern.ch/twiki/bin/view/CMS/IntroToJEC#Mandatory_Jet_Energy_Corrections
                if jec.endswith("_DATA"):
                    jecLevels = jecLevels_L1 + ["L2Relative", "L2L3Residual"]
                elif jec.endswith("_MC"):
                    # "L2L3Residual" could be added, but it is dummy for MC according to
                    # https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetCorApplication  # noqa: B950
                    jecLevels = jecLevels_L1 + ["L2Relative"]
                else:
                    raise ValueError(
                        f"JEC tag {jec} does not end with '_DATA' or '_MC', "
                        "so the levels cannot be guessed")
                jecDBCache = JetDatabaseCache(
                    "JECDatabase", repository="cms-jet/JECDatabase",
                    cachedir=cachedir, mayWrite=mayWriteCache, session=session)
                if jecLevels:
                    config.jec = [
                        jecDBCache.getPayload(jec, jLev, jetType, session=session)
                        for jLev in jecLevels]
                if jecLevels_L1:
                    config.l1Jec = [
                        jecDBCache.getPayload(jec, jLev, jetType, session=session)
                        for jLev in jecLevels_L1]
                config.addHEM2018Issue = addHEM2018Issue
                if jesUncertaintySources:
                    plf, jesUncertaintySources = _getJESUncertaintySources(
                        jesUncertaintySources, jecDBCache, jec, jetType,
                        regroupTag=regroupTag, session=session)
                    config.jesUncertainties = [(src, plf) for src in jesUncertaintySources]
    if jec is None and jesUncertaintySources:
        logger.error("JES uncertainty specified, but no JEC tag; none will be evaluated")
    # define calculator and initialize
    from .root import loadJMESystematicsCalculators, gbl
    loadJMESystematicsCalculators(backend=backend)
    metcalcName = backend.symbol(f"const auto <<name>> = {config.cppConstruct};")
    variProxy._initCalc(op.extVar(config.calcClass, metcalcName),
                        calcHandle=getattr(gbl, metcalcName), args=args)
    variProxy._initFromCalc()
    _enableCalcSystematics(variProxy, enableSystematics=enableSystematics, default=isMC, name="MET")


def splitVariation(variProxy, variation, regions, nomName="nom"):
    """
    Split a systematic variation between (kinematic) regions (to decorrelate the nuisance parameter)

    :param variProxy: jet variations proxy, e.g. ``tree._Jet``
    :param variation: name of the variation that should be split (e.g. "jer")
    :param regions: map of region names and selections
        (for non-collection objects: boolean expression, for collection objects:
        a callable that returns a boolean for an item from the collection)
    :param nomName: name of the nominal variation ("nom" for postprocessed, "nominal" for calculator)

    :Example:

    >>> splitVariation(tree._Jet, "jer", {"forward" : lambda j : j.eta > 0.,
    >>>                                   "backward" : lambda j : j.eta < 0.})
    """
    if not (hasattr(variProxy, "brMapMap")
            and f"{variation}up" in variProxy.brMapMap
            and f"{variation}down" in variProxy.brMapMap):
        raise RuntimeError(
            f"Could not find up and down variation for {variation} "
            f"(available: {list(variProxy.brMapMap.keys())!s})")
    from itertools import chain
    from functools import partial
    from . import treefunctions as op
    from .treeoperations import adaptArg
    from .treeproxies import ListBase
    nomProxy = variProxy[nomName]
    for direction in ("up", "down"):
        origVarName = f"{variation}{direction}"
        origBrMap = variProxy.brMapMap[origVarName]
        for regNm, regSel in regions.items():
            if isinstance(nomProxy, ListBase):  # collection
                regBrMap = {attN: adaptArg(op.map(nomProxy, partial(
                    lambda osel, oatt, attn, obj: op.switch(
                        osel(obj), oatt.result[obj._idx], getattr(obj, attn)),
                    regSel, origAtt, attN)
                )) for attN, origAtt in origBrMap.items()}
            else:  # non-collection
                regBrMap = {
                    attN: adaptArg(op.switch(regSel, origAtt, getattr(nomProxy, attN)))
                    for attN, origAtt in origBrMap.items()}
            variProxy.brMapMap[f"{variation}{regNm}{direction}"] = regBrMap
    # adjust varMap and enabled variations for with-syst ops (as in initFromCalc and configure* above)
    origVarNames = tuple(f"{variation}{direction}" for direction in ("up", "down"))
    newVarNames = tuple(f"{variation}{regNm}{direction}"
                        for regNm in regions.keys() for direction in ("up", "down"))
    for attN, opWithSyst in variProxy.brMapMap[getattr(variProxy, "withSystName", "nomWithSyst")].items():
        if opWithSyst._cache:
            raise RuntimeError(
                "Expression has already been used, changing now would lead to undefined behaviour")
        for nvN in newVarNames:
            if attN in variProxy.brMapMap[nvN]:
                opWithSyst.varMap[nvN] = variProxy.brMapMap[nvN][attN]
        opWithSyst.variations = tuple(chain(
            (varnm for varnm in opWithSyst.variations if varnm not in origVarNames), newVarNames))


def forceDefine(arg, selection, includeSub=True):
    """ Force the definition of an expression as a column at a selection stage

    Use only for really computation-intensive operations that need to be precalculated

    :param arg: expression to define as a column
    :param selection: :py:class:`~bamboo.plots.Selection` for which the expression should be defined
    :param includeSub: also precalculate for data-driven background 'shadow' selections
        (:py:class:`bamboo.plots.SelectionWithSub` 'sub'-selections)
    """
    if arg is None:
        raise RuntimeError(
            "Trying to define None. If a correction calculator product was passed: "
            "has the calculator been added and configured?")
    from .treeoperations import adaptArg
    op = adaptArg(arg)
    if not op.canDefine:
        raise RuntimeError(f"Cannot define {op!r}")
    selection._fbe.define(op, selection)
    from .plots import SelectionWithSub
    if includeSub and isinstance(selection, SelectionWithSub):
        for subSel in selection.sub.values():
            if subSel is not None:
                selection._fbe.define(op, subSel)


def addPrintout(selection, funName, *args):
    '''
    Call a method with debugging printout, as part of the RDataFrame graph

    This method is only meant to work with the default backend, since it works
    by inserting a ``Filter`` node that lets all events pass.

    :param selection: selection for which to add the printout.
        The function call will be added to the RDataFrame graph in its current state,
        so if a plot causes a problem this method should be called before defining it.
    :param funName: name of a C++ method to call.
        This method should always return ``true``, and can take any number of arguments.
    :param args: arguments to pass to the function

    The following example would print the entry and event  number
    for each event that passes some selection.

    :Example:

    >>> from bamboo.root import gbl
    >>> gbl.gInterpreter.Declare("""
    ... bool bamboo_printEntry(long entry, long event) {
    ...   std::cout << "Processing entry #" << entry << ": event " << event << std::endl;
    ... }""")
    >>> addPrintout(sel, "bamboo_printEntry", op.extVar("ULong_t", "rdfentry_"), t.event)
    '''
    from . import treefunctions as op
    from .treeoperations import boolType
    be = selection._fbe
    if selection.name not in be.selDFs:
        raise RuntimeError("This trick will only work with a dynamically constructed RDataFrame")
    nd = be.selDFs[selection.name].fdnd
    callPrint = op.extMethod(funName, returnType=boolType)(*args)
    filterStr = nd(callPrint.op)
    logger.debug(f"Adding printout with {filterStr}")
    nd.df = be.df_filter(nd.df, filterStr, callPrint.op, nd)


def makePileupWeight(
        puWeights, numTrueInteractions, systName=None,
        nameHint=None, sel=None, defineOnFirstUse=True):
    """
    Construct a pileup weight for MC, based on the weights in a JSON file

    :param puWeights: path of the JSON file with weights (binned in NumTrueInteractions)
        for cp3-llbb JSON, or tuple of JSON path and correction name (correctionlib JSON)
    :param numTrueInteractions: expression to get the number of true interactions
        (Poissonian expectation value for an event)
    :param systName: name of the associated systematic nuisance parameter
    :param sel: a selection in the current graph (only used to retrieve a pointer to the backend)
    """
    from . import treefunctions as op
    if isinstance(puWeights, tuple):
        from .scalefactors import get_correction
        expr = get_correction(
            puWeights[0], puWeights[1],
            params={"NumTrueInteractions": numTrueInteractions},
            systParam="weights", systNomName="nominal", systVariations=("up", "down"),
            systName=systName,  # will enable or disable systematic variations
            sel=sel, defineOnFirstUse=defineOnFirstUse
        )(None)
    else:
        paramVType = "Parameters::value_type::value_type"
        puArgs = op.construct(
            "Parameters", (op.initList(
                f"std::initializer_list<{paramVType}>", paramVType,
                (op.initList(paramVType, "float", (op.extVar(
                    "int", "BinningVariable::NumTrueInteractions"), numTrueInteractions)),)),))
        puWFun = op.define("ILeptonScaleFactor",
                           f'const ScaleFactor <<name>>{{"{puWeights}"}};', nameHint=nameHint)
        expr = puWFun.get(puArgs, op.extVar("int", "Nominal"))
        if systName:
            expr = op.systematic(
                expr, name=systName,
                up=puWFun.get(puArgs, op.extVar("int", "Up")),
                down=puWFun.get(puArgs, op.extVar("int", "Down")))
        if defineOnFirstUse:
            expr = op.defineOnFirstUse(expr)
    return expr


def makeMultiPrimaryDatasetTriggerSelection(sampleName, datasetsAndTriggers):
    """ Construct a selection that prevents processing multiple times (from different primary datasets)

    If an event is passes triggers for different primary datasets, it will be taken
    from the first of those (i.e. the selection will be 'passes one of the triggers that
    select it for this primary dataset, and not for any of those that come before in the
    input dictionary).

    :param sampleName: sample name
    :param datasetsAndTriggers: a dictionary ``{primary-dataset, set-of-triggers}``, where
        the key is either a callable that takes a sample name and returns true in case
        it originates from the corresponding primary datasets, or a string that is
        the first part of the sample name in that case. The value (second item) can be
        a single expression (e.g. a trigger flag, or an OR of them), or a list of those
        (in which case an OR-expression is constructed from them).
    :returns: an expression to filter the events in the sample with given name

    :Example:

    >>> if not self.isMC(sample):
    >>>     trigSel = noSel.refine("trigAndPrimaryDataset",
    >>>         cut=makeMultiPrimaryDatasetTriggerSelection(sample, {
    >>>               "DoubleMuon" : [t.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
    >>>                               t.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL],
    >>>               "DoubleEG"   : t.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
    >>>               "MuonEG"     : [t.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
    >>>                               t.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL ]
    >>>               }))
    """
    # python3.6+ dictionaries keep insertion order
    # (implementation detail in cpython 3.6, part of the language spec since 3.7)
    # see https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
    from . import treefunctions as op
    inDSAndTrigSel = [
        ((sampleName.startswith(dsArg) if isinstance(dsArg, str) else dsArg(sampleName)),
         (op.OR(*trigArg) if hasattr(trigArg, "__iter__") else trigArg))
        for dsArg, trigArg in (
            datasetsAndTriggers.items() if isinstance(datasetsAndTriggers, dict)
            else datasetsAndTriggers)]
    sels_not = []
    trigSel = None
    for inThisDataset, dsTrigSel in inDSAndTrigSel:
        if not inThisDataset:
            sels_not.append(dsTrigSel)
        else:
            trigSel = dsTrigSel
            break
    if trigSel is None:
        raise RuntimeError(f"Sample name {sampleName} matched none of the primary datasets")
    if len(sels_not) == 0:  # first
        return trigSel
    else:
        return op.AND(op.NOT(op.OR(*sels_not)), trigSel)


def configureRochesterCorrection(variProxy, paramsFile, isMC=False, backend=None, uName=""):
    """ Apply the Rochester correction for muons

    :param variProxy: muon variatons proxy, e.g. ``tree.._Muon`` for NanoAOD
    :param paramsFile: path of the text file with correction parameters
    :param isMC: MC or not
    :param backend: backend pointer
        (returned from :py:meth:`~bamboo.analysismodules.HistogramsModule.prepareTree`)
    :param uName: [deprecated, ignored]
        unique name for the correction calculator (sample name is a safe choice)
    """
    if uName != "":
        warnings.warn("Passing uName to configureRochesterCorrection "
                      "is not necessary anymore (and ignored), please update",
                      DeprecationWarning)
    from bamboo.treefunctions import _to, _tp
    aMu = variProxy.orig[0]
    args = [getattr(aMu, comp).op.arg for comp in (
        "pt", "eta", "phi", "mass", "charge", "nTrackerLayers")]
    if isMC:
        args += [aMu.genPart._idx.arg, variProxy._parent.GenPart[0].pt.op.arg]
        evt = variProxy._parent
        args.append((evt.run << 20) + (evt.luminosityBlock << 10) + evt.event + 169)
    else:
        args += [
            _to.ExtVar("ROOT::VecOps::RVec<Int_t>", "ROOT::VecOps::RVec<Int_t>{}"),
            _to.ExtVar("ROOT::VecOps::RVec<float>", "ROOT::VecOps::RVec<float>{}"),
            _tp.makeConst(0, "unsigned")]  # no seed
    # load necessary library and header(s)
    from . import treefunctions as op  # first to load default headers/libs, if still needed
    from .root import loadRochesterCorrectionCalculator, gbl
    loadRochesterCorrectionCalculator(backend=backend)
    if not os.path.exists(paramsFile):
        raise ValueError(f"File {paramsFile} not found")
    # define calculator and initialize
    roccorName = backend.symbol(
        f'RochesterCorrectionCalculator <<name>>{{"{paramsFile}"}};')
    variProxy._initCalc(op.extVar("RochesterCorrectionCalculator", roccorName),
                        calcHandle=getattr(gbl, roccorName),
                        args=args)
    variProxy._initFromCalc()
    assert variProxy.calcProd
