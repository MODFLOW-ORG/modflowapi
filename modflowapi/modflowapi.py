from ctypes import byref, c_bool
from os import PathLike

from xmipy import XmiWrapper
from xmipy.utils import cd

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
        lib_path: str | PathLike,
        lib_dependency: str | None = None,
        working_directory: str = ".",
        timing: bool = False,
        logger_level: int | str = 0,
    ):
        super().__init__(
            amend_libmf6_path(lib_path),
            lib_dependency=lib_dependency,
            working_directory=working_directory,
            timing=timing,
            logger_level=logger_level,
        )
        self._has_ats_retry: bool | None = None

    @property
    def has_ats_retry(self) -> bool:
        """
        Whether the MODFLOW 6 library exposes adaptive time stepping
        retry routines (prepare_retryloop, start_retry, finish_retry).
        """
        if self._has_ats_retry is None:
            self._has_ats_retry = hasattr(self.lib, "prepare_retryloop")
        return self._has_ats_retry

    def prepare_retryloop(self) -> None:
        """
        Reset the ATS retry counter before running a timestep. Must be
        called once per timestep, before the first start_retry() call.
        """
        with cd(self.working_directory):
            self._execute_function(self.lib.prepare_retryloop)

    def start_retry(self) -> None:
        """
        Signal the start of a (re)try of the current timestep. If not
        the first attempt, timeseries input will be reevaluated. Must be
        called before prepare_solve() on all attempts, including the first.
        """
        with cd(self.working_directory):
            self._execute_function(self.lib.start_retry)

    def finish_retry(self) -> bool:
        """
        Check whether the current timestep is finished, or must be retried
        with a smaller delt. Must be called after finalize_solve().
        """
        finished = c_bool(False)
        with cd(self.working_directory):
            self._execute_function(self.lib.finish_retry, byref(finished))
        return finished.value
