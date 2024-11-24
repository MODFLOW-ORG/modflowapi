from pathlib import Path
from shutil import copytree

import pytest

from autotest.conftest import is_nested
from modflowapi import run_simulation

pytestmark = pytest.mark.mf6
dll = "libmf6"


def test_mf6_example_simulations(function_tmpdir, mf6_example_namfiles):
    """
    MF6 examples parametrized by simulation. `mf6_example_namfiles` is a list
    of models to run in order provided. Coupled models share the same tempdir

    Parameters
    ----------
    function_tmpdir: function-scoped temporary directory fixture
    mf6_example_namfiles: ordered list of namfiles for 1+ coupled models
    """
    if len(mf6_example_namfiles) == 0:
        pytest.skip("No namfiles (expected ordered collection)")
    namfile = Path(mf6_example_namfiles[0])

    nested = is_nested(namfile)
    function_tmpdir = Path(function_tmpdir / "workspace")

    copytree(
        src=namfile.parent.parent if nested else namfile.parent, dst=function_tmpdir
    )

    def callback(sim, step):
        pass

    def run_models():
        # run models in order received (should be alphabetical,
        # so gwf precedes gwt)
        for namfile in mf6_example_namfiles:
            namfile_path = Path(namfile).resolve()
            model_path = namfile_path.parent

            # working directory must be named according to namefile's parent
            # (e.g. 'mf6gwf') because coupled models refer to each other with
            # relative paths
            wrkdir = (
                Path(function_tmpdir / model_path.name) if nested else function_tmpdir
            )
            try:
                run_simulation(dll, wrkdir, callback, verbose=True)
            except Exception as e:
                raise Exception(e)

    run_models()
