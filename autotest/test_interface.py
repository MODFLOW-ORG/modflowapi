import shutil
from pathlib import Path
from platform import system

import numpy as np
import pytest
from modflow_devtools.misc import set_dir

from modflowapi import Callbacks, ModflowApi, run_simulation
from modflowapi.extensions.apiexchange import ApiExchange
from modflowapi.extensions.pakbase import AdvancedPackage, ArrayPackage, ListPackage, Package

data_pth = Path("../docs/examples/data")
pytestmark = pytest.mark.extensions
os = system()
so = "libmf6" + (".so" if os == "Linux" else ".dylib" if os == "Darwin" else ".dll" if os == "Windows" else None)
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
            assert len(sim.models) == 1, "Invalid number of models"

            model = sim.test_model
            assert len(model.package_names) == 16, "Invalid number of packages"
            assert len(model.package_types) == 15, "Invalid number of package types"
            assert model.shape == (1, 10, 10), "Model grid shape is incorrect"
            assert model.size == 100, "Model grid size is incorrect"
            assert (model.kper, model.kstp) == (-1, -1), "Model advanced prior to initialization callback"

            dis = model.dis
            assert "idomain" in dis.variable_names
            assert isinstance(dis, ArrayPackage)

            wel = model.wel
            assert wel.stress_period_data
            assert isinstance(wel, ListPackage)

            gnc = model.gnc
            assert isinstance(gnc, Package)
            assert isinstance(gnc, AdvancedPackage)

            rch = model.rch
            assert len(rch) == 2, "Model multi-packages failed"

            idomain = dis.idomain.values
            assert isinstance(idomain, np.ndarray), "Expecting a numpy array for idomain"

        elif step == Callbacks.stress_period_start:
            assert sim.kstp == 0, "Solution advanced prior to stress_period_start callback"

        elif step == Callbacks.timestep_start:
            assert sim.iteration == -1, "Solution advanced prior to timestep_start callback"

            factor = ((1 + sim.kstp) / sim.nstp) * 0.5
            spd = sim.test_model.wel.stress_period_data.values
            sim.test_model.wel.stress_period_data["q"] *= factor

            spd2 = sim.test_model.wel.stress_period_data.values
            assert np.allclose((spd["q"] * factor), spd2["q"]), "Pointer not being set properly"

            if sim.kper >= 3 and sim.kstp == 0:
                spd = sim.test_model.wel.stress_period_data.values
                nbound0 = sim.test_model.wel.nbound
                spd.resize((nbound0 + 1), refcheck=False)
                spd[-1] = ((0, 1, 5), -20, 1.0, 2.0)
                sim.test_model.wel.stress_period_data.values = spd
                assert sim.test_model.wel.nbound == nbound0 + 1, "Resize routine not properly working"

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
            assert len(sim.models) == 1, "Invalid number of models"

            model = sim.gwf_1
            assert len(model.package_names) == 12, "Invalid number of packages"
            assert len(model.package_types) == 11, "Invalid number of package types"
            assert model.shape == (4, 200), "Model grid shape is incorrect"
            assert model.size == 800, "Model grid size is incorrect"
            assert (model.kper, model.kstp) == (-1, -1), "Model advanced prior to initialization callback"

            dis = model.dis
            assert "idomain" in dis.variable_names
            assert isinstance(dis, ArrayPackage)

            chd = model.chd_left
            assert chd.stress_period_data
            assert isinstance(chd, ListPackage)

            hfb = model.hfb
            assert isinstance(hfb, Package)
            assert isinstance(hfb, AdvancedPackage)

            chd = model.chd
            assert len(chd) == 2, "Model multi-packages failed"

            top = dis.top.values
            assert isinstance(top, np.ndarray), "Expecting a numpy array for top"

        elif step == Callbacks.stress_period_start:
            assert sim.kstp == 0, "Solution advanced prior to stress_period_start callback"

        elif step == Callbacks.timestep_start:
            assert sim.iteration == -1, "Solution advanced prior to timestep_start callback"

            factor = 0.75
            spd = sim.gwf_1.chd_left.stress_period_data.values
            sim.gwf_1.chd_left.stress_period_data["head"] *= factor

            spd2 = sim.gwf_1.chd_left.stress_period_data.values
            assert np.allclose((spd["head"] * factor), spd2["head"]), "Pointer not being set properly"

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
            assert len(sim.models) == 1, "Invalid number of models"

            model = sim.gwf_1
            assert len(model.package_names) == 12, "Invalid number of packages"
            assert len(model.package_types) == 12, "Invalid number of package types"
            assert model.shape == (121,), "Model grid shape is incorrect"
            assert model.size == 121, "Model grid size is incorrect"
            assert (model.kper, model.kstp) == (-1, -1), "Model advanced prior to initialization callback"

            dis = model.dis
            assert "idomain" in dis.variable_names
            assert isinstance(dis, ArrayPackage)

            rch = model.rch
            assert rch.stress_period_data
            assert isinstance(rch, ListPackage)

            mvr = model.mvr
            assert isinstance(mvr, Package)
            assert isinstance(mvr, AdvancedPackage)

            top = dis.top.values
            assert isinstance(top, np.ndarray), "Expecting a numpy array for top"

        elif step == Callbacks.stress_period_start:
            assert sim.kstp == 0, "Solution advanced prior to stress_period_start callback"

        elif step == Callbacks.timestep_start:
            assert sim.iteration == -1, "Solution advanced prior to timestep_start callback"

            factor = 1.75
            spd = sim.gwf_1.rch.stress_period_data.values
            sim.gwf_1.rch.stress_period_data["recharge"] += factor

            spd2 = sim.gwf_1.rch.stress_period_data.values
            assert np.allclose((spd["recharge"] + factor), spd2["recharge"]), "Pointer not being set properly"

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
            assert len(sim.models) == 2, "Invalid number of models"

            assert sim.exchange_names == ["gwf-gwf_1"]

            exchange = sim.get_exchange()
            assert isinstance(exchange, ApiExchange)

            named_exchange = sim.get_exchange("gwf-gwf_1")
            assert named_exchange is exchange

            with pytest.raises(KeyError):
                sim.get_exchange("not_a_real_exchange")

            assert "Exchanges include" in repr(sim)
            assert "gwf-gwf_1" in repr(sim)

            gwf_gwf = exchange.get_package(sim.exchange_names[0])
            assert isinstance(gwf_gwf, ListPackage)

            gnc = exchange.get_package("gnc")
            assert isinstance(gnc, AdvancedPackage)

            mvr = exchange.get_package("mvr")
            assert isinstance(mvr, AdvancedPackage)

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
                assert delt0 != sim.delt, "ATS routines not reducing timestep length"

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
            np.testing.assert_allclose(rhs, rhs2, err_msg="rhs variable not being properly set")

            hcof = wel.hcof
            hcof[0:3] = np.abs(rhs)[0:3] / 2

            wel.hcof = hcof

            hcof2 = wel.get_advanced_var("hcof")

            np.testing.assert_allclose(hcof, hcof2, err_msg="hcof is not being properly set")

            rhs *= 1.2
            wel.set_advanced_var("rhs", rhs)
            rhs3 = wel.rhs

            np.testing.assert_allclose(rhs, rhs3, err_msg="set advanced var method not working properly")

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
