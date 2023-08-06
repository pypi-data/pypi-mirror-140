from typing import List
import numpy as np
import torch
from torch import Tensor
from carsdata.utils.types import Array


def convert_to_tensor(*args: Array) -> List[Tensor]:
    """Convert Arrays to Tensor. 

    Parameters
    ----------
    args : Array
        Arrays to convert.

    Returns
    -------
    List[Tensor]
        The converted array
    """
    res = []
    for array in args:
        if isinstance(array, np.ndarray):
            array = torch.from_numpy(array)
        res.append(array)
    return res