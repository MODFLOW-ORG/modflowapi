from itertools import groupby
from os import linesep
from pathlib import Path
from tempfile import gettempdir

import pytest
from filelock import FileLock
from modflow_devtools.download import download_and_unzip

# import modflow-devtools fixtures
pytest_plugins = ["modflow_devtools.fixtures"]


__mf6_examples = "mf6_examples"
__mf6_examples_path = Path(gettempdir()) / __mf6_examples
__mf6_examples_lock = FileLock(Path(gettempdir()) / f"{__mf6_examples}.lock")


def get_mf6_examples_path() -> Path:
    # use file lock so mf6 distribution is downloaded once,
    # even when tests are run in parallel with pytest-xdist
    __mf6_examples_lock.acquire()
    try:
        if not __mf6_examples_path.is_dir():
            __mf6_examples_path.mkdir(exist_ok=True)
            download_and_unzip(
                url="https://github.com/MODFLOW-USGS/modflow6-examples/releases/download/current/modflow6-examples.zip",
                path=__mf6_examples_path,
                verbose=True,
            )
        return __mf6_examples_path
    finally:
        __mf6_examples_lock.release()


def pytest_addoption(parser):
    parser.addoption("--mf6-examples-path", action="store", default=None)


def is_nested(namfile) -> bool:
    p = Path(namfile)
    if not p.is_file() or not p.name.endswith(".nam"):
        raise ValueError(f"Expected a namfile path, got {p}")
    return p.parent.parent.name != __mf6_examples


def pytest_generate_tests(metafunc):
    # examples to skip:
    #   - ex-gwtgwt-mt3dms-p10: https://github.com/MODFLOW-USGS/modflow6/pull/1008
    option_value = metafunc.config.option.mf6_examples_path
    t = metafunc.fixturenames
    if "mf6_example_namfiles" in metafunc.fixturenames and option_value is not None:
        mf6_examples_path = Path(option_value)
        global __mf6_examples
        __mf6_examples = str(mf6_examples_path.name)
    else:
        mf6_examples_path = get_mf6_examples_path()

    # grouping...
    exclude = [
        "ex-gwt-gwtgwt-mt3dms-p10",
        "mp7-p02",
        "mp7-p04",
        "synthetic-valley",
    ]
    namfiles = [
        str(p)
        for p in mf6_examples_path.rglob("mfsim.nam")
        if not any(e in str(p) for e in exclude)
    ]

    # parametrization by model
    #   - single namfile per test case
    #   - no coupling (only first model in each simulation subdir is used)
    key = "mf6_example_namfile"
    if key in metafunc.fixturenames:
        metafunc.parametrize(key, sorted(namfiles))

    # parametrization by simulation
    #   - each test case gets an ordered list of 1+ namfiles
    #   - models can be coupled (run in order provided, sharing workspace)
    key = "mf6_example_namfiles"
    if key in metafunc.fixturenames:
        simulations = []

        def simulation_name_from_model_path(p):
            p = Path(p)
            return p.parent.parent.name if is_nested(p) else p.parent.name

        for model_name, model_namfiles in groupby(
            namfiles, key=simulation_name_from_model_path
        ):
            models = []
            model_namfiles = list(model_namfiles)
            if len(model_namfiles) > 1:
                # trap gwf models as first set of models
                idxs = [ix for ix, _ in enumerate(model_namfiles) if "gwf" in _]
                if len(idxs) > 0:
                    for ix in idxs[::-1]:
                        models.append(model_namfiles.pop(ix))

            models += list(
                sorted(model_namfiles)
            )  # sort remaining models in alphabetical order (gwe < gwt < prt)
            simulations.append(models)
            print(
                f"Simulation {model_name} has {len(models)} model(s):\n"
                f"{linesep.join(model_namfiles)}"
            )

        def simulation_name_from_model_namfiles(mnams):
            try:
                namfile = next(iter(mnams), None)
            except TypeError:
                namfile = None
            if namfile is None:
                pytest.skip("No namfiles (expected ordered collection)")
            namfile = Path(namfile)
            return (
                namfile.parent.parent if is_nested(namfile) else namfile.parent
            ).name

        metafunc.parametrize(key, simulations, ids=simulation_name_from_model_namfiles)
