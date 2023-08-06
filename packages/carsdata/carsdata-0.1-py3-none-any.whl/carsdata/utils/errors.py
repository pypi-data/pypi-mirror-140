"""
Module with Errors raised by the package.

Classes
-------
InvalidNameError
    Raised when a name used passed in a factory is not recognized.
InvalidExtensionError
    Raised when the extension of a file is not supported.
IncompatibleShapeError
    Raised when the shape of an array is not compatible with the shape of an other when it should.
"""
from struct import pack
from typing import Sequence, Union

class InvalidNameError(ValueError):
    """Error raised when a name used passed in a factory is not recognized.

    Parameters
    ----------
    name : str
        The unrecognized name.
    """
    def __init__(self, name: str) -> None:
        super().__init__(f'{name} is not valid name')


class InvalidExtensionError(ValueError):
    """Error raised when the extension of a file is not supported.

    Parameters
    ----------
    extension : str
        The not supported extension.
    """
    def __init__(self, extension: str) -> None:
        super().__init__(f'{extension} is not a supported file extension')


class IncompatibleShapeError(ValueError):
    """Error raised when the shape of an array is not compatible with the shape of an other when it should.

    Parameters
        ----------
        invalid_shape : Sequence[int]
            The invalid shape.
        other_shape : Sequence[int]
            The shape that it should be compatible with.
    """
    def __init__(self, invalid_shape: Sequence[int], other_shape: Sequence[int]) -> None:
        super().__init__(f'{invalid_shape} is incompatible with shape {other_shape}')


class PackageRequiredError(NotImplementedError):
    def __init__(self, packages: Union[str, Sequence[str]]):
        if isinstance(packages, str):
            packages = [packages]
        packages_str = f'Packages are missing to use this feature: {packages[0]}'
        for package in packages[1:]:
            packages_str += f', {package}'
        super().__init__(packages_str)
