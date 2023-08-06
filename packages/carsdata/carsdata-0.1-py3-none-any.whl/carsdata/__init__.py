"""
Package that provide functions and classes to apply data analysis methods to CARS images.

Subpackages
-----------
analyze
    Provides data analysis classes and methods.
utils
    Provides utils functions and classes to plot, represent data, I/O,...
"""
import importlib as _importlib


def _check_packages(*args: str) -> dict:
    """Check if packages passed as arguments are installed

    Parameters
    ----------
    args : str
        Modules to search.

    Returns
    -------
    dict
        A dictionnary with packages names as keys and boolean indicating the presence as values.
    """
    installed_packages = {}
    for module in args:
        installed_packages[module] = _importlib.util.find_spec(module) is not None
    return installed_packages


NN_LIB = 'torch'
OPTIONAL_PACKAGES = _check_packages(NN_LIB)
