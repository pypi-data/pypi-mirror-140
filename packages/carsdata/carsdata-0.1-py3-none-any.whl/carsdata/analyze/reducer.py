"""
Module that provides Reducer.
Reducer are dimensionality reduction methods.

Classes
-------
Reducer
    Base class for dimensionality reduction methods.
Simplisma
    Simplisma algorithm.
MCR
    Multivariate curve resolution algorithm.
Projection
    Project data onto a known library.
"""
from abc import ABC
from typing import Union, List, Optional
import numpy as np
from pymcr.mcr import McrAR
from pymcr.regressors import LinearRegression
import carsdata.utils.simplisma as simplisma
from carsdata.analyze.analyzer import Analyzer
import carsdata.analyze.factory as analyzer_facto
from carsdata.analyze.mcr.regressors import regressor_factory
from carsdata.analyze.mcr.constraints import constraint_factory, MCRConstraint


class Reducer(Analyzer, ABC):
    """Base class for dimensionality reduction methods.

    Parameters
    ----------
    output_dim : int
        The desired number of dimensions.

    Attributes
    ----------
    output_dim
    """
    _output_dim: int

    def __init__(self, output_dim: int) -> None:
        super().__init__()
        self._output_dim = output_dim

    @property
    def output_dim(self) -> int:
        """int: The desired number of dimensions."""
        return self._output_dim

    @output_dim.setter
    def output_dim(self, output_dim: int) -> None:
        self._output_dim = output_dim


class Simplisma(Reducer):
    """Simplisma algorithm. See the function simplisma in carsdata.utils.simplisma for details.

    Parameters
    ----------
    output_dim : int
        The desired number of dimensions.
    simp_err : float
        The error ratio used during Simplisma.

    Attributes
    ----------
        simp_err
    """
    _simp_err: float

    def __init__(self, output_dim: int, simp_err: float) -> None:
        super().__init__(output_dim)
        self._simp_err = simp_err

    def _analyze(self, data: np.ndarray) -> np.ndarray:
        s_guess = simplisma.simplisma(data, self.output_dim, self.simp_err)
        return s_guess

    @property
    def simp_err(self) -> float:
        """float: The error ratio used during Simplisma."""
        return self._simp_err

    @simp_err.setter
    def simp_err(self, simp_err: float) -> None:
        self._simp_err = simp_err


class MCR(Reducer):
    """Apply multivariate curve resolution based on pymcr implementation.

    Parameters
    ----------
    output_dim : int
        The desired number of dimensions.
    guesser : Union[Reducer, dict]
        The reducer method used to initialize spectra matrix. Can be an instance of a dictionnary representing this instance.
    c_regr : Union[LinearRegression, dict]
        The regression algorithm used to compute concentration matrix. Can be an instance of a dictionnary representing this instance.
    st_regr : Union[LinearRegression, dict]
        The regression algorithm used to compute spectra matrix. Can be an instance of a dictionnary representing this instance.
    c_constr : List[Union[MCRConstraint, dict]]
        The constraints applied to the concentrations after each regression. Each element of the list can be an instance or a dictionnary representing this instance.
    st_constr : Union[List[MCRConstraint], dict]
        The constraints applied to the spectra after each regression. Each element of the list can be an instance or a dictionnary representing this instance.

    Attributes
    ----------    
    spectra (read-only)
    guesser
    c_regr
    st_regr
    c_constr
    st_constr
    """
    _guesser: Reducer
    _mcrar = McrAR
    _error: Optional[np.ndarray]
    _lof: Optional[float]

    def __init__(
        self, output_dim: int, guesser: Union[Reducer, dict], c_regr: Union[LinearRegression, dict],
        st_regr: Union[LinearRegression, dict], c_constr: List[Union[MCRConstraint, dict]],
        st_constr: Union[List[MCRConstraint], dict]
    ) -> None:
        super().__init__(output_dim)
        if isinstance(guesser, dict):
            method_parameters = guesser['parameters']
            if method_parameters.get('output_dim') is None:
                method_parameters['output_dim'] = output_dim
            guesser = analyzer_facto.reducer_factory(guesser['name'], **method_parameters)
        if isinstance(c_regr, dict):
            c_regr = regressor_factory(c_regr['name'], **c_regr['parameters'])
        if isinstance(st_regr, dict):
            st_regr = regressor_factory(st_regr['name'], **st_regr['parameters'])
        for constr_idx, constraint in enumerate(c_constr):
            if isinstance(constraint, dict):
                c_constr[constr_idx] = constraint_factory(constraint['name'], **constraint['parameters'])
        for constr_idx, constraint in enumerate(st_constr):
            if isinstance(constraint, dict):
                st_constr[constr_idx] = constraint_factory(constraint['name'], **constraint['parameters'])
        
        self._guesser = guesser
        self._mcrar = McrAR(c_regr=c_regr, st_regr=st_regr, c_constraints=c_constr, st_constraints=st_constr)
        self._error = None
        self._lof = None

    def _analyze(self, data: np.ndarray) -> np.ndarray:
        shape_0 = np.prod(data.shape[:-1])
        data_2d = np.reshape(data, (shape_0, data.shape[-1]))
        s_guess = self._guesser.analyze(data_2d.T)
        self._mcrar.fit(data_2d, ST=s_guess.T)
        result = self._mcrar.C_opt_
        result_shape = list(data.shape)
        result_shape[-1] = result.shape[-1]
        result = np.reshape(result, result_shape)

        return result

    def _pretreatment(self, data: np.ndarray) -> None:
        super()._pretreatment(data)
        for constr in self._mcrar.c_constraints:
            constr.prepare(data)
        for constr in self._mcrar.st_constraints:
            constr.prepare(data)

    def _posttreatment(self, data: np.ndarray) -> None:
        shape_0 = np.prod(data.shape[:-1])
        data_2d = np.reshape(data, (shape_0, data.shape[-1]))

        result_2d = np.reshape(self.result, (shape_0, self.result.shape[-1]))

        reconstructed = result_2d @ self._mcrar.ST_opt_
        self._error = data_2d - reconstructed
        self._error = np.reshape(self._error, data.shape)
        self._lof = np.sum(self._error * self._error) / np.sum(data_2d * data_2d)

        self._error = np.reshape(self._error, data.shape)

    @Reducer.output_dim.setter
    def output_dim(self, output_dim: int) -> None:
        self._guesser.output_dim = output_dim
        self.output_dim = output_dim

    @property
    def spectra(self) -> Optional[np.ndarray]:
        """Optional[np.ndarray]: The computed spectra matrix (read-only)."""
        return self._mcrar.ST_opt_.T
    
    @property
    def error(self) -> Optional[np.ndarray]:
        return self._error

    @property
    def lof(self) -> Optional[float]:
        return self._lof

    @property
    def explained(self) -> Optional[float]:
        if self._lof is not None:
            return 1.-self._lof
        else:
            return None

    @property
    def guesser(self) -> Reducer:
        """Reducer: The reducer method used to initialize spectra matrix."""
        return self._guesser

    @guesser.setter
    def guesser(self, guesser: Reducer) -> None:
        if guesser.output_dim != self.output_dim:
            raise ValueError('The reducer used to obtain first spectra estimation should have the same number of dimension than MCR')
        self._guesser = guesser

    @property
    def c_regr(self) -> LinearRegression:
        """LinearRegression: The regression algorithm used to compute concentration matrix."""
        return self._mcrar.c_regressor

    @c_regr.setter
    def c_regr(self, c_regr: LinearRegression) -> None:
        self._mcrar.c_regressor = c_regr

    @property
    def st_regr(self) -> LinearRegression:
        """LinearRegression: The regression algorithm used to compute spectra matrix."""
        return self._mcrar.st_regressor

    @st_regr.setter
    def st_regr(self, st_regr: LinearRegression) -> None:
        self._mcrar.st_regressor = st_regr

    @property
    def c_constr(self) -> List[MCRConstraint]:
        """List[MCRConstraint]: The constraints applied to the concentrations after each regression."""
        return self._mcrar.c_constraints

    @c_constr.setter
    def c_constr(self, c_constr: List[MCRConstraint]) -> None:
        self._mcrar.c_constraints = c_constr

    @property
    def st_constr(self) -> List[MCRConstraint]:
        """List[MCRConstraint]: The constraints applied to the spectra after each regression."""
        return self._mcrar.st_constraints

    @st_constr.setter
    def st_constr(self, st_constr: List[MCRConstraint]) -> None:
        self._mcrar.st_constraints = st_constr


class Projection(Reducer):
    """Project data onto a known library using a linear regression algorithm.

    Parameters
    ----------
    spectra : Union[np.ndarray, str]
        The spectra used as a basis for the projection. Can be an array or a text file that contains spectra values.
    regression : Union[LinearRegression, dict]
        The regression algorithm used to project data. Can be an instance of a dictionnary representing this instance.
    constraints : List[Union[MCRConstraint, dict]]
        The constraints applied to the computed concentrations after projection. Each element of the list can be an instance or a dictionnary representing this instance.
    
    Attributes
    ----------
    spectra
    regression
    constraints
    """
    _spectra: np.ndarray
    _regression: LinearRegression
    _constraints: List[MCRConstraint]
    _error: Optional[np.ndarray]
    _lof: Optional[float]

    def __init__(
        self, spectra: Union[np.ndarray, str], regression: Union[LinearRegression, dict],
        constraints: List[Union[MCRConstraint, dict]]
    ) -> None:
        if isinstance(spectra, str):
            spectra = np.loadtxt(spectra)
        if isinstance(regression, dict):
            regression = regressor_factory(regression['name'], **regression['parameters'])
        for constr_idx, constraint in enumerate(constraints):
            if isinstance(constraint, dict):
                constraints[constr_idx] = constraint_factory(constraint['name'], **constraint['parameters'])
        self._spectra = spectra
        self._regression = regression
        self._constraints = constraints
        self._error = None
        self._lof = None
        super().__init__(self._spectra.shape[1])

    def _analyze(self, data: np.ndarray) -> np.ndarray:
        shape_0 = np.prod(data.shape[:-1])
        data_2d = np.reshape(data, (shape_0, data.shape[-1]))
        self.regression.fit(self.spectra, data_2d.T)
        result = self.regression.coef_
        for c in self.constraints:
            result = c.transform(result)

        result_shape = list(data.shape)
        result_shape[-1] = result.shape[-1]
        result = np.reshape(result, result_shape)
        return result

    def _pretreatment(self, data: np.ndarray) -> None:
        super()._pretreatment(data)
        for constr in self.constraints:
            constr.prepare(data)

    def _posttreatment(self, data: np.ndarray) -> None:
        shape_0 = np.prod(data.shape[:-1])
        data_2d = np.reshape(data, (shape_0, data.shape[-1]))

        result_2d = np.reshape(self.result, (shape_0, self.result.shape[-1]))

        reconstructed = result_2d @ self.spectra.T
        self._error = data_2d - reconstructed
        self._lof = np.sum(self._error * self._error) / np.sum(data_2d * data_2d)

        self._error = np.reshape(self._error, data.shape)
    
    @property
    def spectra(self) -> np.ndarray:
        """np.ndarray: The spectra used as a basis for the projection."""
        return self._spectra

    @spectra.setter
    def spectra(self, spectra: np.ndarray) -> None:
        self._spectra = spectra

    @property
    def regression(self) -> LinearRegression:
        """LinearRegression: The regression algorithm used to project data."""
        return self._regression

    @regression.setter
    def regression(self, regression: LinearRegression) -> None:
        self._regression = regression

    @property
    def constraints(self) -> List[MCRConstraint]:
        """List[MCRConstraint]: The constraints applied to the computed concentrations after projection."""
        return self._constraints

    @constraints.setter
    def constraints(self, constraints: List[MCRConstraint]) -> None:
        self._constraints = constraints

    @property
    def error(self) -> Optional[np.ndarray]:
        return self._error

    @property
    def lof(self) -> Optional[float]:
        return self._lof

    @property
    def explained(self) -> Optional[float]:
        if self._lof is not None:
            return 1.-self._lof
        else:
            return None
