from enum import Enum

from .. import ModflowApi
from .apisimulation import ApiSimulation


class Callbacks(Enum):
    initialize = 0
    stress_period_start = 1
    stress_period_end = 2
    timestep_start = 3
    timestep_end = 4
    iteration_start = 5
    iteration_end = 6
    finalize = 7


def run_simulation(dll, sim_path, callback, verbose=False, _develop=False):
    """
    Method to run a Modflow simulation using the MODFLOW-API
    with a callback function

    Parameters
    ----------
    dll : str
        path to the Modflow6 shared object
    sim_path : str
        path to the Modflow6 simulation
    callback : method
        user defined method that intercepts the simulation
        progress and allows for input variable adjustments on the fly
    verbose : bool
        flag for verbose output from the simulation runner
    _develop : bool
        flag that dumps a list of all mf6 api variable addresses to text
        file named "var_list.txt". This is primarily used for extensions
        development purposes and bug fixes within the modflowapi python
        package.
    """
    mf6 = ModflowApi(dll, working_directory=sim_path)

    if verbose:
        version = mf6.get_version()
        print(f"MODFLOW-6 API Version {version}")
        print("Initializing MODFLOW-6 simulation")

    mf6.initialize()
    sim = ApiSimulation.load(mf6)

    if _develop:
        with open("var_list.txt", "w") as foo:
            for name in mf6.get_input_var_names():
                foo.write(f"{name}\n")

    callback(sim, Callbacks.initialize)

    has_converged = False
    current_time = mf6.get_current_time()
    end_time = mf6.get_end_time()
    kperold = [0 for _ in range(sim.subcomponent_count)]

    while current_time < end_time:
        dt = mf6.get_time_step()
        mf6.prepare_time_step(dt)

        if verbose:
            print(f"Solving: Stress Period {sim.kper + 1}; Timestep {sim.kstp + 1}")

        for sol_id, slnobj in sorted(sim.solutions.items()):
            models = {}
            maxiter = slnobj.mxiter
            solution = {sol_id: slnobj}
            for model in sim.models:
                if sol_id == model.solution_id:
                    models[model.name.lower()] = model

            sim_grp = ApiSimulation(
                mf6, models, solution, sim._exchanges, sim.tdis, sim.ats
            )
            mf6.prepare_solve(sol_id)
            if sim.kper != kperold[sol_id - 1]:
                callback(sim_grp, Callbacks.stress_period_start)
                kperold[sol_id - 1] += 1
            elif current_time == 0:
                callback(sim_grp, Callbacks.stress_period_start)

            kiter = 0
            callback(sim_grp, Callbacks.timestep_start)

            if sim_grp.ats_period[0]:
                mindt = sim_grp.ats_period[-1]
                while sim_grp.delt > mindt:
                    sim_grp.iteration = kiter
                    callback(sim_grp, Callbacks.iteration_start)
                    has_converged = mf6.solve(sol_id)
                    callback(sim_grp, Callbacks.iteration_end)
                    kiter += 1
                    if has_converged and sim_grp.allow_convergence:
                        break

            else:
                while kiter < maxiter:
                    sim_grp.iteration = kiter
                    callback(sim_grp, Callbacks.iteration_start)
                    has_converged = mf6.solve(sol_id)
                    callback(sim_grp, Callbacks.iteration_end)
                    kiter += 1
                    if has_converged and sim_grp.allow_convergence:
                        break

            callback(sim_grp, Callbacks.timestep_end)
            mf6.finalize_solve(sol_id)

        mf6.finalize_time_step()
        current_time = mf6.get_current_time()

        if not has_converged:
            print(f"Simulation group: {sim_grp} DID NOT CONVERGE")

        if sim_grp.nstp == sim_grp.kstp + 1:
            callback(sim_grp, Callbacks.stress_period_end)

    try:
        callback(sim, Callbacks.finalize)
        mf6.finalize()
    except Exception:
        raise RuntimeError("MF6 simulation failed, check listing file")

    print("NORMAL TERMINATION OF SIMULATION")
