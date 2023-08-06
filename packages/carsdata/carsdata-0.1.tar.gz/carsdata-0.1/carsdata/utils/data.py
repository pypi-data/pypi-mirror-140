"""
Module defining class representing data.

Classes
-------
Data
    Base class of data composed of measures, positions and spectral units.
DataFile
    Derived class of Data, represents data stocked in a file.

Functions
---------
data_factory
    Factory to construct data instances.
"""
from os import read
import sys
from typing import Union, Optional, List, Iterable
import numpy as np
from numpy.typing import DTypeLike
from carsdata.utils.files import SUPPORTED_FILES, get_file_ext
from carsdata.utils.types import Real, Shape
from carsdata.utils.common import factory
from carsdata.utils.errors import InvalidExtensionError


class Data:
    """
    Represent CARS data with measures, positions and spectral units.
    Data are size fixed data but content can be changed.

    Parameters
    ----------
        measures : np.ndarray
            Data measures.
        pos : Optional[np.ndarray], optional
            Measures positions, by default None.
        spectral_units : Optional[np.ndarray], optional
            Measures spectral units, by default None.

    Attributes
    ----------
    measures (read-only)
    pos (read-only)
    spectral_units (read-only)
    shape (read-only)
    loaded (read-only)
    """
    _measures: np.ndarray
    _pos: Optional[np.ndarray]
    _spectral_units: Optional[np.ndarray]
    _loaded: bool

    def __init__(
        self, measures: np.ndarray, pos: Optional[np.ndarray] = None, spectral_units: Optional[np.ndarray] = None
    ) -> None:
        self._measures = measures
        self._pos = pos
        self._spectral_units = spectral_units
        self._loaded = True

    def __getitem__(self, item: Union[int, slice]) -> Union[Real, Iterable[Real]]:
        """Access to measures

        Parameters
        ----------
        item : Union[int, slice]
            Index or indices to access.

        Returns
        -------
        Union[Real, Iterable[Real]]
            The desired measures.
        """
        if not self._loaded:
            self.load()
        return self._measures[item]

    def __setitem__(self, key: Union[int, slice], value: Union[Real, Iterable[Real]]) -> None:
        """Change measures values.

        Parameters
        ----------
        key : Union[int, slice]
            Index or indices to change.
        value : Union[Real, Iterable[Real]]
            New values.
        """
        if not self._loaded:
            self.load()
        self._measures[key] = value

    def __len__(self) -> int:
        """Length of data is equivalent to length of measures

        Returns
        -------
        int
            Measures length.
        """
        return len(self._measures)

    def load(self) -> None:
        """
        Not used method.
        Use it in a derived class it if you have multiple data and just want to load on RAM only a part of it.
        """
        ...

    @property
    def measures(self) -> np.ndarray:
        """np.ndarray: Data measures (read-only)."""
        if not self._loaded:
            self.load()
        return self._measures

    @property
    def pos(self) -> Optional[np.ndarray]:
        """Optional[np.ndarray]: Measures positions, by default None (read-only)."""
        return self._pos

    @property
    def spectral_units(self) -> Optional[np.ndarray]:
        """Optional[np.ndarray]: Measures spectral units, by default None (read-only)."""
        return self._spectral_units

    @property
    def shape(self) -> Shape:
        """Shape: Measures shape (read-only)."""
        return self._measures.shape

    @property
    def loaded(self) -> bool:
        """bool: Indicate if data are loaded in RAM (read-only)."""
        return self._loaded


class DataFile(Data):
    """
    Class to represent data stocked in files. Data are not loaded until load() is called or an access to measures is attempted.

    Parameters
    ----------
    measures : Union[str, List[str]]
        Measures file or files.
    shape : Optional[Shape], optional
        Measures shape.
        If used, data files does not have position inside.
        If None, shape will be deduced from files, by default None.
    precision : DTypeLike, optional
        The precision used to load data, by default Real.
    """
    _files: Union[str, List[str]]
    _shape: Optional[Shape]

    def __init__(
        self, measures: Union[str, List[str]], shape: Optional[Shape] = None, precision: DTypeLike = Real
    ) -> None:
        super().__init__(np.zeros(1, dtype=precision))
        self._files = measures
        self._shape = shape
        self._loaded = False
        
    def load(self) -> None:
        """Load data files.

        Raises
        ------
        InvalidExtensionError
            Raised if file extension is not supported.
        """
        precision = self._measures.dtype
        pos = None
        if isinstance(self._files, str):
            file_ext = get_file_ext(self._files)
            read_function = SUPPORTED_FILES.get(file_ext, None)
            if read_function is None:
                raise InvalidExtensionError(file_ext)
            data, spectral_units, pos = read_function(self._files, self._shape, precision=precision)
        else:
            file_ext = get_file_ext(self._files[0])
            read_function = SUPPORTED_FILES.get(file_ext, None)
            if read_function is None:
                raise InvalidExtensionError(file_ext)
            data, spectral_units, pos = read_function(self._files[0], self._shape, precision=precision)
            data = data[np.newaxis, ...]
            if pos is not None:
                layer = np.zeros((*pos.shape[:-1], 1), dtype=pos.dtype)
                pos = np.concatenate((layer, pos), axis=-1)
                pos = pos[np.newaxis, ...]
            for idx, measure in enumerate(self._files[1:]):
                file_ext = get_file_ext(measure)
                read_function = SUPPORTED_FILES.get(file_ext, None)
                if read_function is None:
                    raise InvalidExtensionError(file_ext)
                data_tmp, _, pos_tmp = read_function(measure, self._shape, precision)
                data_tmp = data_tmp[np.newaxis, ...]
                data = np.concatenate((data, data_tmp), axis=0)
                if pos is not None:
                    layer = np.full((*pos_tmp.shape[:-1], 1), idx+1)
                    pos_tmp = np.concatenate((layer, pos_tmp), axis=-1)
                    pos_tmp = pos_tmp[np.newaxis, ...]
                    pos = np.concatenate((pos, pos_tmp), axis=0)
        self._measures = data
        self._spectral_units = spectral_units
        if pos is not None:
            self._pos = pos
        self._loaded = True


def data_factory(name: str, **kwargs) -> Data:
    """Factory to create Data instances.

    Parameters
    ----------
    name : str
        The class name.
    kwargs: Any
        Parameters to pass to the color map constructor.
    
    Returns
    -------
    Data
        An instance of Data or one of its derived classes.
    """
    return factory(sys.modules[__name__], name, **kwargs)
