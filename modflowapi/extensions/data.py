from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import xmipy.errors


class InputVar(ABC):
    """Abstract base for a single named variable in the MODFLOW 6 memory manager."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def values(self): ...

    @values.setter
    @abstractmethod
    def values(self, value): ...


class ArrayVar(InputVar):
    """
    A single grid-shaped array variable from the MODFLOW 6 memory manager.

    Parameters
    ----------
    parent : Package
        modflowapi Package object
    var_addr : str
        variable address string
    mf6 : ModflowApi, optional
        required if parent is None
    """

    def __init__(self, parent, var_addr, mf6=None):
        self._ptr = None
        self.parent = parent
        self._name = None
        self._vshape = None

        if self.parent is not None:
            self.mf6 = self.parent.model.mf6
        else:
            if mf6 is None:
                raise AssertionError("mf6 must be supplied if parent is None")
            self.mf6 = mf6

        ivn = self.mf6.get_input_var_names()
        if var_addr in ivn:
            values = self.mf6.get_value_ptr(var_addr)
            self._name = var_addr.split("/")[-1].lower()
            self._vshape = values.shape
            self._ptr = values

    @property
    def name(self) -> str:
        return self._name

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, key, value):
        array = self.values
        array[key] = value
        self.values = array

    @property
    def values(self):
        if not self.parent._sim_package:
            value = np.ones((self.parent.model.size,)) * np.nan
            if self._ptr.size == self.parent.model.size:
                value[:] = self._ptr.ravel()
            elif self._ptr.size == self.parent.model.nodetouser.size:
                # Variable lives on the reduced (active-node) grid
                value[self.parent.model.nodetouser] = self._ptr.ravel()
            else:
                # Non-grid variable (e.g. per-boundary rhs/hcof); return raw copy
                return np.copy(self._ptr.ravel())
            return value.reshape(self.parent.model.shape)
        else:
            return np.copy(self._ptr.ravel())

    @values.setter
    def values(self, array):
        if not isinstance(array, np.ndarray):
            raise TypeError()
        if not self.parent._sim_package:
            if array.size == self.parent.model.size:
                array = array.ravel()
                if self._ptr.size != array.size:
                    array = array[self.parent.model.nodetouser]
                if len(self._vshape) > 1:
                    array.shape = self._vshape
            elif array.size == self._ptr.size:
                # Non-grid variable (e.g. per-boundary rhs/hcof); assign directly
                array = array.ravel()
                if len(self._vshape) > 1:
                    array.shape = self._vshape
            else:
                raise ValueError(
                    f"{self.name} size {array.size} is not equal to modflow variable size {self.parent.model.size}"
                )
        else:
            array = array.ravel()
        self._ptr[:] = array


class ScalarVar(InputVar):
    """
    A single scalar variable from the MODFLOW 6 memory manager.

    Parameters
    ----------
    name : str
        variable name
    ptr : np.ndarray
        1-element pointer array from the MODFLOW 6 memory manager
    """

    def __init__(self, name: str, ptr):
        self._name = name
        self._ptr = ptr

    @property
    def name(self) -> str:
        return self._name

    @property
    def values(self):
        return self._ptr[0]

    @values.setter
    def values(self, v):
        self._ptr[0] = v


class ListVar(InputVar):
    """
    A single list/recarray block from the MODFLOW 6 memory manager.

    Parameters
    ----------
    parent : Package
        modflowapi Package object
    var_addrs : list
        variable address strings
    mf6 : ModflowApi, optional
        required if parent is None
    spd : bool
        True for stress period data, False for packagedata
    name : str, optional
        override the default block name
    """

    _nodevars = ("nodelist", "nexg", "maxats")

    def __init__(self, parent, var_addrs, mf6=None, spd=True, name=None):
        self.parent = parent
        if self.parent is not None:
            self.mf6 = self.parent.model.mf6
        else:
            if mf6 is None:
                raise AssertionError("mf6 must be supplied if parent is None")
            self.mf6 = mf6

        self._name = name or ("stress_period_data" if spd else "packagedata")
        self._ptrs = {}
        self._compound_ptrs = {}
        self._bound = "bound"

        self._maxbound = [0]
        self._nbound = [0]
        self._naux = [0]
        self._auxvar_name = "auxvar"
        self._auxnames = []
        self._dtype = []

        self._spd = spd
        var_addrs = list(var_addrs)
        if self.parent._idm_enabled:
            for var in ("BOUND", "AUXVAR"):
                var_addrs.pop(
                    var_addrs.index(self.mf6.get_var_address(var, self.parent.model.name, self.parent.pkg_name))
                )
            var_addrs.append(self.mf6.get_var_address("AUXVAR_IDM", self.parent.model.name, self.parent.pkg_name))

        self._set_data(var_addrs)

    @property
    def name(self) -> str:
        return self._name

    def _set_data(self, var_addrs):
        for var_addr in var_addrs:
            if ":" in var_addr:
                addr_pieces = var_addr.split("/")
                compound = addr_pieces[-1]
                addr_pieces = addr_pieces[:-1]
                reduced, ctype, ptr_var = [i.lower() for i in compound.split(":")]
                addr_pieces.append(ptr_var.upper())
                var_addr = "/".join(addr_pieces)

                try:
                    values = self.mf6.get_value_ptr(var_addr)
                except xmipy.errors.InputError:
                    continue

                if reduced in ("ndiv",):
                    nbound = self._special_condition_to_values(ctype, values)
                    self._maxbound = [len(values)]
                    self._nbound = [nbound]
                else:
                    self._compound_ptrs[ptr_var] = values
                    self._ptrs[reduced] = f"{ctype}:{ptr_var}"
                    self._dtype.append((reduced, values.dtype.str))
            else:
                try:
                    values = self.mf6.get_value_ptr(var_addr)
                except xmipy.errors.InputError:
                    if self._naux[0] > 0:
                        values = self.mf6.get_value(var_addr)
                    else:
                        continue

                reduced = var_addr.split("/")[-1].lower()
                if reduced in ("maxbound", "nbound"):
                    setattr(self, f"_{reduced}", values)
                    if not self._spd and reduced == "maxbound":
                        self._nbound = values
                elif reduced in ("nexg", "maxats", "nlakes", "nmawwells"):
                    self._maxbound = values
                    self._nbound = values
                elif reduced in ("naux",):
                    self._naux = values
                elif reduced in ("auxname_cst",):
                    self._auxnames = list(values)
                else:
                    self._ptrs[reduced] = values
                    if reduced == self._bound:
                        for nm in self.parent._bound_vars:
                            self._dtype.append((nm, values.dtype.str))
                    elif reduced in self.parent._bound_vars:
                        self._dtype.append((reduced, values.dtype.str))
                    elif reduced in self._nodevars:
                        self._dtype.append((reduced, "O"))
                    elif "auxvar" in reduced:
                        self._auxvar_name = reduced
                        if self._naux[0] == 0:
                            continue
                        else:
                            for ix in range(self._naux[0]):
                                self._dtype.append((self._auxnames[ix], values.dtype.str))
                    else:
                        self._dtype.append((reduced, values.dtype.str))

    def _ptr_to_recarray(self):
        if self._nbound[0] == 0:
            return
        recarray = np.recarray((self._nbound[0],), self._dtype)
        for name, ptr in self._ptrs.items():
            if name == self._auxvar_name and self._naux[0] == 0:
                continue

            if isinstance(ptr, str):
                ctype, ptr_name = ptr.split(":")
                ptr_vals = self._compound_ptrs[ptr_name]
                values = self._special_condition_to_values(ctype, ptr_vals)
            else:
                values = np.copy(ptr)

            if name == self._bound:
                for ix, nm in enumerate(self.parent._bound_vars):
                    bnd_values = values[0 : self._nbound[0], ix]
                    recarray[nm][0 : self._nbound[0]] = bnd_values

            elif name in self.parent._bound_vars and self.parent._idm_enabled:
                bnd_values = values[0 : self._nbound[0]].ravel()
                recarray[name][0 : self._nbound[0]] = bnd_values

            elif name == self._auxvar_name:
                for ix in range(self._naux[0]):
                    nm = self._auxnames[ix]
                    aux_values = values[0 : self._nbound[0], ix]
                    recarray[nm][0 : self._nbound[0]] = aux_values

            elif name == "auxname_cst":
                pass

            else:
                values = values.ravel()
                if name in self._nodevars:
                    values -= 1
                    values = self.parent.model.nodetouser[values]
                    values = list(zip(*np.unravel_index(values, self.parent.model.shape)))
                elif name in ("idv", "divreach"):
                    values -= 1

                values = values[0 : self._nbound[0]]
                recarray[name][0 : self._nbound[0]] = values

        return recarray

    def _recarray_to_ptr(self, recarray):
        if recarray is None:
            self._nbound[0] = 0
            return

        if len(recarray) != self._nbound[0]:
            if len(recarray) > self._maxbound[0]:
                raise AssertionError(
                    f"Length of stresses ({len(recarray)},) cannot be larger than maxbound value ({self._maxbound[0]},)"
                )
            self._nbound[0] = len(recarray)
            if len(recarray) == 0:
                return

        visited = []
        for name in recarray.dtype.names:
            if name in visited:
                continue
            if name in self._nodevars:
                multi_index = tuple(np.array([list(i) for i in recarray[name]]).T)
                nodes = np.ravel_multi_index(multi_index, self.parent.model.shape)
                recarray[name] = self.parent.model.usertonode[nodes] + 1

            if name in ("divreach",):
                self._ptrs[name][0 : self._nbound[0]] = recarray[name].ravel() + 1
                visited.append(name)

            elif self._bound in self._ptrs and name in self.parent._bound_vars:
                idx = self.parent._bound_vars.index(name)
                self._ptrs[self._bound][0 : self._nbound[0], idx] = recarray[name]
                visited.append(name)

            elif name in self._auxnames:
                ptr_name = self._auxvar_name
                idx = self._auxnames.index(name)
                self._ptrs[ptr_name][0 : self._nbound[0], idx] = recarray[name]
                visited.append(name)

            elif name == "auxname_cst":
                pass

            elif name == self._bound:
                pass

            else:
                if isinstance(self._ptrs[name], str):
                    visited = self._special_condition_to_ptr(recarray, name, visited)
                else:
                    self._ptrs[name][0 : self._nbound[0]] = recarray[name]
                    visited.append(name)

    def _special_condition_to_values(self, ctype, inval):
        functions = {
            "range": lambda x: np.arange(0, int(x), dtype=int),
            "count_nonzero": lambda x: np.count_nonzero(x),
            "where_idx": lambda x: np.array(np.where(x)[0]),
            "where_val": lambda x: x[x != 0],
        }
        ctype = ctype.lower()
        if ctype in ("range",):
            inval = inval[0]
        return functions[ctype](inval)

    def _special_condition_to_ptr(self, recarray, name, visited):
        functions = {
            "range": lambda x: [len(x)],
        }
        ctype, ptr_name = self._ptrs[name].split(":")
        if "where" in ctype:
            idx_name = val_name = None
            if ctype == "where_idx":
                idx_name = name
                for k, v in self._ptrs.items():
                    if isinstance(v, str) and v == f"where_val:{ptr_name}":
                        val_name = k
                        break
            elif ctype == "where_val":
                val_name = name
                for k, v in self._ptrs.items():
                    if isinstance(v, str) and v == f"where_idx:{ptr_name}":
                        idx_name = k
                        break
            else:
                return visited

            if idx_name is None or val_name is None:
                return visited

            idx = list(recarray[idx_name].astype(int))
            vals = recarray[val_name].ravel()
            if val_name in ("idv",):
                vals += 1
            self._compound_ptrs[ptr_name][idx] = vals
            visited.extend([idx_name, val_name])
        else:
            func = functions[ctype]
            values = func(recarray[name])
            self._compound_ptrs[ptr_name][:] = values[:]
            visited.append(name)

        return visited

    def __getitem__(self, item):
        recarray = self._ptr_to_recarray()
        return recarray[item]

    def __setitem__(self, key, value):
        recarray = self._ptr_to_recarray()
        recarray[key] = value
        self._recarray_to_ptr(recarray)

    @property
    def dtype(self):
        return self._dtype

    @property
    def values(self):
        return self._ptr_to_recarray()

    @values.setter
    def values(self, recarray):
        if isinstance(recarray, ListVar):
            recarray = recarray.values
        self._recarray_to_ptr(recarray)

    @property
    def dataframe(self):
        recarray = self._ptr_to_recarray()
        return pd.DataFrame.from_records(recarray)

    @dataframe.setter
    def dataframe(self, dataframe):
        recarray = dataframe.to_records(index=False)
        self._recarray_to_ptr(recarray)


class AdvancedInput(object):
    """
    Data object for dynamically storing pointers and working with
    "advanced" data types

    Parameters
    ----------
    parent : Package
        modflowapi Package object
    mf6 : ModflowApi, optional
        required if parent is None
    """

    def __init__(self, parent, mf6=None):
        self._ptrs = {}
        self.parent = parent

        if self.parent is not None:
            self.mf6 = self.parent.model.mf6
        else:
            if mf6 is None:
                raise AssertionError("mf6 must be supplied if parent is None")
            self.mf6 = mf6

    def get_variable(self, name):
        if name.lower() in self._ptrs:
            return self._ptrs[name.lower()]

        if not self.parent._sim_package:
            var_addr = self.mf6.get_var_address(name.upper(), self.parent.model.name, self.parent.pkg_name)
        else:
            var_addr = self.mf6.get_var_address(name.upper(), self.parent.pkg_name)

        try:
            values = self.mf6.get_value_ptr(var_addr)
            self._ptrs[name.lower()] = values
        except xmipy.errors.InputError:
            values = self.mf6.get_value(var_addr)

        return values.copy()

    def set_variable(self, name, values):
        if name.lower() not in self._ptrs:
            values0 = self.get_variable(name)
        else:
            values0 = self._ptrs[name.lower()]

        if values0.shape != values.shape:
            raise ValueError(
                f"Array shapes are incompatible: current shape={values.shape}, valid shape={values0.shape}"
            )

        if name.lower() not in self._ptrs:
            self.mf6.set_value(
                self.mf6.get_var_address(name.upper(), self.parent.model.name, self.parent.pkg_name),
                values,
            )
        else:
            self._ptrs[name.lower()][:] = values[:]


# Backward compatibility aliases
ArrayPointer = ArrayVar
ListInput = ListVar
