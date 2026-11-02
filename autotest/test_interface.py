import shutil
from pathlib import Path
from platform import system
from textwrap import dedent

import numpy as np
import pytest
from modflow_devtools.misc import set_dir

from modflowapi import Callbacks, ModflowApi, run_simulation
from modflowapi.extensions.apiexchange import ApiExchange
from modflowapi.extensions.pakbase import AdvancedPackage, ArrayPackage, ListPackage

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
                raise AssertionError("ApiModel has advanced prior to initialization callback")

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
                raise AssertionError("Solution advanced prior to stress_period_start callback")

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError("Solution advanced prior to timestep_start callback")

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
                raise AssertionError("ApiModel has advanced prior to initialization callback")

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
                raise AssertionError("Solution advanced prior to stress_period_start callback")

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError("Solution advanced prior to timestep_start callback")

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
                raise AssertionError("ApiModel has advanced prior to initialization callback")

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
                raise AssertionError("Solution advanced prior to stress_period_start callback")

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError("Solution advanced prior to timestep_start callback")

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

            assert sim.exchange_names == ["gwf-gwf_1"]

            exchange = sim.get_exchange()
            assert isinstance(exchange, ApiExchange)

            named_exchange = sim.get_exchange("gwf-gwf_1")
            assert named_exchange is exchange

            with pytest.raises(KeyError):
                sim.get_exchange("not_a_real_exchange")

            assert "Exchanges include" in repr(sim)
            assert "gwf-gwf_1" in repr(sim)

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


def test_sfr_input_context_names(function_tmpdir):
    def callback(sim, step):
        if step != Callbacks.timestep_start or sim.kstp != 0:
            return
        model = sim.get_model()
        sfr = model.get_package("sfr_0")
        if sim.kper == 1:
            # the write persists into the next time step
            np.testing.assert_allclose(sfr.packagedata.values["hk"], written["hk"], err_msg="hk write did not persist")
            written["persisted"] = True
            return
        if f"__INPUT__/{model.name}/SFR_0/BEDK" in sim.mf6.get_input_var_names():
            path = f"__INPUT__/{model.name}/SFR_0"
            names = ("BEDK", "MANNING", "UPSTREAM_FRAC")
        else:
            path = f"{model.name}/SFR_0"
            names = ("HK", "ROUGH", "USTRF")
        addrs = [f"{path}/{name}" for name in names]
        for addr in addrs:
            assert addr in sfr._package_var_addrs, f"{addr} not used"

        pd = sfr.packagedata.values
        for column, values in expected.items():
            np.testing.assert_allclose(pd[column], values, err_msg=f"{column} does not match the input")

        pd["hk"] *= 10.0
        sfr.packagedata = pd
        np.testing.assert_allclose(sim.mf6.get_value(addrs[0]), pd["hk"], err_msg="hk is not being properly set")
        written["hk"] = pd["hk"].copy()

    written = {}

    # three reaches in a row of three cells; reach 1 flows to reach 2 and
    # diverts to reach 3
    expected = {"hk": [0.1, 0.2, 0.3], "rough": [0.03, 0.035, 0.04], "ustrf": [1.0, 1.0, 0.0]}
    packagedata = "\n".join(
        f"  {i + 1} 1 1 {i + 1} 100.0 {width} 0.001 {rtp} 1.0 {hk} {rough} {ncon} {ustrf} {ndiv}"
        for i, (width, rtp, hk, rough, ncon, ustrf, ndiv) in enumerate(
            zip(
                [10.0, 10.0, 5.0],
                [9.0, 8.9, 8.9],
                expected["hk"],
                expected["rough"],
                [2, 1, 1],
                expected["ustrf"],
                [1, 0, 0],
            )
        )
    )
    files = {
        "mfsim.nam": """
            BEGIN timing
              TDIS6 sim.tdis
            END timing
            BEGIN models
              gwf6 sfr.nam sfr
            END models
            BEGIN exchanges
            END exchanges
            BEGIN solutiongroup 1
              ims6 sim.ims sfr
            END solutiongroup
            """,
        "sim.tdis": """
            BEGIN dimensions
              NPER 2
            END dimensions
            BEGIN perioddata
              1.0 1 1.0
              1.0 1 1.0
            END perioddata
            """,
        "sim.ims": "",
        "sfr.nam": """
            BEGIN packages
              DIS6 sfr.dis dis
              NPF6 sfr.npf npf
              IC6 sfr.ic ic
              CHD6 sfr.chd chd_0
              SFR6 sfr.sfr sfr_0
            END packages
            """,
        "sfr.dis": """
            BEGIN dimensions
              NLAY 1
              NROW 1
              NCOL 3
            END dimensions
            BEGIN griddata
              delr
                CONSTANT 100.0
              delc
                CONSTANT 100.0
              top
                CONSTANT 10.0
              botm
                CONSTANT 0.0
            END griddata
            """,
        "sfr.npf": """
            BEGIN griddata
              icelltype
                CONSTANT 0
              k
                CONSTANT 10.0
            END griddata
            """,
        "sfr.ic": """
            BEGIN griddata
              strt
                CONSTANT 8.0
            END griddata
            """,
        "sfr.chd": """
            BEGIN dimensions
              MAXBOUND 1
            END dimensions
            BEGIN period 1
              1 1 1 8.0
            END period
            """,
        "sfr.sfr": """
            BEGIN dimensions
              NREACHES 3
            END dimensions
            BEGIN packagedata
            {packagedata}
            END packagedata
            BEGIN connectiondata
              1 -2 -3
              2 1
              3 1
            END connectiondata
            BEGIN diversions
              1 1 3 UPTO
            END diversions
            BEGIN period 1
              1 INFLOW 10.0
              1 DIVERSION 1 2.0
            END period
            """,
    }
    test_pth = function_tmpdir / "sfr_model"
    test_pth.mkdir()
    for name, text in files.items():
        (test_pth / name).write_text(dedent(text).format(packagedata=packagedata))

    run_simulation(so, test_pth, callback)
    assert written.get("persisted"), "hk was not checked in the second stress period"


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
