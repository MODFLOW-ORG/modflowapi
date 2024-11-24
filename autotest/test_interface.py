import shutil
from pathlib import Path
from platform import system

import numpy as np
import pytest
from modflow_devtools.misc import set_dir

from modflowapi import Callbacks, ModflowApi, run_simulation
from modflowapi.extensions.pakbase import AdvancedPackage, ArrayPackage, ListPackage

data_pth = Path("../examples/data")
pytestmark = pytest.mark.extensions
os = system()
so = "libmf6" + (
    ".so"
    if os == "Linux"
    else ".dylib"
    if os == "Darwin"
    else ".dll"
    if os == "Windows"
    else None
)
if so is None:
    pytest.skip("Unsupported operating system", allow_module_level=True)


@pytest.mark.parametrize("use_str", [True, False])
def test_ctor_finds_libmf6_by_name(use_str):
    ModflowApi(so if use_str else Path(so))


@pytest.mark.parametrize("use_str", [True, False])
def test_ctor_finds_libmf6_by_relpath(function_tmpdir, use_str):
    shutil.copy(so, function_tmpdir)
    inner = function_tmpdir / "inner"
    inner.mkdir()
    with set_dir(inner):
        so_path = f"../{so}"
        ModflowApi(so_path if use_str else Path(so_path))


@pytest.mark.parametrize("use_str", [True, False])
def test_ctor_finds_libmf6_by_abspath(function_tmpdir, use_str):
    shutil.copy(so, function_tmpdir)
    so_path = function_tmpdir / so
    ModflowApi(str(so_path) if use_str else so_path)


def test_dis_model(function_tmpdir):
    def callback(sim, step):
        """
        Callback function

        Parameters
        ----------
        sim : modflowapi.ApiSimulation object
        step : Enum
            step is the simulation step defined by Callbacks
        """
        if step == Callbacks.initialize:
            if len(sim.models) != 1:
                raise AssertionError("Invalid number of models")

            model = sim.test_model
            if len(model.package_names) != 16:
                raise AssertionError("Invalid number of packages")

            if len(model.package_types) != 15:
                raise AssertionError("Invalid number of package types")

            if model.shape != (1, 10, 10):
                raise AssertionError("ApiModel shape is incorrect")

            if model.size != 100:
                raise AssertionError("ApiModel size is incorrect")

            if (model.kper, model.kstp) != (-1, -1):
                raise AssertionError(
                    "ApiModel has advanced prior to initialization callback"
                )

            dis = model.dis
            if not isinstance(dis, ArrayPackage):
                raise TypeError("DIS package has incorrect base class type")

            wel = model.wel
            if not isinstance(wel, ListPackage):
                raise TypeError("WEL package has incorrect base class type")

            gnc = model.gnc
            if not isinstance(gnc, AdvancedPackage):
                raise TypeError("GNC package has incorrect base class type")

            rch = model.rch
            if len(rch) != 2:
                raise AssertionError("ApiModel object not returning multiple packages")

            idomain = dis.idomain.values
            if not isinstance(idomain, np.ndarray):
                raise TypeError("Expecting a numpy array for idomain")

        elif step == Callbacks.stress_period_start:
            if sim.kstp != 0:
                raise AssertionError(
                    "Solution advanced prior to stress_period_start callback"
                )

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError(
                    "Solution advanced prior to timestep_start callback"
                )

            factor = ((1 + sim.kstp) / sim.nstp) * 0.5
            spd = sim.test_model.wel.stress_period_data.values
            sim.test_model.wel.stress_period_data["q"] *= factor

            spd2 = sim.test_model.wel.stress_period_data.values
            if not np.allclose((spd["q"] * factor), spd2["q"]):
                raise AssertionError("Pointer not being set properly")

            if sim.kper >= 3 and sim.kstp == 0:
                spd = sim.test_model.wel.stress_period_data.values
                nbound0 = sim.test_model.wel.nbound
                spd.resize((nbound0 + 1), refcheck=False)
                spd[-1] = ((0, 1, 5), -20, 1.0, 2.0)
                sim.test_model.wel.stress_period_data.values = spd
                if sim.test_model.wel.nbound != nbound0 + 1:
                    raise AssertionError("Resize routine not properly working")

    name = "dis_model"
    sim_pth = data_pth / name
    test_pth = function_tmpdir / name
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    try:
        run_simulation(so, test_pth, callback)
    except Exception as e:
        raise Exception(e)


def test_disv_model(function_tmpdir):
    def callback(sim, step):
        """
        Callback function

        Parameters
        ----------
        sim : modflowapi.ApiSimulation object
        step : Enum
            step is the simulation step defined by Callbacks
        """
        if step == Callbacks.initialize:
            if len(sim.models) != 1:
                raise AssertionError("Invalid number of models")

            model = sim.gwf_1
            if len(model.package_names) != 12:
                raise AssertionError("Invalid number of packages")

            if len(model.package_types) != 11:
                raise AssertionError("Invalid number of package types")

            if model.shape != (4, 200):
                raise AssertionError("ApiModel shape is incorrect")

            if model.size != 800:
                raise AssertionError("ApiModel size is incorrect")

            if (model.kper, model.kstp) != (-1, -1):
                raise AssertionError(
                    "ApiModel has advanced prior to initialization callback"
                )

            dis = model.dis
            if not isinstance(dis, ArrayPackage):
                raise TypeError("DIS package has incorrect base class type")

            chd = model.chd_left
            if not isinstance(chd, ListPackage):
                raise TypeError("CHD package has incorrect base class type")

            hfb = model.hfb
            if not isinstance(hfb, AdvancedPackage):
                raise TypeError("HFB package has incorrect base class type")

            chd = model.chd
            if len(chd) != 2:
                raise AssertionError("ApiModel object not returning multiple packages")

            top = dis.top.values
            if not isinstance(top, np.ndarray):
                raise TypeError("Expecting a numpy array for top")

        elif step == Callbacks.stress_period_start:
            if sim.kstp != 0:
                raise AssertionError(
                    "Solution advanced prior to stress_period_start callback"
                )

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError(
                    "Solution advanced prior to timestep_start callback"
                )

            factor = 0.75
            spd = sim.gwf_1.chd_left.stress_period_data.values
            sim.gwf_1.chd_left.stress_period_data["head"] *= factor

            spd2 = sim.gwf_1.chd_left.stress_period_data.values
            if not np.allclose((spd["head"] * factor), spd2["head"]):
                raise AssertionError("Pointer not being set properly")

    name = "disv_model"
    sim_pth = data_pth / name
    test_pth = function_tmpdir / name
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    try:
        run_simulation(so, test_pth, callback)
    except Exception as e:
        raise Exception(e)


def test_disu_model(function_tmpdir):
    def callback(sim, step):
        """
        Callback function

        Parameters
        ----------
        sim : modflowapi.ApiSimulation object
        step : Enum
            step is the simulation step defined by Callbacks
        """
        if step == Callbacks.initialize:
            if len(sim.models) != 1:
                raise AssertionError("Invalid number of models")

            model = sim.gwf_1
            if len(model.package_names) != 12:
                raise AssertionError("Invalid number of packages")

            if len(model.package_types) != 12:
                raise AssertionError("Invalid number of package types")

            if model.shape != (121,):
                raise AssertionError("ApiModel shape is incorrect")

            if model.size != 121:
                raise AssertionError("ApiModel size is incorrect")

            if (model.kper, model.kstp) != (-1, -1):
                raise AssertionError(
                    "ApiModel has advanced prior to initialization callback"
                )

            dis = model.dis
            if not isinstance(dis, ArrayPackage):
                raise TypeError("DIS package has incorrect base class type")

            rch = model.rch
            if not isinstance(rch, ListPackage):
                raise TypeError("RCH package has incorrect base class type")

            mvr = model.mvr
            if not isinstance(mvr, AdvancedPackage):
                raise TypeError("MVR package has incorrect base class type")

            top = dis.top.values
            if not isinstance(top, np.ndarray):
                raise TypeError("Expecting a numpy array for top")

        elif step == Callbacks.stress_period_start:
            if sim.kstp != 0:
                raise AssertionError(
                    "Solution advanced prior to stress_period_start callback"
                )

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError(
                    "Solution advanced prior to timestep_start callback"
                )

            factor = 1.75
            spd = sim.gwf_1.rch.stress_period_data.values
            sim.gwf_1.rch.stress_period_data["recharge"] += factor

            spd2 = sim.gwf_1.rch.stress_period_data.values
            if not np.allclose((spd["recharge"] + factor), spd2["recharge"]):
                raise AssertionError("Pointer not being set properly")

    name = "disu_model"
    sim_pth = data_pth / name
    test_pth = function_tmpdir / name
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    try:
        run_simulation(so, test_pth, callback)
    except Exception as e:
        raise Exception(e)


def test_two_models(function_tmpdir):
    def callback(sim, step):
        """
        Callback function

        Parameters
        ----------
        sim : modflowapi.ApiSimulation object
        step : Enum
            step is the simulation step defined by Callbacks
        """
        if step == Callbacks.initialize:
            if len(sim.models) != 2:
                raise AssertionError("Invalid number of models")

    name = "two_models"
    sim_pth = data_pth / name
    test_pth = function_tmpdir / name
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    try:
        run_simulation(so, test_pth, callback)
    except Exception as e:
        raise Exception(e)


def test_ats_model(function_tmpdir):
    def callback(sim, step):
        if step == Callbacks.stress_period_start:
            if sim.kper == 0 and sim.kstp == 0:
                delt0 = sim.delt

        if step == Callbacks.timestep_start:
            if sim.kstp == 1:
                if delt0 == sim.delt:
                    raise AssertionError("ATS routines not reducing timestep length")

        name = "ats0"
        sim_pth = data_pth / name
        test_pth = function_tmpdir / name
        shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

        try:
            run_simulation(so, test_pth, callback)
        except Exception as e:
            raise Exception(e)


def test_rhs_hcof_advanced(function_tmpdir):
    def callback(sim, step):
        model = sim.test_model
        if step == Callbacks.timestep_start:
            wel = model.wel
            rhs = wel.rhs
            rhs[0:3] = [-150, -100, -50]
            wel.rhs = rhs

            rhs2 = wel.get_advanced_var("rhs")
            np.testing.assert_allclose(
                rhs, rhs2, err_msg="rhs variable not being properly set"
            )

            hcof = wel.hcof
            hcof[0:3] = np.abs(rhs)[0:3] / 2

            wel.hcof = hcof

            hcof2 = wel.get_advanced_var("hcof")

            np.testing.assert_allclose(
                hcof, hcof2, err_msg="hcof is not being properly set"
            )

            rhs *= 1.2
            wel.set_advanced_var("rhs", rhs)
            rhs3 = wel.rhs

            np.testing.assert_allclose(
                rhs, rhs3, err_msg="set advanced var method not working properly"
            )

            npf = model.npf

            try:
                npf.hcof = [1, 2, 3]
                raise AssertionError("hcof setter is not reporting errors")
            except Exception:
                pass

            try:
                npf.rhs = [1, 2, 3]
                raise AssertionError("rhs setter is not reporting errors")
            except Exception:
                pass

    name = "dis_model"
    sim_pth = data_pth / name
    test_pth = function_tmpdir / name
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    try:
        run_simulation(so, test_pth, callback)
    except Exception as e:
        raise Exception(e)
