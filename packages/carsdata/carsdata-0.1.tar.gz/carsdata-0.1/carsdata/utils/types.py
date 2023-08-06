"""
Module with types for hinting.

Types
-----
Real
    Type used for floating numbers.
Shape
    Type corresponding to an array shape.
Color
    Type corresponding to a RGB color in float.
ColorMap
    Type corresponding to color maps.
"""
from typing import Tuple, Sequence, Union
import numpy as np
from matplotlib.colors import Colormap
from carsdata import NN_LIB, OPTIONAL_PACKAGES
from carsdata.utils.errors import InvalidNameError
if OPTIONAL_PACKAGES[NN_LIB]:
    import torch


Real = np.float64
"""Define a floating number."""
Shape = Sequence[int]
"""Define an array shape."""
Color = Tuple[float, float, float]
"""Define a Color type as RGB float."""
ColorMap = Colormap
"""An alias for matplotlib color maps."""
if OPTIONAL_PACKAGES[NN_LIB]:
    Array = Union[np.array, torch.Tensor]
    """An alias for array. If pytorch is installed, can be numpy array or torch tensor."""

    DType = Union[np.dtype, torch.dtype]

    numpy_to_torch_dtype_dict = {
        bool: torch.bool,
        np.uint8: torch.uint8,
        np.int8: torch.int8,
        np.int16: torch.int16,
        np.int32: torch.int32,
        np.int64: torch.int64,
        np.float16: torch.float16,
        np.float32: torch.float32,
        np.float64: torch.float64,
        np.complex64: torch.complex64,
        np.complex128: torch.complex128
    }
    """From https://github.com/pytorch/pytorch/blob/e180ca652f8a38c479a3eff1080efe69cbc11621/torch/testing/_internal/common_utils.py#L349"""

    # Dict of torch dtype -> NumPy dtype
    torch_to_numpy_dtype_dict = {value: key for (key, value) in numpy_to_torch_dtype_dict.items()}
    """From https://github.com/pytorch/pytorch/blob/e180ca652f8a38c479a3eff1080efe69cbc11621/torch/testing/_internal/common_utils.py#L349"""

else:
    Array = np.array

    DType = np.dtype


def dtype_factory(name: str, api: str) -> DType:
    if OPTIONAL_PACKAGES[NN_LIB] and api == NN_LIB:
            dtype = getattr(torch, name, None)
    else:
        dtype = getattr(np, name, None)
    if dtype is None:
        raise InvalidNameError(name)
    else:
        return dtype
