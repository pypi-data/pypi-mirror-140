#!/usr/bin/env python3
import logging
import os
import os.path

logger = logging.getLogger(__name__)

PRINT_LEVELS = ["directory", "file", "histogram", "bin"]
LV_DIR = 0
LV_FILE = 1
LV_HISTOGRAM = 2
LV_BIN = 3


class LoggingDiffCollector:
    def __init__(self, level=0):
        self.level = level
        self.hasDiff = False

    def add(self, msg, level=0):
        self.hasDiff = True
        if level <= self.level:
            logger.error(msg)


def diffHistos(hA, hB, name=None, printLevel=0):
    diffs = LoggingDiffCollector(printLevel)
    nBinsOK, nBinsD = 0, 0
    assert hA.GetNcells() == hB.GetNcells()
    nBins = hA.GetNcells()
    for i in range(nBins):
        bcA = hA.GetBinContent(i)
        bcB = hB.GetBinContent(i)
        if bcA != bcB:
            diffs.add(f"Difference in bin {i:d} of histogram {name}: {bcA:e} (ref) vs {bcB:e} (test)", LV_BIN)
            nBinsD += 1
        else:
            nBinsOK += 1
    if nBinsD:
        diffs.add(f"{nBinsD:d} bins different for histogram {name} ({nBinsOK:d} equal)", LV_HISTOGRAM)
    return diffs.hasDiff


def diffFiles(fA, fB, name=None, skipSystematicVariations=False, printLevel=0):
    diffs = LoggingDiffCollector(printLevel)
    from cppyy import gbl
    histosA = {ky.GetName() for ky in fA.GetListOfKeys() if isinstance(ky.ReadObj(), gbl.TH1)}
    histosB = {ky.GetName() for ky in fB.GetListOfKeys() if isinstance(ky.ReadObj(), gbl.TH1)}
    if skipSystematicVariations:
        histosA = {nm for nm in histosA if "__" not in nm}
        histosB = {nm for nm in histosB if "__" not in nm}
    aNotB = histosA - histosB
    bNotA = histosB - histosA
    if aNotB:
        diffs.add(f"Histograms in reference but not in test for {name}: {', '.join(aNotB)}", LV_FILE)
    if bNotA:
        diffs.add(f"Histograms in test but not in reference for {name}: {', '.join(bNotA)}", LV_FILE)
    cmHistoNames = list(histosA.intersection(histosB))
    nHistosOK, nHistosD = 0, 0
    for hName in cmHistoNames:
        hA = fA.Get(hName)
        hB = fB.Get(hName)
        if diffHistos(hA, hB, name=f"{hName} in file {name}", printLevel=printLevel):
            nHistosD += 1
        else:
            nHistosOK += 1
    if nHistosD:
        diffs.add(f"{nHistosD:d} histograms with differences in file {name} ({nHistosOK:d} equal)", LV_FILE)
    return diffs.hasDiff


def collectFiles(dirX):
    fileNames = []
    for root, _dirs, files in os.walk(dirX):
        for f in files:
            if not f.startswith("__"):
                fileNames.append(os.path.relpath(os.path.join(root, f), dirX))
    return fileNames


def diffResultsDirs(test_dir, ref_dir, skipSystematicVariations=False, printLevel=0):
    diffs = LoggingDiffCollector(printLevel)
    fileNamesA = set(collectFiles(ref_dir))
    fileNamesB = set(collectFiles(test_dir))
    aNotB = fileNamesA - fileNamesB
    bNotA = fileNamesB - fileNamesA
    if aNotB:
        diffs.add(f"Files in reference but not in test: {', '.join(aNotB)}", LV_DIR)
    if bNotA:
        diffs.add(f"Files in test but not in reference: {', '.join(bNotA)}", LV_DIR)
    cmFileNames = list(fileNamesA.intersection(fileNamesB))
    nFilesOK, nFilesD = 0, 0
    from cppyy import gbl
    for fn in cmFileNames:
        fA = gbl.TFile.Open(os.path.join(ref_dir, fn))
        fB = gbl.TFile.Open(os.path.join(test_dir, fn))
        if diffFiles(fA, fB, name=fn, printLevel=printLevel,
                     skipSystematicVariations=skipSystematicVariations):
            nFilesD += 1
        else:
            nFilesOK += 1
    if nFilesD:
        diffs.add(f"{nFilesD:d} files with differences ({nFilesOK:d} equal)", LV_DIR)
    return diffs.hasDiff


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Compare histograms in all ROOT files between two directories")
    parser.add_argument("test_dir", help="Test directory with histograms")
    parser.add_argument("reference_dir", help="Reference directory with histograms")
    parser.add_argument("--print-level", default="bin", choices=PRINT_LEVELS,
                        help="Printout detail level")
    parser.add_argument("--skip-systematic-variations", action="store_true",
                        help="Skip systematic variation histograms")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if diffResultsDirs(
            args.test_dir, args.reference_dir,
            skipSystematicVariations=args.skip_systematic_variations,
            printLevel=PRINT_LEVELS.index(args.print_level)):
        import sys
        sys.exit(1)
