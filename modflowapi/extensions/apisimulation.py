import numpy as np

from .apiexchange import ApiExchange
from .apimodel import ApiMbase, ApiModel
from .pakbase import ApiSlnPackage, ListPackage, ScalarPackage, package_factory


class ApiSimulation:
    """
    ApiSimulation object that holds a modflow simulation info and loads
    supported models.

    Parameters
    ----------
    mf6 : ModflowApi
        initialized ModflowApi object
    models : dict
        dictionary of model_name: modflowapi.extensions.ApiModel objects
    solutions : dict
        dictionary of solution_id: solution_name
    exchanges : dict
        dictionary of exchange_name: modflowapi.extensions.ApiExchange objects
    tdis : ApiTdisPackage
        time discretization (TDIS) ScalarPackage
    ats : None or ApiAtsPackage
        adaptive time step ScalarPackage object
    """

    def __init__(self, mf6, models, solutions, exchanges, tdis, ats):
        self.mf6 = mf6
        self._models = models
        self._exchanges = exchanges
        self._solutions = solutions
        self._iteration = -1

        self.tdis = tdis
        self.ats = ats
        self._ats_active = True
        if ats is None:
            self._ats_active = False

    def __getattr__(self, item):
        """
        Dynamic method to get models by model name
        """
        if item.lower() in self._models:
            return self.get_model(item)
        else:
            return super().__getattribute__(item)

    def __repr__(self):
        s = self.__doc__
        s += f"Number of models: {len(self._models)}:\n"
        for name, obj in self._models.items():
            s += f"\t{name} : {type(obj)}\n"
        s += "Simulation level packages include:\n"
        s += f"\tSLN: {self.sln}\n"
        s += f"\tTDIS: {self.tdis}\n"
        if self.ats_active:
            s += f"\tATS: {self.ats}\n"
        if self._exchanges:
            s += "\tExchanges include:\n"
            for name, exchange in self._exchanges.items():
                f"\t\t{name}: {type(exchange)}\n"

        return s

    @property
    def ats_active(self):
        """
        Returns a boolean to indicate if the ATS package is used in this
        simulation.
        """
        return self._ats_active

    @property
    def ats_period(self):
        """
        Returns a boolean to indicate if this is an ATS stress period
        """
        # maybe return tuple (bool, dtmin)
        if self.ats_active:
            recarray = self.ats.stress_period_data.values
            idx = np.where(recarray["iperats"] == self.kper + 1)[0]
            if len(idx) > 0:
                return True, recarray["dtmin"][idx[0]]

        return False, None

    @property
    def allow_convergence(self):
        """
        Returns a boolean value that specifies if the user will allow the
        model to converge. Default is True
        """
        for model in self.models:
            if not model.allow_convergence:
                return False
        return True

    @allow_convergence.setter
    def allow_convergence(self, value):
        """
        Method to set the allow_convergence flag

        Parameters
        ----------
        value : bool
            if True (default) model converges if solution converges, if False
            model will continue solving after solution converges.
        """
        for model in self.models:
            model.allow_convergence = value

    @property
    def subcomponent_count(self):
        """
        Returns the number of subcomponents in the simulation
        """
        return self.mf6.get_subcomponent_count()

    @property
    def solutions(self):
        """
        Returns a dictionary of solution_id : (name, ApiSlnPackage)
        """
        return self._solutions

    @property
    def sln(self):
        """
        Returns an ApiSolution object
        """
        if len(self._solutions) > 1:
            return list(self._solutions.values())
        else:
            for sln in self._solutions.values():
                return sln

    @property
    def model_names(self):
        """
        Returns a list of model names
        """
        return list(self._models.keys())

    @property
    def exchange_names(self):
        """
        Returns a list of exchange GWF-GWF names
        """
        if self._exchanges.keys():
            return list(self._exchanges.keys())

    @property
    def models(self):
        """
        Returns a list of ApiModel objects associated with the simulation
        """
        return [v for _, v in self._models.items()]

    @property
    def iteration(self):
        return self._iteration

    @iteration.setter
    def iteration(self, value):
        if isinstance(value, int):
            self._iteration = value

    @property
    def kper(self):
        """
        Returns the current stress period
        """
        return self.tdis.kper - 1

    @property
    def kstp(self):
        """
        Returns the current time step
        """
        return self.tdis.kstp - 1

    @property
    def nstp(self):
        """
        Returns the total number of time steps
        """
        return self.tdis.nstp

    @property
    def nper(self):
        """
        Returns the total number of stress periods
        """
        return self.tdis.nper

    @property
    def totim(self):
        """
        Returns the current model time
        """
        return self.tdis.totim

    @property
    def delt(self):
        """
        Returns the timestep length for the current time step
        """
        return self.tdis.delt

    def get_model(self, model_id=None):
        """
        Method to get a model from the simulation object by model name or
        subcomponent id

        Parameters
        ----------
        model_id : str, int
            model name (ex. "GWF_1") or subcomponent id (ex. 1)
        """
        if model_id is None:
            model_id = int(min([model.subcomponent_id for model in self.models]))

        if isinstance(model_id, int):
            for model in self.models:
                if model_id == model.subcomponent_id:
                    return model
            raise KeyError(f"No model found with subcomponent id {model_id}")

        elif isinstance(model_id, str):
            model_id = model_id.lower()
            if model_id in self._models:
                return self._models[model_id]
            raise KeyError(f"Model name {model_id} is invalid")

        else:
            raise TypeError("A string or int must be supplied to get model")

    def get_exchange(self, exchange_name=None):
        """
        Get a GWF-GWF "model" and all associated simulation level package
        data (ex. GNC, MVR)

        Parameters
        ----------
        exchange_name : str
            name of the GWF-GWF exchange package

        Returns
        -------
            modflowapi.extensions.ApiExchange object
        """
        if self.exchange_names is None:
            raise AssertionError("No exchanges are present in this simulation")

        if exchange_name is None:
            for _, exg in self._exchanges:
                return exg

        else:
            if exchange_name in self._exchanges:
                return self._exchanges[exchange_name]
            raise KeyError(f"Exchange name {exchange_name} is invalid")

    @staticmethod
    def load(mf6):
        """
        Method to load a modflowapi instance into the ApiSimulation extensions

        Parameters
        ----------
        mf6 : ModflowApi
            initialized ModflowApi object
        """
        variables = mf6.get_input_var_names()
        model_names = []
        for variable in variables:
            t = variable.split("/")
            if len(t) == 3:
                name = t[0]
                id_var_addr = mf6.get_var_address("ID", name)
                if name.startswith("SLN"):
                    continue
                if id_var_addr not in variables:
                    continue

                if name not in model_names:
                    model_names.append(name)

        models = {}
        for name in model_names:
            models[name.lower()] = ApiModel(mf6, name)

        solution_names = []
        for variable in variables:
            t = variable.split("/")
            if len(t) == 2:
                name = t[0]
                id_var_addr = mf6.get_var_address("ID", name)
                if name.lower() in models or name == "TDIS":
                    continue
                if id_var_addr not in variables:
                    continue

                solution_names.append(t[0])

        idp_names = [i for i in mf6.get_value("__INPUT__/SIM/NAM/SLNMNAMES")]
        solution_types = [
            i[:-1].lower()
            for ix, i in enumerate(mf6.get_value("__INPUT__/SIM/NAM/SLNTYPE"))
            if idp_names[ix]
        ]

        tmpmdl = ApiMbase(mf6, "", {})
        solution_names = list(set(solution_names))
        solution_dict = {}
        for name in solution_names:
            sid_var_addr = mf6.get_var_address("ID", name)
            sid = mf6.get_value(sid_var_addr)[0]
            slntype = solution_types[sid - 1]
            sln = ApiSlnPackage(tmpmdl, name, pkg_type=slntype)
            solution_dict[sid] = sln

        solutions = solution_dict

        # TDIS package construction
        tdis_constructor = package_factory("tdis", ScalarPackage)
        tdis = tdis_constructor(ScalarPackage, tmpmdl, "tdis", "tdis", sim_package=True)

        ats = None
        # ATS package construction
        for variable in variables:
            if variable.startswith("ATS"):
                ats_constructor = package_factory("ats", ListPackage)
                ats = ats_constructor(
                    ListPackage, tmpmdl, "ats", "ats", sim_package=True
                )
                break

        # get the exchanges
        exchange_names = []
        for variable in variables:
            if variable.startswith("GWF-GWF") or variable.startswith("GWT-GWT"):
                exchange_name = variable.split("/")[0]
                if exchange_name not in exchange_names:
                    exchange_names.append(exchange_name)

        # sim_packages: tdis, gwf-gwf, sln
        exchanges = {}
        for exchange_name in exchanges:
            exchange = ApiExchange(mf6, exchange_name)
            exchanges[exchange_name.lower()] = exchange

        return ApiSimulation(mf6, models, solutions, exchanges, tdis, ats)
