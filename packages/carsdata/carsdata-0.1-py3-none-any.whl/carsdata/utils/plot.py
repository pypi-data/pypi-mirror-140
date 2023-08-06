"""
Module with help functions to plot results.

Functions
---------
plot_curves
    Plot curves with the ability to add vertical span to emphasize zones.
plot_mat
    Plot a matrix.
"""
from typing import Optional, Union, Sequence
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure
from cycler import cycler
from carsdata.utils.color_maps import RedColorMap
from carsdata.utils.types import ColorMap


def plot_curves(
    x: np.ndarray, y: np.ndarray, title: Optional[str] = None, legend: Optional[Sequence[str]] = None, yscale: str = 'linear',
    nb_legend: Optional[int] = None, x_label: Optional[str] = None, y_label: Optional[str] = None,
    vspan: Sequence[dict] = None, colors: Sequence[str] = None
) -> Figure:
    """Plot curves with the ability to add vertical span to emphasize zones.

    Parameters
    ----------
    x : np.ndarray
        1D array of x coordinates of plotted values.
    y : np.ndarray
        y coordinates of plotted values.
        If len(y.shape) > 2,
        2 last dimensions will be used to create new axes and each element will be used as other groups of curves.
    title : Optional[str], optional
        The figure title, by default None.
    legend : Optional[Sequence[str]], optional
        The legend, by default None.
    yscale : str, optional
        The scale used for y axis, by default 'linear'.
    nb_legend : Optional[int], optional
        The number of curves which legend is displayed. If None all are shown, by default None.
    x_label : Optional[str], optional
        Label of x axis, by default None.
    y_label : Optional[str], optional
        Label of y axis, by default None.
    vspan : Sequence[dict], optional
        Vertical span to display. Mandatories attributes are : begin, end and color. 
        The 2 firsts are the x coordinate of the vspan begin and end while the last is the color name.
        Supported colors are the one supported by matplotlib, by default None.
        Example : [{'begin': 50, 'end': 55, 'color': 'red'}]
    colors : Sequence[str], optional
        Curves colors names, default are the one used by matplotlib, by default None.

    Returns
    -------
    Figure
        The figure which contains the plots.
    """
    if legend is None:
        legend = []
    if nb_legend is None:
        nb_legend = len(legend)
    if vspan is None:
        vspan = []

    #plt.rc('font', size=22)
    #plt.rc('axes', titlesize=26)
    #plt.rc('axes', labelsize=24)
    #plt.rc('xtick', labelsize=22)
    #plt.rc('ytick', labelsize=22)
    #plt.rc('legend', fontsize=22)

    if len(y.shape) > 2 and (y.shape[-2] > 1 or y.shape[-1] > 1):
        fig, ax = plt.subplots(y.shape[-2], y.shape[-1])
        for idx, row in enumerate(ax):
            for idy, elem in enumerate(row):
                if colors is not None:
                    elem.set_prop_cycle(cycler(color=colors))
                lines = elem.plot(x, y[..., idx, idy], scalex=False)
                if x[0] > x[1]:
                    elem.set_xlim([np.ceil(x[0]), np.floor(x[-1])])
                else:
                    elem.set_xlim([np.floor(x[-1]), np.ceil(x[0])])
                for span in vspan:
                    elem.axvspan(span['begin'], span['end'], color=span['color'], alpha=0.2, ec=None)
                plt.yscale(yscale)
                if len(legend) > 0:
                    elem.legend((lines[:nb_legend])[::-1], (legend[:nb_legend])[::-1], loc='upper right')
                if title is not None:
                    plt.title(title)
                if x_label is not None:
                    elem.set_xlabel(x_label)
                if y_label is not None:
                    elem.set_ylabel(y_label)
                elem.set_yticklabels([])
    else:
        fig, ax = plt.subplots()
        if colors is not None:
            ax.set_prop_cycle(cycler(color=colors))
        lines = ax.plot(x, np.squeeze(y), scalex=False)
        if x[0] > x[1]:
            ax.set_xlim([np.ceil(x[0]), np.floor(x[-1])])
        else:
            ax.set_xlim([np.floor(x[-1]), np.ceil(x[0])])
        for span in vspan:
            ax.axvspan(span['begin'], span['end'], color=span['color'], alpha=0.2, ec=None)
        plt.yscale(yscale)
        if len(legend) > 0:
            ax.legend((lines[:nb_legend])[::-1], (legend[:nb_legend])[::-1], loc='upper right')
        if title is not None:
            fig.suptitle(title)
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)
        ax.set_yticklabels([])
    if title is not None:
        fig.canvas.manager.set_window_title(title)
    plt.axis('on')

    return fig


def plot_mat(
    mat: np.ndarray, title: Optional[str] = None, cmap: Optional[Union[str, ColorMap]] = None, colorbar: bool = False
) -> Figure:
    """Plot a matrix.

    Parameters
    ----------
    mat : np.ndarray
        The matrix to plot.
    title : Optional[str], optional
        The figure title, by default None..
    cmap : Optional[Union[str, ColorMap]], optional
        The used colormap, by default None.
    colorbar : bool, optional
        Set to true if you want to display the colorbar associated to the the colormap, by default False

    Returns
    -------
    Figure
        The figure which contains the plot.
    """
    if cmap is None:
        cmap = RedColorMap()
    fig = plt.figure()
    ax = plt.subplot(111)
    img = ax.matshow(mat, cmap=cmap)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    if colorbar:
        plt.colorbar(img, ax=ax)
    if title is not None:
        plt.title(title)
        fig.canvas.manager.set_window_title(title)
    return fig
