import pytest


def pytest_addoption(parser):
    parser.addoption("--plots-reference", action="store", help="Directory with reference plots")
    parser.addoption("--plots-output", action="store", help="Directory to store the produced plots")
    parser.addoption("--with-compiled", action="store_true",
                     help="Run the tests with the compiled backend")


@pytest.fixture(scope="session")
def plots_reference(request):
    return request.config.getoption("--plots-reference")


@pytest.fixture(scope="session")
def plots_output(request):
    return request.config.getoption("--plots-output")


@pytest.fixture(scope="session")
def with_compiled(request):
    return request.config.getoption("--with-compiled")


def pytest_configure(config):
    config.addinivalue_line("markers", "plotswithreference: produce and compare plots (slow)")
    config.addinivalue_line("markers", "withcompiled: produce and compare plots (slow, high memory)")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--plots-reference"):  # --plots-reference not given in cli: skip plots
        skip_plots_with_reference = pytest.mark.skip(reason="need --plots-reference option to run")
        for item in items:
            if "plotswithreference" in item.keywords:
                item.add_marker(skip_plots_with_reference)
    if not config.getoption("--with-compiled"):  # --with-compiled not given in cli: skip plots
        skip_with_compiled = pytest.mark.skip(reason="need --with-compiled option to run")
        for item in items:
            if "withcompiled" in item.keywords:
                item.add_marker(skip_with_compiled)
