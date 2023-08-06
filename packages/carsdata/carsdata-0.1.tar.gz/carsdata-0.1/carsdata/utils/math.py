from math import pi
import numpy as np
try:
    import torch
    from torch import Tensor
    torch_imported = True
except ImportError:
    torch_imported = False
from carsdata.utils.types import Array


def sum_norm(x: Array, dim: int) -> Array:
    summ = x.sum(axis=dim, keepdims=True)
    summ[summ == 0] = 1
    return x / summ


if torch_imported:
    def sad(u: Tensor, v: Tensor, eps: float = 1e-6) -> Tensor:
        dot = torch.sum(u * v, dim=-1)
        norm = torch.linalg.vector_norm(u, dim=-1) * torch.linalg.vector_norm(v, dim=-1)
        norm = torch.maximum(norm, u.new_tensor(eps))
        res = torch.acos(dot / norm)
        return res

    def gaussian(nb_points: int, center_idx: int, width: int) -> Tensor:
        return 1. / (width * torch.sqrt(Tensor([2. * pi]))) * torch.exp(
            - (torch.arange(nb_points) - center_idx) ** 2 / (2. * width ** 2))
