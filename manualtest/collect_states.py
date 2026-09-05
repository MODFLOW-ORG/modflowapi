"""Test helper for sequence of model states."""

from collections import defaultdict

import pandas as pd

import modflowapi


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


def run(dll, sim_path):
    """Run a model and collect its sat sequence."""
    callback = StateCollector()
    modflowapi.run_simulation(dll=dll, sim_path=sim_path, callback=callback)
    return callback.states


def visualize_states(states, limit=None):
    """
    Visualize the state sequence by model.

    This prints one tree-like sequence of state names per model.
    Different state groups have different indentations to visualize the
    flow.
    """
    indents = {
        "initialize": 0,
        "finalize": 0,
        "stress_period_start": 4,
        "stress_period_end": 4,
        "timestep_start": 8,
        "timestep_end": 8,
        "iteration_start": 12,
        "iteration_end": 12,
    }
    models = defaultdict(list)
    for model_name, state in states:
        models[model_name].append(state)
    for model_name, model_states in models.items():
        print(model_name)
        for count, state in enumerate(model_states):
            if limit and limit == count:
                break
            print(" " * indents[state], state)


def count_states(states):
    """
    Count states per model.

    The numbers of `start_state` and `end_state` should match.
    """
    states = pd.DataFrame(states, columns=["model", "state"])
    counts = states.groupby(["model", "state"])[["state"]].agg("count")
    counts.columns = ["counts"]
    return counts
