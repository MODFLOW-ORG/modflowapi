from pathlib import Path

import modflow_devtools.models as models
import pytest

from modflowapi import run_simulation

examples = models.get_examples()
pytestmark = pytest.mark.mf6
dll = "libmf6"


def _get_model_relpath(model_name) -> str:
    head, _, tail = model_name.rpartition("_")
    return str(Path(head) / tail)


@pytest.mark.parametrize("example_name", examples.keys())
def test_example(function_tmpdir, example_name):
    model_names = examples[example_name]
    n_models = len(model_names)
    for model_name in model_names:
        model_relpath = _get_model_relpath(model_name) if n_models > 1 else model_name
        workspace = function_tmpdir / model_relpath
        models.copy_to(workspace, model_name, verbose=True)
        run_simulation(dll, workspace, lambda sim, step: None, verbose=True)
