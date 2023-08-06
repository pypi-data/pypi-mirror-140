"""
Module with functions to interact with files.

Constants:
----------
SUPPORTED_FILES
    A dictionnary with keys corresponding to supported extensions for data file and values functions to read it.

Functions
---------
read_txt_file
    Read a text file holding data.
get_file_ext
    Return the extestion of a file.
get_data_files
    Get recursively all data files present in a directory.
read_json
    Read a JSON file or eval a string representing a json dictionnary.
write_json
    Write a dictionnary into a JSON file.
"""
import os
from typing import Tuple, Dict, Optional, List, Sequence
import json
import numpy as np
from carsdata.utils.common import get_shape
from carsdata.utils.types import Real, Shape, DType


def _recurse_txt_loading(
    path: str, begin: Shape, end: Shape, data_shape: Shape, pos_len: int, spectral_range: [Tuple[int, int]],
    idx: Tuple[int, ...], precision: DType
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Load recursively data from a text file to load only a part of data stocked in the file.
    Iterate over each value between begin and end for each dimension until be at the dimension
    where end[dim]-begin[dim] == data_shape[dim] to load lines.
    Parameters
    ----------
    path : str
        File path.
    begin : Shape
        First index to load.
    end : Shape
        Last index to load (exclude).
    data_shape : Shape
        Data spatial shape (shape of the complete data volume).
    pos_len: int
        The number of element at each position.
    spectral_range: Tuple[int, int]
        The first and last index of the spectral measures to read.
    idx : Tuple[int, ...]
        Current index of data to load
    precision : DType
        The precision to use to load data.
    Returns
    -------
    Tuple[np.ndarray, Optional[np.ndarray]]
        A tuple with first element is measures and last positions if present in the file.
    """
    data = None
    pos = None
    delta = np.array([end[i] - begin[i] for i in range(len(data_shape))])
    diff_values = np.nonzero(np.array(data_shape) - delta)[0]
    if len(idx) == diff_values[-1]:  # read data
        linearized_begin = 0
        for i in range(len(idx)):
            offset = 1 if i == len(data_shape)-1 else np.cumprod(data_shape[i+1:])[-1]
            linearized_begin += idx[i] * offset
        for i in range(len(idx), len(data_shape)):
            offset = 1 if i == len(data_shape) - 1 else np.cumprod(data_shape[i+1:])[-1]
            linearized_begin += begin[i] * offset
        nb_elems = delta[-1]
        if (len(idx)+1) < len(data_shape):
            nb_elems += np.cumprod(data_shape[len(idx)+1:len(data_shape)])[-1]
        data = np.loadtxt(path, dtype=precision, skiprows=1+linearized_begin, max_rows=nb_elems,
                          usecols=range(pos_len+spectral_range[0], pos_len+spectral_range[1]))
        if pos_len != 0:
            pos = np.loadtxt(path, dtype=precision, skiprows=1+linearized_begin, max_rows=nb_elems,
                             usecols=range(pos_len))
    else:  # recursively
        for curr_idx in range(begin[len(idx)], end[len(idx)]):
            data_idx = *idx, curr_idx
            loaded_data, loaded_pos = _recurse_txt_loading(path, begin, end, data_shape, pos_len, spectral_range,
                                                           data_idx, precision)
            if data is None:
                data = loaded_data
            else:
                data = np.concatenate((data, loaded_data))
            if loaded_pos is not None:
                if pos is None:
                    pos = loaded_pos
                else:
                    pos = np.concatenate((pos, loaded_pos))
    return data, pos


def read_txt_file(
    path: str, shape: Optional[Shape] = None, begin: Shape = 0, nb_measures: Optional[Shape] = None,
    spectral_range: Optional[Tuple[int, int]] = None, precision: DType = Real, verbose: bool = False
) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """
    Read a text file holding data and return measures, wavelength and positions if available.
    Spatial shape is deduced from shape if not None, otherwise it is deduced from the data file. 

    Parameters
    ----------
    path : str
        File path.
    shape : Optional[Shape], optional
        Spatial shape of measures.
        Use it if positions are not in the file but measures are spatially organized,
        by default None.
    begin : Shape, optional
        First measure to read in the file,
        by default 0
    nb_measures: Optional[Shape], optional
        Number of measures to read from begin. If None, all data until the end, by default None.
    spectral_range: Optional[Tuple[int, int]], optional
        The first and last index of the spectral measures to read. If None all are read, by default None.
    precision : DType, optional
        The precision to use to load data, by default Real.
    verbose : bool, optional
        If True, print the path file before loading, by default False.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]
        A tuple with first element is measures, second spectral units and last positions.
    """
    if verbose:
        print(f'Load {path}')
    pos = None
    spectral_units = np.loadtxt(path, dtype=precision, max_rows=1)
    if spectral_range is None:
        spectral_range = 0, len(spectral_units)
    second_line = np.loadtxt(path, dtype=precision, skiprows=1, max_rows=1)
    pos_len = second_line.shape[0] - spectral_units.shape[0]
    if pos_len == 0:  # no positions are present in the file
        if shape is None:
            data_shape = (len(np.loadtxt(path, dtype=precision, skiprows=1, usecols=0)),)
        else:
            data_shape = shape
    else:  # first columns are positions
        pos = np.loadtxt(path, dtype=precision, skiprows=1, usecols=range(pos_len))
        data_shape = get_shape(pos)
    if nb_measures is not None:  # we want to load only a part of data
        if tuple(nb_measures) == tuple(data_shape):
            data = np.loadtxt(path, dtype=precision, skiprows=1, usecols=range(pos_len + spectral_range[0],
                                                                               pos_len + spectral_range[1]))
            if pos_len != 0:
                pos = np.loadtxt(path, dtype=precision, skiprows=1, usecols=range(pos_len))
            final_spatial_shape = data_shape
        else:
            if begin == 0:  # transform into a tuple of the same size of nb_measures
                begin = (0 for _ in range(len(nb_measures)))
            end = np.array(begin) + np.array(nb_measures)
            data, pos = _recurse_txt_loading(path, begin, end, data_shape, pos_len, spectral_range, (), precision)
            final_spatial_shape = nb_measures
    else:  # we want to load until the end
        first_index = 0
        if begin != 0:  # we want to skip data so we compute the begin index
            for i in range(len(data_shape)):
                offset = 1 if i == len(data_shape) - 1 else np.cumprod(data_shape[i + 1:])[-1]
                first_index += begin[i] * offset
        data = np.loadtxt(path, dtype=precision, skiprows=1+first_index,
                          usecols=range(pos_len+spectral_range[0], pos_len+spectral_range[1]))
        if begin != 0:
            final_spatial_shape = tuple(map(tuple, np.array(data_shape) - np.array(begin)))
        else:
            final_spatial_shape = data_shape
        if pos_len != 0:
            pos = np.loadtxt(path, dtype=precision, skiprows=1+first_index, usecols=range(pos_len))
    data = np.reshape(data, (*final_spatial_shape, spectral_range[1]-spectral_range[0]))
    if pos is not None:
        pos = np.reshape(pos, (*final_spatial_shape, pos_len))
    return data, spectral_units[spectral_range[0]:spectral_range[1]], pos


def get_spectral_units_txt(path: str, precision: DType = Real) -> np.ndarray:
    """
    Get spectral units from a CARS data text file (first line of the file).
    Parameters
    ----------
    path : str
        The file path.

    precision : DType, optional
        The precision to use to load data, by default Real.

    Returns
    -------
    np.ndarray
        An array which content is file data spectral units.
    """
    return np.loadtxt(path, dtype=precision, max_rows=1)


def get_file_ext(file: str) -> str:
    """Get the extension of the specified file path.

    Parameters
    ----------
    file : str
        The file path.

    Returns
    -------
    str
        The file path extension.
    """
    return file.split('.')[-1]


def get_data_files(directory: str, exclude_directories: Optional[List[str]] = None) -> List[str]:
    """
    Get recursively all data files present in a directory.
    Data files are files with a supported extension.

    Parameters
    ----------
    directory : str
        Directory path.
    exclude_directories : Optional[List[str]], optional
        Directories to exclude from the search, by default None.

    Returns
    -------
    List[str]
        A list with the path of all found data files.
    """
    data_files = []
    for root, dirs, files in os.walk(directory):
        if exclude_directories is not None and root in exclude_directories:
            continue
        for file in files:
            file_ext = get_file_ext(file)
            if file_ext in SUPPORTED_FILES.keys():
                data_files.append(os.path.join(root, file))
    return data_files


def read_json(path: str, encoding: str = 'utf-8') -> Dict:
    """Read a JSON file or eval a string representing a json dictionnary.

    Parameters
    ----------
    path : str
        The file path or dictionnary string to eval.
    encoding : str, optional
        The file encoding, by default 'utf-8'.

    Returns
    -------
    Dict
        A dict corresponding to the JSON file or evaluated string.
    """
    if os.path.isfile(path):
        with open(path, encoding=encoding) as f:
            return json.load(f)
    else:
        return eval(path)


def write_json(path: str, json_tree: Dict, indent: Optional[int] = None, encoding: str = 'utf-8'):
    """Write a dictionnary into a JSON file.

    Parameters
    ----------
    path : str
        The path where write the file.
    json_tree : Dict
        The dictionnary to write.
    indent : Optional[int], optional
        The indentation used in the file, by default None.
    encoding : str, optional
        The file encoding, by default 'utf-8'.
    """
    with open(path, 'w', encoding=encoding) as f:
        json.dump(json_tree, f, indent=indent, default=lambda o: o.__dict__)


SUPPORTED_FILES = {
    'txt': read_txt_file
}
"""
A dictionnary with keys corresponding to supported extensions for data file and values functions to read it.
Only text file are supported for the moment.
"""