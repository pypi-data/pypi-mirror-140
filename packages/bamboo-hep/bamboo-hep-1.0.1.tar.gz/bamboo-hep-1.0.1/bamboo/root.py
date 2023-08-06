"""
The :py:mod:`bamboo.root` module collects a set of thin wrappers around ROOT
methods, and centralizes the import of the Cling interpreter global namespace
in PyROOT. For compatibility, it is recommended that user code uses
``from bamboo.root import gbl`` rather than ``import ROOT as gbl`` or
``from cppyy import gbl``.
"""
import functools
from contextlib import contextmanager

import pkg_resources

import ROOT; gbl = ROOT  # noqa: E702
_rootVersion = gbl.gROOT.GetVersion()
_rootVersion_split = tuple(int(iv) for tk in _rootVersion.split("/") for iv in tk.split("."))
if _rootVersion_split[0] == 6 and _rootVersion_split[1] < 22:
    gbl.PyConfig.IgnoreCommandLineOptions = True


def addIncludePath(incPath):
    """ Add an include path to the ROOT interpreter """
    gbl.gInterpreter.AddIncludePath(incPath)


def loadHeader(headerName):
    """ Include a C++ header in the ROOT interpreter """
    gbl.gROOT.ProcessLine(f'#include "{headerName}"')


def addDynamicPath(libPath):
    """ Add a dynamic library path to the ROOT interpreter"""
    gbl.gSystem.AddDynamicPath(libPath)


def loadLibrary(libName):
    """ Load a shared library in the ROOT interpreter """
    st = gbl.gSystem.Load(libName)
    if st == -1:
        raise RuntimeError(f"Library {libName} could not be found")
    elif st == -2:
        raise RuntimeError(f"Version match for library {libName}")


def findLibrary(libName):
    """ Check if a library can be found, and returns the path in that case """
    ret = gbl.gSystem.FindDynamicLibrary(gbl.TString(libName), True)
    if ret != "":
        return str(ret)


def loadDependency(bambooLib=None, includePath=None, headers=None, dynamicPath=None, libraries=None):
    """
    Load a C++ extension

    :param bambooLib: name(s) of the bamboo extension libraries, if any
    :param includePath: include directory for headers
    :param headers: headers to load explicitly (which can depend on other headers in the inclue path)
    :param dynamicPath: dynamic library path to add
    :param libraries: additional shared libraries to load
    """
    def asList(arg):
        if isinstance(arg, str):
            return [arg]
        else:
            return arg
    if dynamicPath:
        for pth in asList(dynamicPath):
            addDynamicPath(pth)
    if libraries:
        for lib in asList(libraries):
            loadLibrary(f"lib{lib}")
    if includePath:
        for pth in asList(includePath):
            addIncludePath(pth)
    if headers:
        for hdr in asList(headers):
            loadHeader(hdr)
    if bambooLib:
        for lib in asList(bambooLib):
            loadLibrary(f"lib{lib}")


@contextmanager
def returnToDirectory():
    gpwd = gbl.gDirectory.GetPath()
    yield
    gbl.gDirectory.cd(gpwd)


class once:
    """ Function decorator to make sure things are not loaded more than once """
    def __init__(self, fun):
        self.fun = fun
        self.has_run = False
        functools.update_wrapper(self, fun)

    def __call__(self, **kwargs):
        if not self.has_run:
            self.has_run = True
            return self.fun(**kwargs)


_defaultHeaders = ("Math/VectorUtil.h", "bamboohelpers.h", "range.h",
                   "LumiMask.h", "bamboorandom.h",
                   "scalefactors.h", "BTagCalibrationStandalone.h")
_defaultBambooLibs = ("BambooLumiMask", "BambooRandom", "BinnedValues")
_defaultDependencies = ("ROOT::ROOTDataFrame", "ROOT::GenVector")


@once
def loadBambooExtensions():
    # Add extension libraries and necessary header files to the ROOT interpreter
    incDir = pkg_resources.resource_filename("bamboo", "include")
    libDir = pkg_resources.resource_filename("bamboo", "lib")
    import os.path
    if not (os.path.exists(incDir) and os.path.exists(libDir)):
        raise RuntimeError(
            f"Could not find {incDir} and/or {libDir}, this may happen when running "
            "from the source repository and using a virtualenv with non-editable install")
    addIncludePath(incDir)
    addDynamicPath(libDir)
    # now load default headers and libraries
    for lib in _defaultBambooLibs:
        loadLibrary(f"lib{lib}")
    for fname in _defaultHeaders:
        loadHeader(fname)


@once
def loadJMESystematicsCalculators(backend=None):
    loadBambooExtensions()
    try:
        import CMSJMECalculators
        CMSJMECalculators.loadJMESystematicsCalculators()
    except ImportError:
        raise RuntimeError(
            "Could not load jet&MET correction and systematic variations calculators. "
            "Please install them (see https://gitlab.cern.ch/cp3-cms/CMSJMECalculators "
            "for more information)"
        ) from None
    if backend:
        import pkg_resources
        calc_dir = pkg_resources.resource_filename("CMSJMECalculators", "cmake")
        backend.addDependency(
            package="CMSJMECalculators", cmakeArgs=f"-DCMSJMECalculators_DIR={calc_dir}",
            headers="JMESystematicsCalculators.h", libraries="CMSJMECalculators"
        )


@once
def loadRochesterCorrectionCalculator(backend=None):
    loadBambooExtensions()
    loader = backend.addDependency if backend else loadDependency
    loader(bambooLib="RoccoR", headers="RochesterCorrectionCalculator.h")
    getattr(gbl, "RochesterCorrectionCalculator::result_t")  # trigger dictionary generation


@once
def loadLibTorch(backend=None):
    if loadTensorflowC.has_run:
        raise RuntimeError("If loading both Tensorflow-C and libtorch, the latter should be loaded first")
    loadBambooExtensions()
    torchLib = findLibrary("libtorch")
    dynPath = None
    if (not torchLib) and pkg_resources.resource_filename("torch", "lib"):
        dynPath = pkg_resources.resource_filename("torch", "lib")
    loader = backend.addDependency if backend else loadDependency
    loader(bambooLib="BambooTorch", headers="bambootorch.h", dynamicPath=dynPath)


def _addVirtualEnvPaths():
    import os
    incPath, dynPath = None, None
    if "VIRTUAL_ENV" in os.environ:
        incPath = addIncludePath(os.path.join(os.environ["VIRTUAL_ENV"], "include"))
        dynPath = addDynamicPath(os.path.join(os.environ["VIRTUAL_ENV"], "lib"))
    return incPath, dynPath


@once
def loadTensorflowC(backend=None):
    loadBambooExtensions()
    tfLib = findLibrary("libtensorflow")
    incPath, dynPath = None, None
    if not tfLib:
        incPath, dynPath = _addVirtualEnvPaths()
    loader = backend.addDependency if backend else loadDependency
    loader(bambooLib="BambooTensorflowC", headers="bambootensorflowc.h",
           includePath=incPath, dynamicPath=dynPath, libraries="tensorflow")


@once
def loadlwtnn(backend=None):
    loadBambooExtensions()
    lwtnnLib = findLibrary("liblwtnn")
    incPath, dynPath = None, None
    if not lwtnnLib:
        incPath, dynPath = _addVirtualEnvPaths()
    loader = backend.addDependency if backend else loadDependency
    loader(bambooLib="BambooLwtnn", headers="bamboolwtnn.h",
           includePath=incPath, dynamicPath=dynPath, libraries="lwtnn")


@once
def loadONNXRuntime(backend=None):
    loadBambooExtensions()
    onnxRuntimeLib = findLibrary("libonnxruntime")
    incPath, dynPath = None, None
    if not onnxRuntimeLib:
        incPath, dynPath = _addVirtualEnvPaths()
    onnxRuntimeLib = findLibrary("libonnxruntime")
    import os.path
    incDir = os.path.join(os.path.dirname(os.path.dirname(onnxRuntimeLib)), "include")
    if os.path.isdir(os.path.join(incDir, "onnxruntime")):
        incDir = os.path.join(incDir, "onnxruntime")
    onnx_cxx_hdr = os.path.join(incDir, "core", "session", "onnxruntime_cxx_api.h")
    if not os.path.isfile(onnx_cxx_hdr):
        raise RuntimeError(f"Could not find onnxruntime header {onnx_cxx_hdr}")
    loader = backend.addDependency if backend else loadDependency
    loader(bambooLib="BambooONNXRuntime", headers="bambooonnxruntime.h",
           includePath=os.path.dirname(onnx_cxx_hdr),
           dynamicPath=dynPath, libraries="onnxruntime")


@once
def loadcorrectionlib(backend=None):
    import os.path
    loader = backend.addDependency if backend else loadDependency
    loader(headers="correction.h",
           includePath=pkg_resources.resource_filename("correctionlib", "include"),
           libraries=pkg_resources.resource_filename(
               "correctionlib", os.path.join("lib", "libcorrectionlib.so"))
           )
