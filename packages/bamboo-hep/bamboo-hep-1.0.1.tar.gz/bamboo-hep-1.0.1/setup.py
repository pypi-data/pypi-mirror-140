""" Setuptools-based setup module for bamboo """
import os
import os.path

import pkg_resources
from setuptools import find_packages

from skbuild import setup

try:
    from sphinx.setup_command import BuildDoc
except ImportError:
    BuildDoc = None

cmake_args = []
if "VIRTUAL_ENV"in os.environ:  # allow picking up packages from virtualenv
    cmake_args.append("-DCMAKE_PREFIX_PATH={}".format(os.environ["VIRTUAL_ENV"]))
try:  # pick up pytorch from environment (needs --no-build-isolation)
    torch_cmake_locPath = os.path.join("share", "cmake", "Torch")
    if (pkg_resources.resource_exists("torch", torch_cmake_locPath)
        and (pkg_resources.get_distribution("torch").parsed_version
             >= pkg_resources.parse_version("1.2.0"))):
        cmake_args.append("-DTorch_DIR={}".format(
            pkg_resources.resource_filename("torch", torch_cmake_locPath)))
except ImportError:
    print(
        "Warning: optional dependency torch (>=1.2.0) not found. "
        "Install bamboo[torch] to install it as a dependency, "
        "or use --no-build-isolation to pick up an existing install from the environment")

setup(
    packages=find_packages(".", exclude=["ext", "tests", "examples"]),
    cmake_source_dir="ext",
    cmake_args=cmake_args,
    cmdclass={
        "build_sphinx": BuildDoc
    }
)
