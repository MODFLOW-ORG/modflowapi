import numpy as np

from .data import ListInput
from .pakbase import AdvancedPackage


class SfrPakage(AdvancedPackage):
    """
    Container for SFR and SFR like packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "SFR"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        super().__init__(model, pkg_type, pkg_name, sim_package)

        self._diversion_var_arrs = []
        self._set_advanced_variable_addrs("diversions", "_diversion_var_addrs")
        self._diversion_vars = ListInput(self, self._diversion_var_arrs, spd=False)

    @property
    def diversions(self):
        return self._diversion_vars

    @diversions.setter
    def diversions(self, recarray):
        """
        Setter object to update the diversions data

        """
        if isinstance(recarray, np.recarray):
            self._diversion_vars.values = recarray
        elif isinstance(recarray, ListInput):
            self._diversion_vars.values = recarray.values
        elif recarray is None:
            self._diversion_vars.values = recarray
        else:
            raise TypeError(f"{type(recarray)} is not a supported diversions type")


class LakPackage(AdvancedPackage):
    """
    Container for LAK and LAK like packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "LAK"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        super().__init__(model, pkg_type, pkg_name, sim_package)


class MawPackage(AdvancedPackage):
    """
    Container for MAW and MAW like packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "MAW"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        super().__init__(model, pkg_type, pkg_name, sim_package)


class UzfPackage(AdvancedPackage):
    """
    Container for UZF and UZF like packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "UZF"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        super().__init__(model, pkg_type, pkg_name, sim_package)


class CsubPackage:
    """
    Container for CSUB packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "CSUB"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(
        self,
    ):
        self.x = None


class MvrPackage:
    """
    Container for MVR packages

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type. Ex. "MVR"
    pkg_name : str
        package name (in the mf6 variables)
    sim_package : bool
        boolean flag for simulation level packages. Ex. TDIS, IMS
    """

    def __init__(
        self,
    ):
        self.x = None
