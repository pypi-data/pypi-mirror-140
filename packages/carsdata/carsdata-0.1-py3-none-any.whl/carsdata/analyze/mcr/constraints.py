"""
Define Constraints compatible with pymcr package adding a prepare method to add information relative to input data.

Classes
-------
MCRConstraint
    Base class for Constraints with a prepare method.

NonNegativeConstraint
    Constraint that set to 0 all negative values.

NormConstraint
    Constraint that normalize data to sum to one.

ChanVeseConstraint
    Constraint that apply Chan-Sandberg-Vese algorithm and set to 0 values outside the segmentation.

Functions
---------
constraint_factory
    Construct MCRConstraint instances.
"""
import sys
from typing import Optional
import numpy as np
from pymcr.constraints import Constraint
from carsdata.utils.chan_sandberg_vese import chan_sandberg_vese
from carsdata.utils.common import factory
from carsdata.utils.errors import InvalidNameError
from carsdata.utils.types import Shape


class MCRConstraint(Constraint):
    """
    Constraint inheriting from pymcr ones adding a prepare method.
    Prepare method has to be implemented to add information about data that cannot be retreived when MCR is launched.
    """
    def __init__(self, copy: bool) -> None:
        super().__init__(copy)

    def prepare(self, data: np.ndarray) -> None:
        ...


class NonNegativeConstraint(MCRConstraint):
    """
    Constraint that set to 0 all negative values.

    Parameters:
    -----------
    copy : bool, optional
        If true, make copy of input data, otherwise, overwrite, by default False.
    """
    def __init__(self, copy: bool = False) -> None:
        super().__init__(copy)

    def transform(self, data: np.ndarray) -> np.ndarray:
        if self.copy:
            current = np.copy(data)
        else:
            current = data
        return current * (current > 0)


class NormConstraint(MCRConstraint):
    """
    Constraint that normalize data to sum to one along the specified axis.

    Parameters
    ----------
    axis : int
        Axis along to do the normalization.
    copy : bool, optional
        If true, make copy of input data, otherwise, overwrite, by default False.

    Attributes
    ----------
    axis
    """
    _axis: int

    def __init__(self, axis: int, copy: bool = False) -> None:
        super().__init__(copy)
        self._axis = axis
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        if self.copy:
            current = np.copy(data)
        else:
            current = data
        if self._axis == 0:
            sum_axis = current.sum(axis=self._axis)[None, :]
        else:
            sum_axis = current.sum(axis=self._axis)[:, None]
        sum_axis[sum_axis == 0] = 1
        current /= sum_axis
        return current

    @property
    def axis(self) -> int:
        """int: Axis along to do the normalization."""
        return self._axis

    @axis.setter
    def axis(self, axis: int) -> None:
        self._axis = axis


class ChanVeseConstraint(MCRConstraint):
    """
    Constraint that apply Chan-Sandberg-Vese algorithm and set to 0 values outside the segmentation.
    See the function chan_sandberg_vese in carsdata.utils.chan_sandberg_vese for details about the segmentation method.
    The prepare method stores spatial shape of data because MCR-ALS is applied on linearized data.
    This means that number of layers, lines and columns is lost during the MCR regression so we have to save it before starting the process.
    The implemented Chan-Sandberg-Vese method works only on images, so independant segmentation are done for each data layer.

    Parameters
    ----------
    mu : float
        Segmentation curve length penalty.
    nu : float
        Segmentation area length penalty.
    lambda1 : float
        Penalty of the inside class intravariance.
    lambda2 : float
        Penalty of the outside class intravariance.
    copy : bool, optional
        If true, make copy of input data, otherwise, overwrite, by default False.

    Attributes
    ----------
    mu
    nu
    lambda1
    lambda2
    """
    _mu: float
    _nu: float
    _lambda1: float
    _lambda2: float
    _image_dim: Optional[Shape]

    def __init__(self, mu: float, nu: float, lambda1: float, lambda2: float, copy: bool = False) -> None:
        super().__init__(copy)
        self._mu = mu
        self._nu = nu
        self._lambda1 = lambda1
        self._lambda2 = lambda2

    def prepare(self, data: np.ndarray) -> None:
        self._image_dim = data.shape[:-1]

    def transform(self, data: np.ndarray) -> np.ndarray:
        if self.copy:
            current = np.copy(data)
        else:
            current = data
        img_dim = list(self._image_dim)
        if len(img_dim) == 2:
            img_dim = [1] + img_dim
        img_dim.append(data.shape[-1])
        img_dim = tuple(img_dim)
        img = current.reshape(img_dim)
        res = np.zeros(img_dim)
        for idx, layer in enumerate(img):
            seg = chan_sandberg_vese(layer, mu=self._mu, nu=self._nu, lambda1=self._lambda1, lambda2=self._lambda2)
            rep_seg = np.repeat(seg, img.shape[-1])
            rep_seg = rep_seg.reshape(img.shape)
            res[idx] = layer * rep_seg
        return np.reshape(res, data.shape)

    @property
    def mu(self) -> float:
        """float: Segmentation curve length penalty."""
        return self._mu
    
    @mu.setter
    def mu(self, mu: float) -> None:
        self._mu = mu
    
    @property
    def nu(self) -> float:
        """float: Segmentation curve area penalty."""
        return self._mu
    
    @nu.setter
    def nu(self, nu: float) -> None:
        self._nu = nu

    @property
    def lambda1(self) -> float:
        """float: Penalty of the inside class intravariance."""
        return self._lambda1
    
    @lambda1.setter
    def lambda1(self, lambda1: float) -> None:
        self._lambda1 = lambda1
    
    @property
    def lambda2(self) -> float:
        """float: Penalty of the outside class intravariance."""
        return self._lambda2
    
    @lambda2.setter
    def lambda2(self, lambda2: float) -> None:
        self._lambda2 = lambda2


def constraint_factory(name: str, **kwargs) -> MCRConstraint:
    """Construct MCRConstraint instances.

    Parameters
    ----------
    name : str
        The class name.
    kwargs : Any
        Parameters to pass to the constraint constructor.

    Returns
    -------
    MCRConstraint
        The desired MCRConstraint instance.
    """
    return factory(sys.modules[__name__], name, **kwargs)
