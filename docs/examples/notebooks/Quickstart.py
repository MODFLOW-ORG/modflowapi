# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # MODFLOW API Quickstart
#
# This notebook presents a quickstart guide to working with the modflowapi package through the extension modules.
# This quickstart guide serves as a roadmap for user development of custom callback functions. For a detailed
# explanation of the `modflowapi.extensions` objects that are accessible through a callback function, see the
# notebook `MODFLOW-API extensions objects.ipynb`.

# +
from pathlib import Path

import modflowapi
from modflowapi import Callbacks

# -

# Define paths to the modflow6 api shared library

# +
sim_ws = Path("../data/dis_model")

dll = Path("./libmf6")


# -

# First we create a callback function for adjusting model data.
#
# The callback function allows users to wrap function that updates the modflow model at different steps.
# The `modflowapi.Callbacks` object allows users to find the particular solution step that they are
# currently in. `modflowapi.Callbacks` includes:
#
#    - `Callbacks.initialize`: the initialize callback sends loaded simulation data back to the user to
#       make adjustments before the model begins solving. This callback only occurs once at the beginning
#       of the MODFLOW6 simulation.
#    - `Callbacks.stress_period_start`: the stress_period_start callback sends simulation data for each
#       solution group to the user to make adjustments to stress packages at the beginning of each stress
#       period.
#    - `Callbacks.stress_period_end`: the stress_period_end callback sends simulation data for each solution
#       group to the user at the end of each stress period. This can be useful for writing custom output
#       and coupling models.
#    - `Callbacks.timestep_start`: the timestep_start callback sends simulation data for each solution group
#       to the user to make adjustments to stress packages at the beginning of each timestep.
#    - `Callbacks.timestep_end`: the timestep_end callback sends simulation data for each solution group to
#       the user at the end of each timestep. This can be useful for writing custom output and coupling models.
#    - `Callbacks.iteration_start`: the iteration_start callback sends simulation data for each solution group
#       to the user to make adjustments to stress packages at the beginning of each outer solution iteration.
#    - `Callbacks.iteration_end`: the iteration_end callback sends simulation data for each solution group to
#       the user to make adjustments to stress packages and check values of stress packages at the end of each
#       outer solution iteration.
#
# The user can use any of these callbacks within their callback function.


def callback_function(sim, callback_step):
    """
    A demonstration function that dynamically adjusts recharge
    and pumping in a modflow-6 model through the MODFLOW-API

    Parameters
    ----------
    sim : modflowapi.ApiSimulation
        A simulation object for the solution group that is
        currently being solved
    step : enumeration
        modflowapi.Callbacks enumeration object that indicates
        the part of the solution modflow is currently in.
    """
    ml = sim.test_model
    if callback_step == Callbacks.initialize:
        print(sim.models)

    if callback_step == Callbacks.stress_period_start:
        # adjust recharge for stress periods 7 through 12
        if sim.kper <= 6:
            rcha = ml.rcha_0
            spd = rcha.stress_period_data
            print(f"updating recharge: stress_period={ml.kper}")
            spd["recharge"] += 0.40 * sim.kper

    if callback_step == Callbacks.timestep_start:
        print(f"updating wel flux: stress_period={ml.kper}, timestep={ml.kstp}")
        ml.wel.stress_period_data["q"] -= ml.kstp * 1.5

    if callback_step == Callbacks.iteration_start:
        # we can implement complex solutions to boundary conditions here!
        pass


# The callback function is then passed to `modflowapi.run_simulation`

modflowapi.run_simulation(dll, sim_ws, callback_function, verbose=False)
