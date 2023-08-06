from carsdata.utils.common import factory
from torch import nn, Tensor
from carsdata.analyze.autoencoders import normalizer
from carsdata.utils.math import sum_norm


class SumNorm(nn.Module):
    dim: int

    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim

    def forward(self, x: Tensor) -> Tensor:
        return sum_norm(x, self.dim)


class SumNorm2d(nn.Module):
    """2d normalization with sum
    """
    def forward(self, x: Tensor) -> Tensor:
        return sum_norm(x, 1)


def normalizer_factory(name: str, **kwargs) -> nn.Module:
    return factory([normalizer, nn], name, **kwargs)
