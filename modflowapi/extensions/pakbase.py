import numpy as np

from .data import AdvancedInput, ArrayVar, ListVar, ScalarVar
from .datamodel import adv_pkgvars, pkgvars

_BASE_ATTRS = frozenset({"model", "pkg_name", "pkg_type"})
_ADV_BLOCK_NAMES = frozenset({"packagedata", "perioddata"})


class Package:
    """
    Package object for MODFLOW 6 API packages.

    Parameters
    ----------
    model : ApiModel
        modflowapi model object
    pkg_type : str
        package type name, e.g. 'wel'
    pkg_name : str
        package name in the MF6 variables, e.g. 'wel_0'
    sim_package : bool
        flag indicating this is a simulation-level package
    """

    def __init__(self, model, pkg_type, pkg_name, sim_package=False):
        self.model = model
        self.pkg_type = pkg_type
        self.pkg_name = pkg_name.upper()
        self._sim_package = sim_package
        self._rhs = None
        self._hcof = None
        self._bound_vars = []
        self._advanced_var_names = None
        self._idm_enabled = False
        self._inputs = {}

        self._variables_adv = None
        self._build_inputs()

    # ------------------------------------------------------------------
    # Input construction
    # ------------------------------------------------------------------

    def _build_inputs(self):
        if self.pkg_type in adv_pkgvars:
            self._build_advanced_inputs()
        elif self.pkg_type in pkgvars and any(isinstance(v, tuple) for v in pkgvars[self.pkg_type]):
            self._build_list_inputs(pkgvars[self.pkg_type])
        elif self.pkg_type in pkgvars:
            self._build_plain_inputs(pkgvars[self.pkg_type])

    def _build_list_inputs(self, vars_list):
        var_addrs = []
        for var in vars_list:
            if isinstance(var, tuple):
                self._bound_vars = var[-1]
                var = var[0]
            if self._sim_package:
                var_addrs.append(self.model.mf6.get_var_address(var.upper(), self.pkg_name))
            else:
                var_addrs.append(self.model.mf6.get_var_address(var.upper(), self.model.name, self.pkg_name))

        for var in self._bound_vars:
            addr_chk = self.model.mf6.get_var_address(var.upper(), self.model.name, self.pkg_name)
            if addr_chk in self.model.mf6.get_input_var_names():
                self._idm_enabled = True
                var_addrs.append(addr_chk)

        self._inputs["stress_period_data"] = ListVar(self, var_addrs, spd=True)

    def _build_plain_inputs(self, vars_list):
        ivn = self.model.mf6.get_input_var_names()
        for var in vars_list:
            if self._sim_package:
                addr = self.model.mf6.get_var_address(var.upper(), self.pkg_name)
            else:
                addr = self.model.mf6.get_var_address(var.upper(), self.model.name, self.pkg_name)
            if addr not in ivn:
                continue
            name = var.lower()
            if self._sim_package:
                self._inputs[name] = ScalarVar(name, self.model.mf6.get_value_ptr(addr))
            else:
                arr_var = ArrayVar(self, addr)
                if arr_var.name is not None:
                    self._inputs[name] = arr_var

    def _build_advanced_inputs(self):
        adv_var_dict = adv_pkgvars[self.pkg_type]

        pkg_var_addrs = self._collect_adv_var_addrs(adv_var_dict, "packagedata")
        if pkg_var_addrs:
            self._inputs["packagedata"] = ListVar(self, pkg_var_addrs, spd=False)

        sp_var_addrs = []
        if "perioddata" in adv_var_dict:
            for var in adv_var_dict["perioddata"]:
                if isinstance(var, tuple):
                    use_bound = all(":" not in v for v in var[-1])
                    if use_bound:
                        self._bound_vars = var[-1]
                        var = var[0]
                    else:
                        for v in var[-1]:
                            if ":" in v:
                                self._bound_vars.append(v.split(":")[0])
                            else:
                                self._bound_vars.append(v)
                            sp_var_addrs.append(self._adv_var_addr(v))
                        var = None
                if var is not None:
                    sp_var_addrs.append(self.model.mf6.get_var_address(var.upper(), self.model.name, self.pkg_name))

        if sp_var_addrs:
            self._inputs["stress_period_data"] = ListVar(self, sp_var_addrs, spd=True)

        for block in adv_var_dict:
            if block in _ADV_BLOCK_NAMES:
                continue
            var_addrs = self._collect_adv_var_addrs(adv_var_dict, block)
            if var_addrs:
                self._inputs[block] = ListVar(self, var_addrs, spd=False, name=block)

    def _collect_adv_var_addrs(self, adv_var_dict, block):
        var_addrs = []
        if block in adv_var_dict:
            for var in adv_var_dict[block]:
                if not isinstance(var, tuple):
                    var_addrs.append(self._adv_var_addr(var))
                else:
                    for v in var:
                        var_addrs.append(self._adv_var_addr(v))
        return var_addrs

    def _adv_var_addr(self, var_str):
        return f"{self.model.name}/{self.pkg_name}/{var_str.upper()}"

    # ------------------------------------------------------------------
    # Attribute dispatch
    # ------------------------------------------------------------------

    def __repr__(self):
        s = f"{self.pkg_type.upper()} Package: {self.pkg_name}\n"
        names = self.variable_names
        if names:
            s += " Accessible variables include:\n"
            for name in names:
                s += f"  {name}\n"
        return s

    def __getattr__(self, item):
        try:
            inputs = object.__getattribute__(self, "_inputs")
        except AttributeError:
            raise AttributeError(item)
        if item in inputs:
            v = inputs[item]
            return v.values if isinstance(v, ScalarVar) else v
        raise AttributeError(item)

    def __setattr__(self, item, value):
        if item.startswith("_") or item in _BASE_ATTRS:
            object.__setattr__(self, item, value)
            return
        for cls in type(self).__mro__:
            desc = cls.__dict__.get(item)
            if desc is not None and hasattr(desc, "__set__"):
                desc.__set__(self, value)
                return
        try:
            inputs = object.__getattribute__(self, "_inputs")
        except AttributeError:
            object.__setattr__(self, item, value)
            return
        if item in inputs:
            inputs[item].values = value
            return
        raise AttributeError(f"{item} is not a valid attribute for {self.pkg_type}")

    # ------------------------------------------------------------------
    # Static properties
    # ------------------------------------------------------------------

    @property
    def variable_names(self):
        """Returns a sorted list of non-list variable names accessible through the API."""
        return sorted(n for n, v in self._inputs.items() if not isinstance(v, ListVar))

    @property
    def _spd_var(self):
        return next((v for v in self._inputs.values() if isinstance(v, ListVar) and v._spd), None)

    @property
    def nbound(self):
        """Returns the number of active boundaries for the current stress period."""
        lv = self._spd_var
        return lv._nbound[0] if lv is not None else None

    @property
    def maxbound(self):
        """Returns the maximum number of boundaries."""
        lv = self._spd_var
        return lv._maxbound[0] if lv is not None else None

    @property
    def rhs(self):
        if not self._sim_package:
            if self._rhs is None:
                var_addr = self.model.mf6.get_var_address("RHS", self.model.name, self.pkg_name)
                if var_addr in self.model.mf6.get_input_var_names():
                    self._rhs = self.model.mf6.get_value_ptr(var_addr)
                else:
                    return None
        return np.copy(self._rhs)

    @rhs.setter
    def rhs(self, values):
        if self._rhs is None:
            rhs = self.rhs
            if rhs is None:
                raise Exception(f"{self.pkg_type} does not have a rhs array")
        self._rhs[:] = values[:]

    @property
    def hcof(self):
        if not self._sim_package:
            if self._hcof is None:
                var_addr = self.model.mf6.get_var_address("HCOF", self.model.name, self.pkg_name)
                if var_addr in self.model.mf6.get_input_var_names():
                    self._hcof = self.model.mf6.get_value_ptr(var_addr)
                else:
                    return None
        return np.copy(self._hcof)

    @hcof.setter
    def hcof(self, values):
        if self._hcof is None:
            hcof = self.hcof
            if hcof is None:
                raise Exception(f"{self.pkg_type} does not have an hcof array")
        self._hcof[:] = values[:]

    @property
    def advanced_vars(self):
        """Returns a list of additional variables accessible through get/set_advanced_var."""
        if self._advanced_var_names is None:
            adv_vars = []
            for var_addr in self.model.mf6.get_input_var_names():
                t = var_addr.split("/")
                is_advanced = False
                if not self._sim_package:
                    if t[0] == self.model.name and t[1] == self.pkg_name:
                        is_advanced = self._check_if_advanced_var(t[-1])
                else:
                    if t[0] == self.pkg_name:
                        is_advanced = self._check_if_advanced_var(t[-1])
                if is_advanced:
                    adv_vars.append(t[-1].lower())
            self._advanced_var_names = adv_vars
        return self._advanced_var_names

    def _check_if_advanced_var(self, variable_name):
        if variable_name.lower() in self._bound_vars:
            return False
        if self.pkg_type not in pkgvars:
            return True
        if variable_name.lower() in pkgvars[self.pkg_type]:
            return False
        return True

    def get_advanced_var(self, name):
        """Get a variable not surfaced through stress_period_data or variable_names."""
        name = name.lower()
        if name not in self.advanced_vars:
            raise AssertionError(f"{name} is not accessible as an advanced variable for this package")
        if self._variables_adv is None:
            self._variables_adv = AdvancedInput(self)
        values = self._variables_adv.get_variable(name)
        if not self._sim_package:
            if values.size == self.model.nodetouser.size:
                array = np.full(self.model.size, np.nan)
                array[self.model.nodetouser] = values
                return array
        return values

    def set_advanced_var(self, name, values):
        """Set a variable not surfaced through stress_period_data or variable_names."""
        if not self._sim_package:
            if values.size == self.model.size:
                values = values[self.model.nodetouser]
        if self._variables_adv is None:
            self._variables_adv = AdvancedInput(self)
        self._variables_adv.set_variable(name, values)

    # ------------------------------------------------------------------
    # Explicit accessor methods (backward compatibility)
    # ------------------------------------------------------------------

    def get_array(self, item):
        """Get a grid-shaped array variable by name."""
        v = self._inputs.get(item)
        if v is None or not isinstance(v, ArrayVar):
            raise KeyError(f"{item} is not accessible in this package")
        return v.values

    def set_array(self, item, array):
        """Set a grid-shaped array variable by name."""
        v = self._inputs.get(item)
        if v is None or not isinstance(v, ArrayVar):
            raise KeyError(f"{item} is not a valid variable name for this package")
        v.values = array

    def get_value(self, item):
        """Get a scalar variable by name."""
        v = self._inputs.get(item)
        if v is None or not isinstance(v, ScalarVar):
            raise KeyError(f"{item} is not accessible in this package")
        return v.values

    def set_value(self, item, value):
        """Set a scalar variable by name."""
        v = self._inputs.get(item)
        if v is None or not isinstance(v, ScalarVar):
            raise KeyError(f"{item} is not accessible in this package")
        v.values = value


# ------------------------------------------------------------------
# Marker subclasses — preserve isinstance compatibility
# ------------------------------------------------------------------


class PackageBase(Package):
    pass


class ListPackage(Package):
    pass


class ArrayPackage(Package):
    pass


class ScalarPackage(Package):
    pass


class AdvancedPackage(Package):
    pass


# ------------------------------------------------------------------
# Solution package
# ------------------------------------------------------------------


class ApiSlnPackage(Package):
    """
    Class to access solution packages.

    Parameters
    ----------
    sim : ApiSimulation or ApiMbase
        simulation object
    pkg_name : str
        package name in the MF6 variables
    pkg_type : str
        solution type abbreviation, default 'ims'
    """

    def __init__(self, sim, pkg_name, pkg_type="ims"):
        from .apimodel import ApiMbase

        super().__init__(sim, f"sln-{pkg_type}", pkg_name, sim_package=True)

        if pkg_type == "ims":
            mdl = ApiMbase(sim.mf6, pkg_name.upper(), pkg_types={pkg_type: Package})
            imslin = Package(mdl, "ims", "IMSLINEAR", sim_package=True)
            for key, var in imslin._inputs.items():
                if key in self._inputs:
                    key = f"{imslin.pkg_type}_{key}"
                self._inputs[key] = var
        else:
            object.__setattr__(self, "mxiter", 10)
