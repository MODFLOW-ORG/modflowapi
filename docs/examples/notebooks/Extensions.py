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

# # Interacting with MODFLOW-API Interface objects
#
# The purpose of this notebook is to show the MODFLOW-API interface objects and introduce the user to the data types and how to interact with the objects. 
#
# **Note**: This notebook shows how to run a model using the modflow-api at the end of the notebook. However, the majority of the notebook is an illustration of how to access and work with the data types that are returned to a user defined callback function. 

# +
import platform
from pathlib import Path

import modflowapi
from modflowapi.extensions import ApiSimulation
# -

# Define the paths to the model and the Modflow shared library

# +
sim_ws = Path("../data/dis_model")
dll = "./libmf6"
if platform.system().lower() == "windows":
    ext = ".dll"
elif platform.system().lower() == "linux":
    ext = ".so"
else:
    ext = ".dylib"

dll = Path(dll + ext)
# -

# #### Initializing the API model object
#
# The modflow api allows users to initialize an object that can be used to interact with the model. This processes is done automatically with the `modflowapi.run_model` function call. We're going to initialize an object outside of that call as a demonstration of the interface data objects

# +
mf6 = modflowapi.ModflowApi(dll, working_directory=sim_ws)
mf6.initialize()

# let's advance the model to the first timestep
dt = mf6.get_time_step()
mf6.prepare_time_step(dt)
# -

# ## The `ApiSimulation` object 
#
# The `ApiSimulation` object is the top level container for the modflowapi interface classes. This container holds methods and other objects that allow the user to access boundary condition pointer data without assembling the specific memory addresses of the modflow data. 
#
# Let's take a look at the `ApiSimulation` object

sim = ApiSimulation.load(mf6)
sim

# The simulation object allows the user to access models by name and has a number of handy properties and contains simulation level packages such as `sln`, `tdis`, `ats`, and `exchanges`

mnames = sim.model_names
mnames

kstp, kper = sim.kstp, sim.kper
kstp, kper

nstp = sim.nstp
nstp

ims = sim.sln
ims

ims.dvclose

# ## The `ApiModel` object
#
# `ApiModel` objects are accessed from the `ApiSimulation` object and are a container for packages. These objects allow the user to view which packages are available and access those packages. 
#
# The following cells show the main attributes and functions available on the `ApiModel` object

# Model objects are accessible through the `get_model` function and as attributes on the sim object

model = sim.get_model("test_model")
model

# approach 2
model = sim.test_model
model

# There are also a number of other functions available including the following:

model.shape

model.size

model.solution_id

# A list of all package names that are accessible is also available

model.package_names

# ## The `ApiPackage` object(s)
#
# Each package is contained in `ApiPackage` container. There are three types depending on the input data. We'll access and take a look at each of the types of `ApiPackage` containers.

# Packages can be accessed from the `Model` object using `get_package()` or by attribute

# example 1: get a package using get_package
rch = model.get_package("rcha_0")
rch

# example 2: get a package by package name attribute
wel = model.wel_0
wel

# example 3: get all packages based on a package type
rch_pkgs = model.rch
rch_pkgs

# ### `ListPackage` objects
#
# `ListPackage` objects are the primary object type of stress period data. The exception to this rule is the advanced packages which will be discussed later. 
#
# `ListPackage` objects allow users to access stress period data as a numpy recarray or as a pandas dataframe.

recarray = rch.stress_period_data.values
recarray[0:10]

df = rch.stress_period_data.dataframe
df.head()

# ### Updating values for `ListPackage` based data
#
# There are multiple ways to update values for `ListPackage` based data. The `.values` and `.dataframe` attributes can be used, or the object can be directly indexed if the user knows the underlying data. Here are some examples

# +
recarray["recharge"][0] *= 100
rch.stress_period_data.values = recarray

# show that values have been updated
recarray = rch.stress_period_data.values
recarray[0:5]

# +
df = rch.stress_period_data.dataframe
df.loc[1, "recharge"] = 10000
rch.stress_period_data.dataframe = df

# show that values have been updated
df = rch.stress_period_data.dataframe
df.head()
# -

# #### Interfacing directly with the `.stress_period_data` attribute
#
# The `.stress_period_data` attribute returns a container class that interacts with the internal modflow pointers. The data can be adjusted by interacting with `.stress_period_data` in the same fashion as changing data in a numpy recarray. 

rch.stress_period_data["recharge"] *= 100

df = rch.stress_period_data.dataframe
df.head()

# #### Adding or removing a boundary condition
# In list packages the user can add and remove specific boundary conditions. Note: if a user adds a boundary condition, such as another well during a stress period, the total number of wells cannot be greater than the wel package's `maxbound` variable. Here's an example

wel = model.wel
maxbound = wel.maxbound
nbound = wel.nbound
print(f"{nbound=}", f"{maxbound=}")

# For the current stress period there are two active wells `nbound=2`, but there can be up to ten `maxbound=10`.

recarray = wel.stress_period_data.values
recarray

recarray.resize((nbound + 1,), refcheck=False)
recarray[-1] = ((0, 1, 5), -20.0, 0, 1)
recarray

wel.stress_period_data.values = recarray
nbound = wel.nbound
f"{nbound=}"

wel.stress_period_data.dataframe

# ### `ArrayPackage` objects
#
# The `ArrayPackage` class is used as a container for packages such as `DIS`, `NPF`, and `IC` that do not contain any sort of stress period data. These packages are used primarily to define model connectivity, initial conditions, and hydraulic parameters of the basin. 

npf = model.npf
npf

# For an `ArrayPackage` type object, variable names can be viewed by calling the `.variable_names` property

npf.variable_names

# ### Updating values for `ArrayPackage` objects
#
# Two methods are available for accessing and updating data in `ArrayPackage` objects. `get_array()` and `set_array()` methods can be used to get and set data. Arrays can also be accessed as attributes on the object.

# Using `get_array()` and `set_array()`

hk = npf.get_array("k11")
hk

hk[0, 0:5, 0:5] = 50
npf.set_array("k11", hk)

# confirm that the data has been updated
hk = npf.get_array("k11")
hk

# Getting and setting data by attribute

# needs an update for inplace operations....
npf.k33[0, 0:5, 0:5] = 5

# confirm that the data has been updated
npf.k33.values

# ## Accessing "advanced variables"
#
# Advanced variables in this context are variables that would not normally need to be accessed by the user, and in many cases changes to these variables would cause the Modflow simulation to do unexpected things. 

# For each package object a list of advanced variables can be returned by calling the `advanced_vars` attribute

wel = model.wel_0
wel.advanced_vars

# The user can access and change these values, _at their own risk_, using the `.get_advanced_var()` and `.set_advanced_var()` methods. Data is returned to the user in the internal modflowapi structure. 

wel.get_advanced_var("ibcnum")

# ### Advanced Packages
#
# Certain packages only support accessing data through the `.get_advanced_var()` and `.set_advanced_var()` methods. These packages, are sometimes referred to as "advanced packages" and include: BUY, CSUB, GNC, HFB, MAW, MVR, SFR, and UZF. 

# -------

# Let's close the existing modflowapi shared library object and look at an example of how this is all used in practice

mf6.finalize()

# # Putting it all together and running a modflowapi simulation
#
# To run a simulation using the built in modflowapi runner the user needs to create a function that will receive callbacks at different steps in the simulation run. For the remainder of this notebook, we'll show how to create a callback function and use it with the `modflowapi.run_simulation()` method.

# ## Create a callback function for adjusting model data
#
# The callback function allows users to wrap function that updates the modflow model at different steps. The `modflowapi.Callbacks` object allows users to find the particular solution step that they are currently in. `modflowapi.Callbacks` includes:
#
#    - `Callbacks.initialize`: the initialize callback sends loaded simulation data back to the user to make adjustments before the model begins solving. This callback only occurs once at the beginning of the MODFLOW6 simulation
#    - `Callbacks.stress_period_start`: the stress_period_start callback sends simulation data for each solution group to the user to make adjustments to stress packages at the beginning of each stress period.
#    - `Callbacks.stress_period_end`: the stress_period_end callback sends simulation data for each solution group to the user at the end of each stress period. This can be useful for writing custom output and coupling models
#    - `Callbacks.timestep_start`: the timestep_start callback sends simulation data for each solution group to the user to make adjustments to stress packages at the beginning of each timestep.
#    - `Callbacks.timestep_end`: the timestep_end callback sends simulation data for each solution group to the user at the end of each timestep. This can be useful for writing custom output and coupling models
#    - `Callbacks.iteration_start`: the iteration_start callback sends simulation data for each solution group to the user to make adjustments to stress packages at the beginning of each outer solution iteration.
#    - `Callbacks.iteration_end`: the iteration_end callback sends simulation data for each solution group to the user to make adjustments to stress packages and check values of stress packages at the end of each outer solution iteration.
#    - `Callbacks.finalize`: the finalize callback is useful for finalizing models coupled with the modflowapi.
#    
# The user can use any or all of these callbacks within their callback function

from modflowapi import Callbacks


def callback_function(sim, callback_step):
    """
    A demonstration function that dynamically adjusts recharge
    and pumping in a modflow-6 model through the MODFLOW-API

    Parameters
    ----------
    sim : modflowapi.Simulation
        A simulation object for the solution group that is
        currently being solved
    callback_step : enumeration
        modflowapi.Callbacks enumeration object that indicates
        the part of the solution modflow is currently in.
    """
    ml = sim.test_model
    if callback_step == Callbacks.initialize:
        print(sim.models)

    if callback_step == Callbacks.stress_period_start:
        # adjust recharge for stress periods 1 through 7
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


