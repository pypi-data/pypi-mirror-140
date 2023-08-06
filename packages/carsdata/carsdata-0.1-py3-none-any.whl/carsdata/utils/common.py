"""
Module with diverse functions to select file or directory, normalize spectra and a factory method.

Functions
---------
factory
    Return an instance of an object based on a getattr function.
normalize_spectra
    Normalize spectra with adding an offset to prepare to visualization.
get_shape
    Compute data spatial shape from file path or positions.
select_file
    Open a dialog to select a file.
select_dir
    Open a dialog to select a directory.
"""
import importlib
from typing import Union, Iterable
import numpy as np
import tkinter as tk
from tkinter import filedialog
from carsdata.utils.errors import InvalidNameError
from carsdata.utils.types import Shape


def factory(modules: Union[object, Iterable[object]], obj_name: str, **kwargs) -> object:
    """
    Function to implement factory based on the getattr builtin function.
    Return the first object matching with obj_name in modules.

    Parameters
    ----------
    modules : Iterable[object]
        Iterable of searched modules. The order matters, first object matching is returned.
    obj_name : str
        The object name.

    Returns
    -------
    object
        An instance of obj_name.

    Raises
    ------
    InvalidNameError
        Raised if no attribute in modules matches with obj_name.
    """
    obj = None
    if not hasattr(modules, '__iter__'):
        modules = [modules]
    for module in modules:
        obj = getattr(module, obj_name, None)
        if obj is not None:
            break
    if obj is None:
        raise InvalidNameError(obj_name)
    return obj(**kwargs)


def normalize_spectra(spectra: np.ndarray, offset: float = 0.1) -> np.ndarray:
    """
    Normalize spectra along columns.
    A small offset is set between each spectrum to avoid overlapping and prepare to visualization.

    Parameters
    ----------
    spectra : np.ndarray
        Spectra to normalize.
    offset : float, optional
        The offset between each spectrum, by default 0.1

    Returns
    -------
    np.ndarray
        Normalized spectra with an offset between each spectrum.
    """
    normalized_spectra = np.zeros(spectra.shape)
    for idx, spectr in enumerate(spectra.T):
        min_value = spectr.min()
        max_value = spectr.max()
        max_previous = normalized_spectra[:, idx - 1].max() if idx != 0 else 0
        normalized_spectra[:, idx] = (spectr - min_value) / (max_value - min_value) + (max_previous + offset)
    return normalized_spectra


def get_shape(data: Union[str, np.ndarray]) -> Shape:
    """Compute data spatial shape from file path or positions.

    Parameters
    ----------
    data : Union[str, np.ndarray]
        The positions

    Returns
    -------
    Shape
        Data spatial shape.
    """
    if isinstance(data, str):
        spectral_units = np.loadtxt(data, max_rows=1)
        second_line = np.loadtxt(data, skiprows=1, max_rows=1)
        pos_len = second_line.shape[0] - spectral_units.shape[0]
        pos = np.loadtxt(data, skiprows=1, usecols=range(pos_len))
    else:
        pos = data
    shape = []
    for dim in pos.T:
        shape.append(np.unique(dim).shape[0])
    return tuple(shape)


def select_file(title_name: str = 'Open') -> str:
    """Open a dialog to select a file and return the selected file path.
    Parameters
    ----------
    title_name : str, optional
        Window name, by default 'Open'.

    Returns
    -------
    str
        The selected file path.
    """
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(title=title_name)
    root.destroy()
    return file


def select_dir(title_name: str = 'Open') -> str:
    """Open a dialog to select a directory and return the selected directory path.

    Parameters
    ----------
    title_name : str, optional
        Window name, by default 'Open'.

    Returns
    -------
    str
        The selected directory path.
    """
    root = tk.Tk()
    root.withdraw()
    dir_path = filedialog.askdirectory(title=title_name)
    root.destroy()
    return dir_path
