import numpy as np

from .pakbase import (
    AdvancedPackage,
    ArrayPackage,
    ListPackage,
    package_factory,
)

gridshape = {
    "dis": ["nlay", "nrow", "ncol"],
    "disu": [
        "nlay",
        "ncpl",
    ],
}


class ApiMbase:
    """
    Base object for the Models and Exchanges

    Parameters
    ----------
    mf6 : ModflowApi
        initialized ModflowApi object
    name : str
        modflow model name. ex. "GWF_1", "GWF-GWF_1"
    pkg_types : dict
        dictionary of package types and ApiPackage class types
    """

    def __init__(self, mf6, name, pkg_types):
        self.mf6 = mf6
        self.name = name
        self._pkg_names = None
        self._pak_type = None
        self.pkg_types = pkg_types
        self.package_dict = {}
        self._set_package_names()
        self._create_package_list()

    @property
    def package_list(self):
        """
        Returns a list of package objects for the model
        """
        return [package for _, package in self.package_dict.items()]

    @property
    def package_names(self):
        """
        Returns a list of package names for the model
        """
        return list(self.package_dict.keys())

    @property
    def package_types(self):
        return list(set([package.pkg_type for package in self.package_list]))

    def _set_package_names(self):
        """
        Method to get/set all package names within the model
        """
        pak_types = {"dis": "DIS"}
        for addr in self.mf6.get_input_var_names():
            tmp = addr.split("/")
            if addr.endswith("PACKAGE_TYPE") and tmp[0] == self.name:
                pak_types[tmp[1]] = self.mf6.get_value(addr)[0]
            elif tmp[0] == self.name and len(tmp) == 2:
                if tmp[0].startswith("GWF-GWF"):
                    pak_types[tmp[0]] = "GWF-GWF"
                    pak_types.pop("dis", None)
                elif tmp[0].startswith("GWT-GWT"):
                    pak_types[tmp[0]] = "GWT-GWT"
                    pak_types.pop("dis", None)

        self._pak_type = list(pak_types.values())
        self._pkg_names = list(pak_types.keys())

    def _create_package_list(self):
        """
        Method to load packages and set up the package dict/list variable
        """
        for ix, pkg_name in enumerate(self._pkg_names):
            pkg_type = self._pak_type[ix].lower()
            if pkg_type in self.pkg_types:
                basepackage = self.pkg_types[pkg_type]
            else:
                basepackage = AdvancedPackage

            package = package_factory(pkg_type, basepackage)
            adj_pkg_name = "".join(pkg_type.split("-"))

            if adj_pkg_name.lower() in ("gwfgwf", "gwtgwt"):
                adj_pkg_name = ""
            else:
                adj_pkg_name = pkg_name

            package = package(basepackage, self, pkg_type, adj_pkg_name)
            self.package_dict[pkg_name.lower()] = package

    def get_package(self, pkg_name) -> ListPackage or ArrayPackage or AdvancedPackage:
        """
        Method to get a package

        Parameters
        ----------
        pkg_name : str
            package name str. Ex. "wel_0"
        """
        pkg_name = pkg_name.lower()
        if pkg_name in self.package_dict:
            return self.package_dict[pkg_name]

        raise KeyError(f"{pkg_name} is not a valid package name for this model")


class ApiModel(ApiMbase):
    """
    Container to hold MODFLOW model information and load supported packages

    Parameters
    ----------
    mf6 : ModflowApi
        initialized ModflowApi object
    name : str
        modflow model name. ex. "GWF_1"

    """

    def __init__(self, mf6, name):
        _id_addr = mf6.get_var_address("ID", name)
        self._id = mf6.get_value(_id_addr)[0]
        if self._id < 1:
            self._id = 1
        _solnid = mf6.get_var_address("IDSOLN", name)
        self._solnid = mf6.get_value(_solnid)[0]
        grid_type = mf6.get_grid_type(self._id)
        if grid_type == "rectilinear":
            self.dis_type = "dis"
            self.dis_name = "DIS"
        elif grid_type == "unstructured":
            self.dis_type = "disu"
            self.dis_name = "DIS"
        else:
            raise AssertionError(f"Unrecognized discretization type {grid_type}")

        pkg_types = {
            "dis": ArrayPackage,
            "chd": ListPackage,
            "drn": ListPackage,
            "evt": ListPackage,
            "ghb": ListPackage,
            "ic": ArrayPackage,
            "npf": ArrayPackage,
            "rch": ListPackage,
            "riv": ListPackage,
            "sto": ArrayPackage,
            "wel": ListPackage,
            # gwt
            "dsp": ArrayPackage,
            "cnc": ListPackage,
            "ist": ArrayPackage,
            "mst": ArrayPackage,
            "src": ListPackage,
            # gwe
            "cnd": ArrayPackage,
            "est": ArrayPackage,
            "cpt": ListPackage,
            "esl": ListPackage,
            # prt
            "mip": ArrayPackage,
        }

        self.allow_convergence = True
        self._shape = None
        self._size = None
        self._nodetouser = None
        self._usertonode = None
        self._iteration = 0

        super().__init__(mf6, name, pkg_types)

    def __repr__(self):
        s = f"{self.name}, "
        shape = self.shape
        if self.dis_type == "dis":
            s += f"{shape[0]} Layer, {shape[1]} Row, {shape[2]} Column model\n"

        elif self.dis_type == "disu":
            if len(shape) == 2:
                s += f"{shape[0]} Layer, {shape[1]} Nodes per layer model\n"
            else:
                s += f"{shape[0]} Node model\n"
        else:
            pass

        s += "Packages accessible include: \n"
        for typ, baseobj in [
            ("ArrayPackage", ArrayPackage),
            ("ListPackage", ListPackage),
            ("AdvancedPackage", AdvancedPackage),
        ]:
            s += f"  {typ} objects:\n"
            for name, obj in self.package_dict.items():
                if isinstance(obj, baseobj):
                    s += f"    {name}: {type(obj)}\n"

        return s

    def __getattr__(self, item):
        """
        Method for getting packages either by package name or by
        package type name

        """
        if item in self.package_dict:
            return self.package_dict[item]
        else:
            pkg_list = []
            for pkg_name, package in self.package_dict.items():
                if item == package.pkg_type:
                    pkg_list.append(package)

            if len(pkg_list) == 0:
                return super().__getattribute__(item)
            elif len(pkg_list) == 1:
                return pkg_list[0]
            else:
                return pkg_list

    def __setattr__(self, key, value):
        """
        Method for type checking variables
        """
        if key == "allow_convergence":
            if not isinstance(value, bool):
                raise TypeError("allow convergenge must be a boolean value")

        super().__setattr__(key, value)

    @property
    def kper(self):
        """
        Returns the current stress period
        """
        var_addr = self.mf6.get_var_address("KPER", "TDIS")
        return self.mf6.get_value(var_addr)[0] - 1

    @property
    def kstp(self):
        """
        Returns the current timestep
        """
        var_addr = self.mf6.get_var_address("KSTP", "TDIS")
        return self.mf6.get_value(var_addr)[0] - 1

    @property
    def nstp(self):
        """
        Returns the number of timesteps in the current stress period
        """
        var_addr = self.mf6.get_var_address("NSTP", "TDIS")
        return self.mf6.get_value(var_addr)[0]

    @property
    def nper(self):
        """
        Returns the number of stress periods
        """
        var_addr = self.mf6.get_var_address("NPER", "TDIS")
        return self.mf6.get_value(var_addr)[0]

    @property
    def totim(self):
        """
        Returns the current model time
        """
        var_addr = self.mf6.get_var_address("TOTIM", "TDIS")
        return self.mf6.get_value(var_addr)[0]

    @property
    def subcomponent_id(self):
        """
        Returns the model subcomponent id
        """
        return self._id

    @property
    def solution_id(self):
        """
        Returns the model solution id
        """
        return self._solnid

    @property
    def shape(self):
        """
        Returns a tuple of the model shape
        """
        ivn = self.mf6.get_input_var_names()
        if self._shape is None:
            shape_vars = gridshape[self.dis_type]
            shape = []
            for var in shape_vars:
                var_addr = self.mf6.get_var_address(
                    var.upper(), self.name, self.dis_name
                )
                if var_addr in ivn:
                    shape.append(self.mf6.get_value(var_addr)[0])
            if not shape:
                var_addr = self.mf6.get_var_address("NODES", self.name, self.dis_name)
                shape.append(self.mf6.get_value(var_addr)[0])
            self._shape = tuple(shape)
        return self._shape

    @property
    def size(self):
        """
        Returns the number of nodes in the model
        """
        if self._size is None:
            size = 1
            for dim in self.shape:
                size *= dim
            self._size = size
        return self._size

    @property
    def nodetouser(self):
        """
        Returns the "nodeuser" array
        """
        if self._nodetouser is None:
            self._set_node_mapping()
        return self._nodetouser

    @property
    def usertonode(self):
        """
        Returns an array that maps user arrays to modflow's internal nodes
        """
        if self._usertonode is None:
            self._set_node_mapping()
        return self._usertonode

    @property
    def X(self):
        """
        Returns the solution array. Ex. GFW models return heads, GWT
        returns a concentration array, etc...
        """
        x = self.mf6.get_value(self.mf6.get_var_address("X", self.name))
        array = np.full(self.size, np.nan)
        array[self.nodetouser] = x
        return array.reshape(self.shape)

    def _set_node_mapping(self):
        """
        Sets the node mapping arrays NODEUSER and NODEREDUCED for mapping
        user arrays to modflow's internal arrays
        """
        node_addr = self.mf6.get_var_address("NODES", self.name, self.dis_name)
        nodes = self.mf6.get_value(node_addr).item()
        if nodes == self.size:
            nodeuser = np.arange(nodes).astype(int)
            nodereduced = np.copy(nodeuser)
        else:
            nodeuser_addr = self.mf6.get_var_address(
                "NODEUSER", self.name, self.dis_name
            )
            nodeuser = self.mf6.get_value(nodeuser_addr) - 1
            nodereduced_addr = self.mf6.get_var_address(
                "NODEREDUCED", self.name, self.dis_name
            )
            nodereduced = self.mf6.get_value(nodereduced_addr) - 1

        self._nodetouser = nodeuser
        self._usertonode = nodereduced
