from xmipy import XmiWrapper

from .util import amend_libmf6_path


class ModflowApi(XmiWrapper):
    """
    This class extends eXtended Model Interface (XMI) Wrapper (XmiWrapper)
    for the MODFLOW API. XMI extends the CSDMS Basic Model Interface

    The extension to the XMI does not change anything in the XMI or BMI
    interfaces, so models implementing the ModflowApi interface is compatible
    with the XmiWrapper which provides XMI and BMI functionality.

    """

    def __init__(
        self,
        lib_path: str,
        lib_dependency: str = None,
        working_directory: str = ".",
        timing: bool = False,
    ):
        super().__init__(
            amend_libmf6_path(lib_path),
            lib_dependency=lib_dependency,
            working_directory=working_directory,
            timing=timing,
        )
