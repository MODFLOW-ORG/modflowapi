import warnings

from .pakbase import AdvancedPackage

# Backward compatibility aliases
_DEPRECATED_NAMES = {
    "SfrPackage": AdvancedPackage,
    "SfrPakage": AdvancedPackage,  # preserved old typo spelling
    "LakPackage": AdvancedPackage,
    "MawPackage": AdvancedPackage,
    "UzfPackage": AdvancedPackage,
}


def __getattr__(name):
    if name in _DEPRECATED_NAMES:
        warnings.warn(
            f"{name} is deprecated and will be removed in a future release; use AdvancedPackage "
            "(or Package) from modflowapi.extensions.pakbase instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _DEPRECATED_NAMES[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
