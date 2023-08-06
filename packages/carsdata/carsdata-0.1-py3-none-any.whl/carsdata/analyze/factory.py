"""
Module with factories to instantiate analyzers.

Functions
---------
reducer_factory
    Construct a Reducer.
analyzer_factory
    Construct any kind of Analyzer.
"""
import carsdata.analyze.reducer as reducer
from carsdata.analyze.analyzer import Analyzer
from carsdata.analyze.reducer import Reducer
from carsdata.utils.common import factory


def reducer_factory(name: str, **kwargs) -> Reducer:
    """Factory to create Reducer instances.

    Parameters
    ----------
    name : str
        The class name.
    kwargs: Any
        Parameters to pass to the color map constructor.

    Returns
    -------
    Reducer
        The desired Reducer.
    """
    return factory(reducer, name, **kwargs)


def analyzer_factory(name: str, **kwargs) -> Analyzer:
    """Factory to create Analyzer instances.

    Parameters
    ----------
    name : str
        The class name.
    kwargs: Any
        Parameters to pass to the color map constructor.

    Returns
    -------
    Analyzer
        The desired Analyzer.
    """
    return reducer_factory(name, **kwargs)
