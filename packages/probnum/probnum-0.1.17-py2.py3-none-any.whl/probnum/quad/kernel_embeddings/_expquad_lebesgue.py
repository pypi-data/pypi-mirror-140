"""Kernel embedding of exponentiated quadratic kernel with Lebesgue integration
measure."""

# pylint: disable=no-name-in-module

import numpy as np
from scipy.special import erf

from probnum.quad._integration_measures import LebesgueMeasure
from probnum.randprocs.kernels import ExpQuad


def _kernel_mean_expquad_lebesgue(
    x: np.ndarray, kernel: ExpQuad, measure: LebesgueMeasure
) -> np.ndarray:
    """Kernel mean of the ExpQuad kernel w.r.t. its first argument against a Gaussian
    measure.

    Parameters
    ----------
    x :
        *shape (n_eval, input_dim)* -- n_eval locations where to evaluate the kernel
        mean.
    kernel :
        Instance of an ExpQuad kernel.
    measure :
        Instance of a LebesgueMeasure.

    Returns
    -------
    kernel_mean :
        *shape=(n_eval,)* -- The kernel integrated w.r.t. its first argument,
        evaluated at locations ``x``.
    """
    (input_dim,) = kernel.input_shape

    ell = kernel.lengthscale
    return (
        measure.normalization_constant
        * (np.pi * ell**2 / 2) ** (input_dim / 2)
        * (
            erf((measure.domain[1] - x) / (ell * np.sqrt(2)))
            - erf((measure.domain[0] - x) / (ell * np.sqrt(2)))
        ).prod(axis=1)
    )


def _kernel_variance_expquad_lebesgue(
    kernel: ExpQuad, measure: LebesgueMeasure
) -> float:
    """Kernel variance of the ExpQuad kernel w.r.t. both arguments against a Gaussian
    measure.

    Parameters
    ----------
    kernel :
        Instance of an ExpQuad kernel.
    measure :
        Instance of a LebesgueMeasure.

    Returns
    -------
    kernel_variance :
        The kernel integrated w.r.t. both arguments.
    """

    (input_dim,) = kernel.input_shape

    r = measure.domain[1] - measure.domain[0]
    ell = kernel.lengthscale
    return (
        measure.normalization_constant**2
        * (2 * np.pi * ell**2) ** (input_dim / 2)
        * (
            ell * np.sqrt(2 / np.pi) * (np.exp(-(r**2) / (2 * ell**2)) - 1)
            + r * erf(r / (ell * np.sqrt(2)))
        ).prod()
    )
