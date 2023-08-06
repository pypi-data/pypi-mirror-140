"""
Module with factories to instantiate autoencoders. Pytorch is required.

Functions
---------
unmixing_factory
    Construct a pytorch model based autoencoder.
"""
from torch.nn import Module
from carsdata.analyze.autoencoders import unmixing
from carsdata.utils.common import factory


def unmixing_factory(name: str, **kwargs) -> Module:
    """Factory to create a pytorch based autoencoder for unmixing.

    Parameters
    ----------
    name : str
        The class name.
    kwargs: Any
        Parameters to pass to the constructor.

    Returns
    -------
    Reducer
        The desired Module.
    """
    return factory(unmixing, name, **kwargs)
