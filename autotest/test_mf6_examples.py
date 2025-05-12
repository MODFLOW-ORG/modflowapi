import modflow_devtools.models as models
import pytest

from modflowapi import run_simulation

examples = models.get_examples()
pytestmark = pytest.mark.mf6
dll = "libmf6"
skip = [
    # https://github.com/MODFLOW-ORG/modflowapi/issues/53
    "ex-prt-mp7-p02",
    "ex-prt-mp7-p04",
    "ex-gwe-barends"
]


@pytest.mark.parametrize("example_name", examples.keys())
def test_example(function_tmpdir, example_name):
    if example_name in skip:
        pytest.skip(f"Skipping example {example_name}")
    for model_name in examples[example_name]:
        model_relpath = model_name.rpartition(example_name + "/")[-1]
        model_workspace = function_tmpdir / model_relpath
        models.copy_to(model_workspace, model_name, verbose=True)
        run_simulation(dll, model_workspace, lambda sim, step: None, verbose=True)
