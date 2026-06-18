from .apimodel import ApiMbase


class ApiExchange(ApiMbase):
    """
    ApiExchange class for GWF-GWF packages and container to access the
    simulation level GWF-GWF, MVR, and GNC packages

    Parameters
    ----------
    mf6 : ModflowApi
        initialized ModflowApi object
    name : str
        modflow exchange name. ex. "GWF-GWF_1"
    """

    def __init__(self, mf6, name):
        super().__init__(mf6, name)
