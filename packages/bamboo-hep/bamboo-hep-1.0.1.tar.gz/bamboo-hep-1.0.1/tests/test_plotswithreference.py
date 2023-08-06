"""
Histogram comparison test, to be run locally (requires access to CMS NanoAOD)

The reference directory (passed with --plots-reference) should contain
- test_zmm_ondemand.yml: config for runinng with on-the-fly jet&met
- test_zmm_postproc.yml: config for runinng on postprocessed NanoAOD
- plots_ondemand/results: output dir with ROOT files from running with on-the-fly jet&met
- plots_postproc/results: output dir with ROOT files from running on postprocessed NanoAOD
(with the files and tags they should be very close, but not identical due to
differences in numerical and stored precision)
The directory structure for the results is the same the output produced with
the optional --plots-output argument (otherwise a temporary directory is used)
to make it easier to make a new reference directory.
The `tests/diffHistsAndFiles.py` script can also be used directly to compare
all histograms in two results directories (the arguments should be the
``results`` directories to compare then)
"""

import os.path
import subprocess

import pytest

from diffHistsAndFiles import diffResultsDirs

examples = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")


@pytest.fixture(scope="module")
def output_plots_ondemand(plots_output, tmpdir_factory):
    if plots_output:
        output = os.path.join(plots_output, "plots_ondemand")
        os.makedirs(output, exist_ok=True)
    else:
        output = tmpdir_factory.mktemp("plots_ondemand")
    return output


@pytest.fixture(scope="module")
def output_plots_postproc(plots_output, tmpdir_factory):
    if plots_output:
        output = os.path.join(plots_output, "plots_postproc")
        os.makedirs(output, exist_ok=True)
    else:
        output = tmpdir_factory.mktemp("plots_postproc")
    return output


@pytest.mark.plotswithreference
def test_plots_ondemand(plots_reference, output_plots_ondemand):
    assert subprocess.run([
        "bambooRun",
        "--git-policy=testing",
        "--module={}:NanoZMuMu".format(os.path.join(examples, "nanozmumu.py")),
        os.path.join(plots_reference, "test_zmm_ondemand.yml"),
        f"--output={output_plots_ondemand}"]).returncode == 0
    assert not diffResultsDirs(os.path.join(output_plots_ondemand, "results"),
                               os.path.join(plots_reference, "plots_ondemand", "results"))


@pytest.mark.plotswithreference
def test_plots_postproc(plots_reference, output_plots_postproc):
    assert subprocess.run([
        "bambooRun",
        "--git-policy=testing",
        "--module={}:NanoZMuMu".format(os.path.join(examples, "nanozmumu.py")),
        os.path.join(plots_reference, "test_zmm_postproc.yml"),
        "--postprocessed",
        f"--output={output_plots_postproc}"]).returncode == 0
    assert not diffResultsDirs(os.path.join(output_plots_postproc, "results"),
                               os.path.join(plots_reference, "plots_postproc", "results"))
