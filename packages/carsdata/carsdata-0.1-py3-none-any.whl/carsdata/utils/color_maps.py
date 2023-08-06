"""
Module with classes and functions to create matplotlib color maps.

Clases
------
ColoredColorMap
    Color map class that goes from black to a chosen color.
RedColorMap
    ColoredColorMap that goes from black to red.
GreenColorMap
    ColoredColorMap that goes from black to green.
BlueColorMap
    ColoredColorMap that goes from black to blue.
whiteColorMap
    ColoredColorMap that goes from black to white.

Functions
---------
reverse_cmap
    function that reverse the colors of a listed color map.
cmap_factory
    Factory to construct ColorMap instances.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from carsdata.utils import colors
from carsdata.utils.common import factory
from carsdata.utils.types import ColorMap, Color


class ColoredColorMap(ListedColormap):
    """
    Listed color map varying from black to a specified color.
    Each color in the list is computed using a linear interpolation.

    Parameters
    ----------
    rgb : Color
        The color for the highest intensity.
    nb_points : int, optional
        The number of colors in the color map, by default 256
    """
    def __init__(self, rgb: Color, nb_points: int = 256) -> None:
        vals = np.ones((nb_points, 4))
        vals[:, 0] = np.linspace(0, rgb[0], nb_points)
        vals[:, 1] = np.linspace(0, rgb[1], nb_points)
        vals[:, 2] = np.linspace(0, rgb[2], nb_points)
        super().__init__(vals)


class RedColorMap(ColoredColorMap):
    """A Color map varying from black to red."""
    def __init__(self) -> None:
        super().__init__(colors.red())


class GreenColorMap(ColoredColorMap):
    """A Color map varying from black to green."""
    def __init__(self) -> None:
        super().__init__(colors.green())


class BlueColorMap(ColoredColorMap):
    """A Color map varying from black to blue."""
    def __init__(self) -> None:
        super().__init__(colors.blue())


class WhiteColorMap(ColoredColorMap):
    """A Color map varying from black to white."""
    def __init__(self) -> None:
        """Constructor"""
        super().__init__(colors.white())


def reverse_cmap(cmap: ListedColormap) -> ListedColormap:
    """Create a ListedColorMap where the list of color is the reverse of the input one.

    Parameters
    ----------
    cmap : ListedColormap
        ListedColormap to reverse.

    Returns
    -------
    ListedColormap
        The new colormap with colors reversed.
    """
    return ListedColormap(cmap.colors[::-1])


def cmap_factory(name: str, **kwargs) -> ColorMap:
    """
    Factory to construct ColorMap instances. First look if the name is a matplotlib color map name.
    If not, look if it's the one of the application.

    Parameters
    ----------
    name : str
        The class name.
    kwargs: Any
        Parameters to pass to the color map constructor.

    Returns
    -------
    ColorMap
        The desired color map constructed with parameters in kwargs.
    """
    if name in plt.colormaps():
        return plt.get_cmap(name)
    else:
        return factory(sys.modules[__name__], name, **kwargs)
