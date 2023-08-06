import torch
from torch.optim import Optimizer
from carsdata.utils.common import factory


def optimizer_factory(name: str, **kwargs) -> Optimizer:
    return factory(torch.optim, name, **kwargs)
