"""
Provides regression methods that can be used in MCR or Projection reducers.
At this time, only LinearRegression provided by pymcr package are available

Functions
---------
regressor_factory
    Construct LinearRegression instances.
"""
import sys
from pymcr import regressors
from pymcr.regressors import LinearRegression
from carsdata.utils.common import factory


def regressor_factory(name: str, **kwargs) -> LinearRegression:
    """Construct LinearRegression instances.

    Parameters
    ----------
    name : str
        The class name.
    kwargs : Any
        Parameters to pass to the regression algorithm constructor.

    Returns
    -------
    LinearRegression
        The desired LinearRegression instance.
    """
    return factory([sys.modules[__name__], regressors], name, **kwargs)
