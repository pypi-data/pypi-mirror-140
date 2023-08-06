"""
Module with functions to create colors represented by 3 floats tuples.

Functions
---------
red
    Create a red color.
green
    Create a green color.
blue
    Create a blue color.
yellow
    Create a yellow color.
white
    Create a white color.
black
    Create a black color.
"""
from carsdata.utils.types import Color


def red() -> Color:
    """Create a red color tuple.

    Returns
    -------
    Color
        A tuple representing the red color.
    """
    return 1., 0., 0.


def green() -> Color:
    """Create a green color tuple.

    Returns
    -------
    Color
        A tuple representing the green color.
    """
    return 0., 1., 0.


def blue() -> Color:
    """Create a blue color tuple.

    Returns
    -------
    Color
        A tuple representing the blue color.
    """
    return 0., 0., 1.


def yellow() -> Color:
    """Create a yellow color tuple.

    Returns
    -------
    Color
        A tuple representing the yellow color.
    """
    return 1., 1., 0.


def white() -> Color:
    """Create a white color tuple.

    Returns
    -------
    Color
        A tuple representing the white color.
    """
    return 1., 1., 1.


def black() -> Color:
    """Create a black color tuple.

    Returns
    -------
    Color
        A tuple representing the black color.
    """
    return 0., 0., 0.