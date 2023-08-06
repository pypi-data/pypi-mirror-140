"""
Module that define classes that can be used to evaluate results.

Classes
-------
Metric
    Abstract base class to inherit to define a new metric.
LOF
    Class that computes the lack of fit between results and input data.

Functions
---------
metric_factory
    Factory to create Metric instances.
"""
import sys
from abc import ABC, abstractmethod
from typing import Any
import numpy as np
from carsdata import OPTIONAL_PACKAGES, NN_LIB
import carsdata
from carsdata.utils.types import Real, Array
from carsdata.utils.common import factory


class Metric(ABC):
    """
    Abstract base class to inherit to define a new metric.
    Implement compute method with the desired behavior of your metric.
    """

    @abstractmethod
    def compute(
        self, data: Array, result: Array
    ) -> Any:
        """Abstract method to use to implement the metric.

        Parameters
        ----------
        data : Array
            The data that should be the truth.
        result : Array
            The array to compare to data.

        Returns
        -------
        Any
            The metric result.
        """
        ...


class LOF(Metric):
    """
    Class computing the lack of fit (LOF) between results and input data.
    Lack of fit is defined as the sum of the squared error matrix (error being the difference between data and results),
    divided by the sum of the squared data matrix.
    Except the last dimension, data and result must have the same shape.
    """
    def compute(
        self, data: Array, result: Array
    ) -> Real:
        """
        Compute the lack of fit between data and result.
        First dimensions are spatial ones and last is the spectral one

        Parameters
        ----------
        data : Array
            The input data.
        result : Array
            The reconstruted matrix.

        Returns
        -------
        Real
            The LOF
        """
        data_shape = list(data.shape)
        shape_0 = data_shape[0]
        for idx in range(1, len(data_shape) - 1):
            shape_0 *= data_shape[idx]
        data_2d = data.reshape(shape_0, data_shape[-1])

        result_2d = result.reshape(shape_0, result.shape[-1])

        error = data_2d - result_2d
        return ((error * error).sum() / (data_2d * data_2d).sum()).item()


def metric_factory(name: str, **kwargs) -> Metric:
    """Factory to create Metric instances.

    Parameters
    ----------
    name : str
        The class name.
    kwargs: Any
        Parameters to pass to the color map constructor.

    Returns
    -------
    Metric
        The desired Metric.
    """
    modules = [sys.modules[__name__]]
    if OPTIONAL_PACKAGES[NN_LIB]:
        from carsdata.utils.torch import metrics as torch_metrics
        modules.append(torch_metrics)
    return factory(modules, name, **kwargs)
