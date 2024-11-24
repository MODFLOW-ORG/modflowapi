import numpy as np
import pandas as pd
import xmipy.errors


class ListInput(object):
    """
    Data object for storing pointers and working with list based input data

    Parameters
    ----------
    parent : ListPackage
        modflowapi ListPackage object
    var_addrs : list, None
        optional list of variable addresses
    mf6 : ModflowApi, None
        optional ModflowApi object
    """

    def __init__(self, parent, var_addrs=None, mf6=None):
        self.parent = parent
        if self.parent is not None:
            self.var_addrs = self.parent.var_addrs
            self.mf6 = self.parent.model.mf6
        else:
            if var_addrs is None or mf6 is None:
                raise AssertionError(
                    "var_addrs and mf6 must be supplied if parent is None"
                )
            self.var_addrs = var_addrs
            self.mf6 = mf6

        self._ptrs = {}
        self._nodevars = ("nodelist", "nexg", "maxats")
        self._boundvars = ("bound",)

        self._maxbound = [0]
        self._nbound = [0]
        self._naux = [0]
        self._auxnames = []
        self._dtype = []
        self._reduced_to_var_addr = {}
        if self.parent._idm_enabled:
            for var in ("BOUND", "AUXVAR"):
                self.var_addrs.pop(
                    self.var_addrs.index(
                        self.mf6.get_var_address(
                            var, self.parent.model.name, self.parent.pkg_name
                        )
                    )
                )
            self.var_addrs.append(
                self.mf6.get_var_address(
                    "AUXVAR_IDM", self.parent.model.name, self.parent.pkg_name
                )
            )
            self._set_stress_period_data_idm()
        else:
            self._set_stress_period_data()

    def _set_stress_period_data_idm(self):
        """
        Method to set stress period data variable pointers to the _ptrs
        dictionary. Uses IDM updates instead of bound to access variable
        pointers.
        """
        # for now we need to add self.parent._bound_vars data to var_addrs
        for var_addr in self.var_addrs:
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
            elif reduced in ("nexg", "maxats"):
                setattr(self, "_maxbound", values)
                setattr(self, "_nbound", values)
            elif reduced in ("naux",):
                setattr(self, "_naux", values)
            elif reduced in ("auxname_cst"):
                setattr(self, "_auxnames", list(values))
            else:
                self._ptrs[reduced] = values
                self._reduced_to_var_addr[reduced] = var_addr
                if reduced in self.parent._bound_vars:
                    typ_str = values.dtype.str
                    dtype = (reduced, typ_str)
                    self._dtype.append(dtype)
                elif reduced in self._nodevars:
                    dtype = (reduced, "O")
                    self._dtype.append(dtype)
                elif reduced == "auxvar_idm":
                    if self._naux == 0:
                        continue
                    else:
                        for ix in range(self._naux[0]):
                            typ_str = values.dtype.str
                            dtype = (self._auxnames[ix], typ_str)
                            self._dtype.append(dtype)
                else:
                    typ_str = values.dtype.str
                    dtype = (reduced, typ_str)
                    self._dtype.append(dtype)

    def _set_stress_period_data(self):
        """
        Method to set stress period data variable pointers to the _ptrs
        dictionary

        PENDING DEPRECATION AND REPLACEMENT by _set_stress_period_data_idm()
        """
        for var_addr in self.var_addrs:
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
            elif reduced in ("nexg", "maxats"):
                setattr(self, "_maxbound", values)
                setattr(self, "_nbound", values)
            elif reduced in ("naux",):
                setattr(self, "_naux", values)
            elif reduced in ("auxname_cst"):
                setattr(self, "_auxnames", list(values))
            else:
                self._ptrs[reduced] = values
                self._reduced_to_var_addr[reduced] = var_addr
                if reduced in self._boundvars:
                    for name in self.parent._bound_vars:
                        typ_str = values.dtype.str
                        dtype = (name, typ_str)
                        self._dtype.append(dtype)
                elif reduced in self._nodevars:
                    dtype = (reduced, "O")
                    self._dtype.append(dtype)
                elif reduced == "auxvar":
                    if self._naux == 0:
                        continue
                    else:
                        for ix in range(self._naux[0]):
                            typ_str = values.dtype.str
                            dtype = (self._auxnames[ix], typ_str)
                            self._dtype.append(dtype)
                else:
                    typ_str = values.dtype.str
                    dtype = (reduced, typ_str)
                    self._dtype.append(dtype)

    def _ptr_to_recarray(self):
        """
        Method to get a recarray of stress period data from modflow pointers

        Returns
        -------
            np.recarray
        """
        if self._nbound[0] == 0:
            return
        recarray = np.recarray((self._nbound[0],), self._dtype)
        for name, ptr in self._ptrs.items():
            if "auxvar" in name and self._naux[0] == 0:
                continue
            values = np.copy(ptr)
            if name in self._boundvars:
                # note: block slated for deprecation
                for ix, nm in enumerate(self.parent._bound_vars):
                    bnd_values = values[0 : self._nbound[0], ix]
                    recarray[nm][0 : self._nbound[0]] = bnd_values
            elif name in self.parent._bound_vars and self.parent._idm_enabled:
                # new IDM simplification method
                bnd_values = values[0 : self._nbound[0]].ravel()
                recarray[name][0 : self._nbound[0]] = bnd_values
            elif "auxvar" in name:
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
                    values = list(
                        zip(*np.unravel_index(values, self.parent.model.shape))
                    )

                values = values[0 : self._nbound[0]]
                recarray[name][0 : self._nbound[0]] = values

        return recarray

    def _recarray_to_ptr(self, recarray):
        """
        Method to update stress period information pointers from user supplied
        data

        Parameters
        ----------
        recarray : np.recarray
            numpy recarray of stress period data

        """
        if recarray is None:
            self._nbound[0] = 0
            return

        if len(recarray) != self._nbound:
            if len(recarray) > self._maxbound[0]:
                raise AssertionError(
                    f"Length of stresses ({len(recarray)},) cannot be larger "
                    f"than maxbound value ({self._maxbound[0]},)"
                )
            self._nbound[0] = len(recarray)

            if len(recarray) == 0:
                return

        for name in recarray.dtype.names:
            if name in self._nodevars:
                multi_index = tuple(np.array([list(i) for i in recarray[name]]).T)
                nodes = np.ravel_multi_index(multi_index, self.parent.model.shape)
                recarray[name] = self.parent.model.usertonode[nodes] + 1

            if name in self.parent._bound_vars:
                if "bound" in self._ptrs:
                    # Block slated for deprecation after IDM inclusion
                    idx = self.parent._bound_vars.index(name)
                    bname = "bound"
                    self._ptrs[bname][0 : self._nbound[0], idx] = recarray[name]
                elif self.parent._idm_enabled:
                    # new IDM simplification
                    self._ptrs[name][0 : self._nbound[0]] = recarray[name].ravel()
                else:
                    pass
            elif name in self._auxnames:
                ptr_name = "auxvar"
                if self.parent._idm_enabled:
                    ptr_name += "_idm"
                idx = self._auxnames.index(name)
                self._ptrs[ptr_name][0 : self._nbound[0], idx] = recarray[name]
            elif name == "auxname_cst":
                pass
            else:
                self._ptrs[name][0 : self._nbound[0]] = recarray[name].ravel()

    def __getitem__(self, item):
        recarray = self._ptr_to_recarray()
        return recarray[item]

    def __setitem__(self, key, value):
        recarray = self._ptr_to_recarray()
        recarray[key] = value
        self._recarray_to_ptr(recarray)

    @property
    def dtype(self):
        """
        Returns the numpy dtypes for the recarray
        """
        return self._dtype

    @property
    def values(self):
        """
        Returns a np.recarray of the current stress_period_data
        """
        return self._ptr_to_recarray()

    @values.setter
    def values(self, recarray):
        """
        Setter method to update the current stress_period_data
        """
        self._recarray_to_ptr(recarray)

    @property
    def dataframe(self):
        recarray = self._ptr_to_recarray()
        return pd.DataFrame.from_records(recarray)

    @dataframe.setter
    def dataframe(self, dataframe):
        recarray = dataframe.to_records(index=False)
        self._recarray_to_ptr(recarray)


class ArrayPointer:
    """
    Data object for storing single pointers and
    working with array based input data

    Parameters
    ----------
    parent : ArrayPackage
        ArrayPackage object
    var_addr : str
        variable pointer location
    mf6 : ModflowApi
        optional ModflowApi object
    """

    def __init__(self, parent, var_addr, mf6=None):
        self._ptr = None
        self.parent = parent
        self._mapping = None
        self.name = None
        self.var_addr = var_addr
        self._vshape = None

        if self.parent is not None:
            self.mf6 = self.parent.model.mf6
        else:
            if mf6 is None:
                raise AssertionError("mf6 must be supplied if parent is None")
        self._set_array()

    def _set_array(self):
        ivn = self.mf6.get_input_var_names()
        if self.var_addr in ivn:
            values = self.mf6.get_value_ptr(self.var_addr)
            reduced = self.var_addr.split("/")[-1].lower()
            self._vshape = values.shape
            self._ptr = values
            self.name = reduced

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, key, value):
        array = self.values
        array[key] = value
        self.values = array

    @property
    def values(self):
        """
        Method to get an array from modflow

        Returns
        -------
        np.array of modflow data
        """
        if not self.parent._sim_package:
            value = np.ones((self.parent.model.size,)) * np.nan
            if self._ptr.size == self.parent.model.size:
                value[:] = self._ptr.ravel()
            else:
                value[self.parent.model.nodetouser] = self._ptr.ravel()
            return value.reshape(self.parent.model.shape)
        else:
            return np.copy(self._ptr.ravel())

    @values.setter
    def values(self, array):
        """
        Method to update the modflow pointer arrays

        Parameters
        ----------
        array : np.array
            numpy array

        """

        if not isinstance(array, np.ndarray):
            raise TypeError()
        if not self.parent._sim_package:
            if array.size != self.parent.model.size:
                raise ValueError(
                    f"{self.name} size {array.size} is not equal to "
                    f"modflow variable size {self.parent.model.size}"
                )

            array = array.ravel()
            if self._ptr.size != array.size:
                array = array[self.parent.model.nodetouser]
            if len(self._vshape) > 1:
                array.shape = self._vshape
        else:
            array = array.ravel()
        self._ptr[:] = array


class ArrayInput:
    """
    Data object for storing pointers and working with array based input data

    Parameters
    ----------
    parent : ArrayPackage
        modflowapi ArrayPackage object
    var_addrs : list, None
        optional list of variable addresses
    mf6 : ModflowApi, None
        optional ModflowApi object
    """

    def __init__(self, parent, var_addrs=None, mf6=None):
        self._ptrs = {}
        self.parent = parent
        # change this to a parent package.mapping
        self._mapping = None

        if self.parent is not None:
            self.var_addrs = self.parent.var_addrs
            self.mf6 = self.parent.model.mf6
        else:
            if var_addrs is None or mf6 is None:
                raise AssertionError(
                    "var_addrs and mf6 must be supplied if parent is None"
                )
            self.var_addrs = var_addrs
            self.mf6 = mf6

        self._maxbound = [0]
        self._nbound = [0]
        self._reduced_to_var_addr = {}
        self._set_arrays()

    def _set_arrays(self):
        """
        Method to modflow variable pointers to the _ptrs dictionary
        """
        ivn = self.mf6.get_input_var_names()
        for var_addr in self.var_addrs:
            if var_addr in ivn:
                ptr = ArrayPointer(self.parent, var_addr)
                reduced = var_addr.split("/")[-1].lower()
                self._ptrs[reduced] = ptr
                self._reduced_to_var_addr[reduced] = var_addr

    def __getattr__(self, item):
        """
        Dynamic method to get modflow variables as an attribute
        """
        if item in self._ptrs:
            return self._ptrs[item]
        else:
            return super(ArrayInput).__getattribute__(item)

    def __setattr__(self, item, value):
        """
        Dynamic method that allows users to set modflow variables to the
        _ptr dict
        """
        if item in (
            "parent",
            "var_addrs",
            "_mapping",
            "_ptrs",
            "mf6",
            "_maxbound",
            "_nbound",
            "_reduced_to_var_addr",
        ):
            super().__setattr__(item, value)

        elif item in self._ptrs:
            if isinstance(value, ArrayPointer):
                self._ptrs[item] = value
        else:
            raise AttributeError(f"{item} is not a valid attribute")

    @property
    def variable_names(self):
        """
        Returns a list of valid array names that can be accessed by the user
        """
        return list(sorted(self._ptrs.keys()))

    def get_ptr(self, item):
        """
        Method to get the ArrayPointer object

        Parameters
        ----------
        item : str
            modflow variable name: Ex. "k11"

        Returns
        -------
        ArrayPointer object
        """
        if item in self._ptrs:
            return self._ptrs[item]

    def set_ptr(self, item, ptr):
        """
        Method to set an ArrayPointer object

        Parameters
        ----------
        item : str
            modflow variable name: Ex. "k11"
        ptr : ArrayPointer
            ArrayPointer object
        """
        if item in self._ptrs:
            if isinstance(ptr, ArrayPointer):
                self._ptrs[item] = ptr
            else:
                raise TypeError("An ArrayPointer object must be provided")

        else:
            raise KeyError(f"{item} is not accessible in this package")

    def get_array(self, item):
        """
        Method to get an array from modflow

        Parameters
        ----------
        item : str
            modflow variable name. Ex. "k11"

        Returns
        -------
        np.array of modflow data
        """
        if item in self._ptrs:
            return self._ptrs[item].values
        else:
            raise KeyError(f"{item} is not accessible in this package")

    def set_array(self, item, array):
        """
        Method to update the modflow pointer arrays

        Parameters
        ----------
        item : str
            modflow variable name. Ex. "k11"
        array : np.array
            numpy array

        """
        if item in self._ptrs:
            self._ptrs[item].values = array
        else:
            raise KeyError(f"{item} is not a valid variable name for this package")


class AdvancedInput(object):
    """
    Data object for dynamically storing pointers and working with
    "advanced" data types

    Parameters
    ----------
    parent : ArrayPackage
        modflowapi ArrayPackage object
    mf6 : ModflowApi, None
        optional ModflowApi object
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

    def get_variable(self, name, model=None, package=None):
        """
        method to assemble a variable address and get a variable from the
        ModflowApi instance

        Parameters:
        ----------
        name : str
            variable name
        model : str
            optional model name, note this is required if parent is None
        package : str
            optional package name, note this is required if parent is None

        Returns:
        -------
            np.ndarray or scalar float, int, string, or boolean value
            depending on data type and length
        """
        if name.lower() in self._ptrs:
            return self._ptrs[name.lower()]

        if not self.parent._sim_package:
            if self.parent is not None:
                var_addr = self.mf6.get_var_address(
                    name.upper(), self.parent.model.name, self.parent.pkg_name
                )
            else:
                var_addr = self.mf6.get_var_address(
                    name.upper(), model.upper(), package.upper()
                )
        else:
            if self.parent is not None:
                var_addr = self.mf6.get_var_address(name.upper(), self.parent.pkg_name)
            else:
                var_addr = self.mf6.get_var_address(name.upper(), package.upper())

        try:
            values = self.mf6.get_value_ptr(var_addr)
            self._ptrs[name.lower()] = values
        except xmipy.errors.InputError:
            values = self.mf6.get_value(var_addr)

        return values.copy()

    def set_variable(self, name, values, model=None, package=None):
        """
        method to assemble a variable address and get a variable from the
        ModflowApi instance

        Parameters:
        ----------
        name : str
            variable name
        values : np.ndarray
            numpy array of variable values
        model : str
            optional model name, note this is required if parent is None
        package : str
            optional package name, note this is required if parent is None

        Returns:
        -------
            np.ndarray or scalar float, int, string, or boolean value
            depending on data type and length
        """
        if model is None and not self.parent._sim_package:
            model = self.parent.model.name
        if package is None:
            package = self.parent.pkg_name

        if name.lower() not in self._ptrs:
            values0 = self.get_variable(name, model, package)
        else:
            values0 = self._ptrs[name.lower()]

        if values0.shape != values.shape:
            raise ValueError(
                f"Array shapes are incompatible: "
                f"current shape={values.shape}, valid shape={values0.shape}"
            )

        if name.lower() not in self._ptrs:
            # this is a set value situation
            self.mf6.set_value(
                self.mf6.get_var_address(
                    name.upper(), self.parent.model.name, self.parent.pkg_name
                ),
                values,
            )
        else:
            self._ptrs[name.lower()][:] = values[:]


class ScalarInput:
    """
    Data object for storing pointers and working with array based input data

    Parameters
    ----------
    parent : ArrayPackage
        modflowapi ArrayPackage object
    var_addrs : list, None
        optional list of variable addresses
    mf6 : ModflowApi, None
        optional ModflowApi object
    """

    def __init__(self, parent, var_addrs=None, mf6=None):
        self._ptrs = {}
        self.parent = parent
        # change this to a parent package.mapping
        self._mapping = None

        if self.parent is not None:
            self.var_addrs = self.parent.var_addrs
            self.mf6 = self.parent.model.mf6
        else:
            if var_addrs is None or mf6 is None:
                raise AssertionError(
                    "var_addrs and mf6 must be supplied if parent is None"
                )
            self.var_addrs = var_addrs
            self.mf6 = mf6

        self._reduced_to_var_addr = {}
        self._set_scalars()

    def __getattr__(self, item):
        """
        Dynamic method to get modflow variables as an attribute
        """
        if item in self._ptrs:
            return self._ptrs[item]
        else:
            return super(ArrayInput).__getattribute__(item)

    def __setattr__(self, item, value):
        """
        Dynamic method that allows users to set modflow variables to the
        _ptr dict
        """
        if item in (
            "parent",
            "var_addrs",
            "_mapping",
            "_ptrs",
            "mf6",
            "_maxbound",
            "_nbound",
            "_reduced_to_var_addr",
        ):
            super().__setattr__(item, value)

        elif item in self._ptrs:
            self._ptrs[item] = value
        else:
            raise AttributeError(f"{item} is not a valid attribute")

    @property
    def variable_names(self):
        """
        Returns a list of valid array names that can be accessed by the user
        """
        return list(sorted(self._ptrs.keys()))

    def _set_scalars(self):
        """
        Method to modflow variable pointers to the _ptrs dictionary
        """
        ivn = self.mf6.get_input_var_names()
        for var_addr in self.var_addrs:
            if var_addr in ivn:
                ptr = self.mf6.get_value_ptr(var_addr)
                reduced = var_addr.split("/")[-1].lower()
                self._ptrs[reduced] = ptr
                self._reduced_to_var_addr[reduced] = var_addr

    def get_value(self, item):
        """
        Method to get a scalar value from modflow

        Parameters
        ----------
        item : str
            modflow variable name. Ex. "NPER"

        Returns
        -------
            str, int, float
        """
        if item in self._ptrs:
            return self._ptrs[item][0]
        else:
            raise KeyError(f"{item} is not accessible in this package")

    def set_value(self, item, value):
        """
        Method to set a scalar value in modflow

        Parameters
        ----------
        item : str
            modflow variable name. Ex. "NPER"

        value : str, int, float
        """
        if item in self._ptrs:
            self._ptrs[item][0] = value
        else:
            raise KeyError(f"{item} is not accessible in this package")
