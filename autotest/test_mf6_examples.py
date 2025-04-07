import modflow_devtools.models as models
import pandas as pd
import pytest

from modflowapi import run_simulation

examples = models.get_examples()
pytestmark = pytest.mark.mf6
dll = "libmf6"
skip = [
    # https://github.com/MODFLOW-ORG/modflowapi/issues/53
    "ex-prt-mp7-p02",
    "ex-prt-mp7-p04",
]

temporary_skip_state_count = set(
    [
        # Skip state count tests for these model for now.
        # There seems to be a different problem.
        "ex-gwf-fhb",
        "ex-gwf-nwt-p02a",
        "ex-gwf-nwt-p02b",
        "ex-gwe-geotherm",
        "ex-gwe-radial-slow",
    ]
)


class StateCollector:
    """
    Callback that collects the model state sequence.

    THe attribute `states` is a list of tuples `(model_name, state_name)`,
    where `state_name` is `callback_step.name`.
    """

    def __init__(self):
        self.states = []

    def __call__(self, sim, callback_step):
        self.states.append((sim.model_names[0], callback_step.name))


def count_states(states):
    """
    Count states per model.

    The numbers of `start_state` and `end_state` should match.
    """
    states = pd.DataFrame(states, columns=["model", "state"])
    counts = states.groupby(["model", "state"])[["state"]].agg("count")
    counts.columns = ["counts"]
    return counts


def compare_counts(counts):
    matches = [
        ("iteration_start", "iteration_end"),
        ("stress_period_start", "stress_period_end"),
        ("timestep_start", "timestep_end"),
    ]
    for model_name in counts.index.levels[0]:
        model = counts.loc[model_name]
        for state1, state2 in matches:
            count1, count2 = model.loc[state1].iloc[0], model.loc[state2].iloc[0]
            assert count1 == count2, (
                f"{state1}: {int(count1)}",
                f"{state2}: {int(count2)}",
            )


@pytest.mark.parametrize("example_name", examples.keys())
def test_example(function_tmpdir, example_name):
    if example_name in skip:
        pytest.skip(f"Skipping example {example_name}")
    for model_name in examples[example_name]:
        model_relpath = model_name.rpartition(example_name + "/")[-1]
        model_workspace = function_tmpdir / model_relpath
        models.copy_to(model_workspace, model_name, verbose=True)
        callback = StateCollector()
        run_simulation(dll, model_workspace, callback=callback, verbose=True)
        if model_name in temporary_skip_state_count:
            counts = count_states(callback.states)
            compare_counts(counts)
