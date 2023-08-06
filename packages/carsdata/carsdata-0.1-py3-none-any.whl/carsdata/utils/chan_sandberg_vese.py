"""
Chan-Sandberg-Vese [1], i.e. Chan-Vese for vector valued image, implementation is a modified version of scikit-image Chan-Vese implementation.
see: https://github.com/scikit-image/scikit-image/blob/v0.18.0/skimage/segmentation/_chan_vese.py for original source code.

Functions
---------
chan_sandberg_vese
    Segment a vector valued image using Chan-Sandberg-Vese method.

References
----------
[1] Chan, T. F., Sandberg, B. Y., & Vese, L. A. (2000). Active contours without edges for vector-valued images. Journal of Visual Communication and Image Representation, 11(2), 130-141.
"""
from typing import Union, Tuple
import numpy as np
from carsdata.utils.types import Shape


def _init_level_set(level_set: Union[str, np.ndarray], img_shape: Shape) -> np.ndarray:
    """Initialize the level set used to segment pixels. Only checkerboard and explicit arrays are supported

    Parameters
    ----------
    level_set : Union[str, np.ndarray]
        The level set.
        If level_set is a string equals to 'checkerbard', the level set is made of multiple circles along the image.
        If level_set is an array, then this array will be used as level set.
    img_shape : Shape
        The image spatial dimensions.

    Returns
    -------
    np.ndarray
        The created level set.

    Raises
    ------
    ValueError
        Raised if level_set is an invalid string.
    """    
    if isinstance(level_set, str):
        if level_set == 'checkerboard':
            yv = np.arange(img_shape[0]).reshape(img_shape[0], 1)
            xv = np.arange(img_shape[1])
            phi = (np.sin(np.pi / 5. * yv) * np.sin(np.pi / 5. * xv))
        else:
            raise ValueError(f'{level_set} is not a valid level set name')
    else:
        phi = level_set
    return phi


def _avg(img: np.ndarray, phi: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute average of the two segmentation classes.

    Parameters
    ----------
    img : np.ndarray
        The image.
    phi : np.ndarray
        The level set.
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        The first value is the average inside the level set and the second is the one outside.
    """
    avg_c1 = np.zeros((img.shape[-1]), dtype=img.dtype)
    avg_c2 = np.zeros((img.shape[-1]), dtype=img.dtype)
    idx = phi > 0
    count_c1 = np.count_nonzero(idx)
    count_c2 = idx.size - count_c1

    for dim in range(img.shape[-1]):
        curr = img[:, :, dim]
        avg_c1[dim] = np.sum(curr[idx])
        if count_c1 > 0:
            avg_c1[dim] /= count_c1

        avg_c2[dim] = np.sum(curr[np.logical_not(idx)])
        if count_c2 > 0:
            avg_c2[dim] /= count_c2
    return avg_c1, avg_c2


def _delta(x: np.ndarray, eps: float = 1.) -> np.ndarray:
    """Compute a regularized Dirac function of x.

    Parameters
    ----------
    x : np.ndarray
        Input aray.
    eps : float, optional
        Input aray, by default 1.

    Returns
    -------
    np.ndarray
        The application of a regularized dirac function on x.
    """
    return eps / (eps ** 2 + x ** 2)


def _calculate_variation(
    img: np.ndarray, phi: np.ndarray, mu: float, nu: float, lambda1: float, lambda2: float, dt: float
) -> np.ndarray:
    """Solve the level set values at t+1.

    Parameters
    ----------
    img : np.ndarray
        The image to segment.
    phi : np.ndarray
        The level set.
    mu : float
        Segmentation curve length penalty.
    nu : float
        Segmentation area length penalty.
    lambda1 : float
        Penalty of the inside class intravariance.
    lambda2 : float
        Penalty of the outside class intravariance.
    dt : float
        Time step used for the pde resolution.

    Returns
    -------
    np.ndarray
        The level set values at t+1.
    """
    eta = 1e-16
    padded = np.pad(phi, 1, mode='edge')
    grad_x_p = padded[1:-1, 2:] - padded[1:-1, 1:-1]
    grad_x_n = padded[1:-1, 1:-1] - padded[1:-1, :-2]
    grad_x_0 = (padded[1:-1, 2:] - padded[1:-1, :-2]) / 2.0

    grad_y_p = padded[2:, 1:-1] - padded[1:-1, 1:-1]
    grad_y_n = padded[1:-1, 1:-1] - padded[:-2, 1:-1]
    grad_y_0 = (padded[2:, 1:-1] - padded[:-2, 1:-1]) / 2.0

    div_1 = 1. / np.sqrt(eta + grad_x_p ** 2 + grad_y_0 ** 2)
    div_2 = 1. / np.sqrt(eta + grad_x_n ** 2 + grad_y_0 ** 2)
    div_3 = 1. / np.sqrt(eta + grad_x_0 ** 2 + grad_y_p ** 2)
    div_4 = 1. / np.sqrt(eta + grad_x_0 ** 2 + grad_y_n ** 2)

    mu_term = (padded[1:-1, 2:] * div_1 + padded[1:-1, :-2] * div_2 +
               padded[2:, 1:-1] * div_3 + padded[:-2, 1:-1] * div_4)

    c1, c2 = _avg(img, phi)

    dist_c1 = img - c1
    dist_c1 *= dist_c1
    dist_c1 = lambda1 * np.sum(dist_c1, axis=len(img.shape) - 1)
    dist_c2 = img - c2
    dist_c2 *= dist_c2
    dist_c2 = lambda2 * np.sum(dist_c2, axis=len(img.shape) - 1)

    delta_phi = dt * _delta(phi)
    new_phi = phi + delta_phi * (mu * mu_term - nu - dist_c1 + dist_c2)

    return new_phi / (1 + mu * delta_phi * (div_1 + div_2 + div_3 + div_4))


def chan_sandberg_vese(
    img: np.ndarray, mu: float = 0.25, nu: float = 0, lambda1: float = 1., lambda2: float = 1., tol: float = 1e-3,
    dt: float = 0.5, max_ite: int = 5000, level_set: Union[str, np.ndarray] = 'checkerboard'
) -> np.ndarray:
    """Solve Chan-Sandberg-Vese [1], i.e. Chan-Vese method for vector valued images.

    Parameters
    ----------
    img : np.ndarray
        The image to segment. If len(img) is 2, a new axis is created to have a vector valued image.
    mu : float, optional
        Segmentation curve length penalty, by default 0.25
    nu : float, optional
        Segmentation area length penalty, by default 0
    lambda1 : float, optional
        Penalty of the inside class intravariance, by default 1.
    lambda2 : float, optional
        Penalty of the outside class intravariance, by default 1.
    tol : float, optional
        Convergence threshold, by default 1e-3
    dt : float, optional
        Time step used for the pde resolution, by default 0.5
    max_ite : int, optional
        Maximum number of iterations, by default 5000
    level_set : Union[str, np.ndarray], optional
        The level set.
        If level_set is a string equals to 'checkerbard', the level set is made of multiple circles along the image.
        If level_set is an array, then this array will be used as level set, by default 'checkerboard'.

    Returns
    -------
    np.ndarray
        The segmented input image.
    
    References
    ----------
    [1] Chan, T. F., Sandberg, B. Y., & Vese, L. A. (2000). Active contours without edges for vector-valued images. Journal of Visual Communication and Image Representation, 11(2), 130-141.
    """
    img_shape = img.shape
    if len(img_shape) == 2:
        img = img[..., np.newaxis]

    phi = _init_level_set(level_set, img.shape[0:-1])
    img = img - np.min(img.reshape(img.shape[0] * img.shape[1], img.shape[2]), axis=0)
    max_val = np.max(img.reshape(img.shape[0] * img.shape[1], img.shape[2]), axis=0)
    max_val[max_val == 0] = 1.
    img = img / max_val

    phi_diff = np.inf
    segmentation = phi > 0

    i = 0
    while phi_diff > tol and i < max_ite:
        # Save old level set values
        old_phi = phi

        # Compute new level set
        phi = _calculate_variation(img, phi, mu, nu, lambda1, lambda2, dt)
        phi_diff = np.linalg.norm(phi - old_phi)

        segmentation = phi > 0

        i += 1

    return segmentation
