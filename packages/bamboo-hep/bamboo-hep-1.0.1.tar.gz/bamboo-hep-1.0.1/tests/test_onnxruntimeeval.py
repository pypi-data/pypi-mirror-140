import os.path

import pytest

from bamboo.root import findLibrary
from helpers import isclose_float

onnxRuntime_found = findLibrary("libonnxruntime")
if not onnxRuntime_found and "VIRTUAL_ENV" in os.environ:
    ortlib_guessed_path = os.path.join(os.environ["VIRTUAL_ENV"], "lib", "libonnxruntime.so")
    if os.path.exists(ortlib_guessed_path):
        onnxRuntime_found = ortlib_guessed_path
pytestmark = pytest.mark.skipif(not onnxRuntime_found, reason="ONNX Runtime not found")

testData = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture(scope="module")
def onnxruntime_nn1():
    from bamboo.root import gbl, loadONNXRuntime
    loadONNXRuntime()
    gbl.gInterpreter.Declare('std::vector<const char*> outNames_1 = {"dense_6"};')
    yield gbl.bamboo.ONNXRuntimeEvaluator(os.path.join(testData, "nn1.onnx"), gbl.outNames_1)


def test_onnxruntime_load(onnxruntime_nn1):
    assert onnxruntime_nn1


def test_onnxruntime_evalZero(onnxruntime_nn1):
    from bamboo.root import gbl
    v_in = gbl.std.vector["float"]()
    for _i in range(5):
        v_in.push_back(.7)
    v_out = onnxruntime_nn1.evaluate(v_in)
    assert (v_out.size() == 2) and isclose_float(sum(v_out), 1.)


def test_onnxruntime_evalRandom(onnxruntime_nn1):
    from bamboo.root import gbl
    import random
    v_in = gbl.std.vector["float"]()
    for _i in range(5):
        v_in.push_back(random.uniform(0., 1.))
    v_out = onnxruntime_nn1.evaluate(v_in)
    assert (v_out.size() == 2) and isclose_float(sum(v_out), 1.)
