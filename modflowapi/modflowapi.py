from ctypes import (
    byref,
    c_char_p,
    c_int,
    create_string_buffer,
)
from typing import Tuple
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
        logger_level: int | str = 0,
    ):
        super().__init__(
            amend_libmf6_path(lib_path),
            lib_dependency=lib_dependency,
            working_directory=working_directory,
            timing=timing,
            logger_level=logger_level,
        )

    def get_attrs_item_count(self) -> int:
        count = c_int(0)
        self.execute_function(self.lib.get_attrs_item_count, byref(count))
        return count.value

    def get_attrs_keys(self) -> Tuple[str]:
        len_attr_name = self.get_constant_int("BMI_LENATTRNAME")
        nr_output_vars = self.get_attrs_item_count()
        len_names = nr_output_vars * len_attr_name
        names = create_string_buffer(len_names)

        # get a (1-dim) char array (char*) containing the output variable
        # names as \x00 terminated sub-strings
        self.execute_function(self.lib.get_attrs_keys, byref(names))

        # decode
        output_vars = [
            names[i * len_attr_name : (i + 1) * len_attr_name]
            .split(b"\0", 1)[0]
            .decode("ascii")
            for i in range(nr_output_vars)
        ]
        return tuple(output_vars)

    def get_var_attrs(self, name: str) -> Tuple[str]:
        len_attr_name = self.get_constant_int("BMI_LENATTRNAME")
        nr_output_vars = self.get_attrs_item_count()
        len_attrs = nr_output_vars * len_attr_name
        attrs = create_string_buffer(len_attrs)

        # get a (1-dim) char array (char*) containing the output variable
        # names as \x00 terminated sub-strings
        self.execute_function(
            self.lib.get_var_attrs,
            c_char_p(name.encode()),
            byref(attrs),
            detail="for variable " + name
        )

        # decode
        output_vars = [
            attrs[i * len_attr_name : (i + 1) * len_attr_name]
            .split(b"\0", 1)[0]
            .decode("ascii")
            for i in range(nr_output_vars)
        ]

        return tuple(output_vars)
