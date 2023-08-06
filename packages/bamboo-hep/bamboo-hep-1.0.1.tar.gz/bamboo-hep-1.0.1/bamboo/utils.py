"""
General (not bamboo-specific) utilities
"""
import os
import os.path
import subprocess


# based on https://stackoverflow.com/a/64474435/11079521
def getlcwd():
    """ os.getcwd() with a logical path ($PWD, if available, or `pwd -L`) """
    if "PWD" in os.environ:
        return os.environ["PWD"]
    else:
        return subprocess.check_output(["pwd", "-L"]).decode().strip()


def labspath(path):
    """ os.path.abspath using pwd with symbolic links """
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(getlcwd(), path)


class _DirsAboveStat:
    def __init__(self, aPath):
        self.aPath = aPath
        self.above = {}
        iP = aPath
        while os.path.dirname(iP) != iP:
            self.above[iP] = None
            iP = os.path.dirname(iP)

    def __iter__(self):
        yield from self.above.keys()

    def __getitem__(self, dPath):
        if dPath not in self.above:
            raise KeyError(f"{dPath} not found")
        if self.above[dPath] is None:
            self.above[dPath] = os.stat(dPath)
        return self.above[dPath]


def realcommonpath(pathA, pathB):
    """ Use os.path.samefile to find the lowest common base dir """
    dirsA = _DirsAboveStat(pathA)
    dirsB = _DirsAboveStat(pathB)
    for dA in dirsA:
        for dB in dirsB:
            if dirsA[dA] == dirsB[dB]:
                return dA, dB
