

from scipy.special import erf
import scipy.integrate

import numpy as np



def gauss(x, E0, sigma, shift, slope=0.0, offset=0.0):
    """
    """
    e = E0 / (sigma * np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * ((x - shift) / sigma)**2)
    e += slope * x + offset

    return e


def decay_function(x, x_source, x0=None):
    """
    Exp. decay in x direction downstream of x_source with decay distance x0.
    """
    e = np.zeros_like(x)
    downstream = x > x_source

    if x0 is None:
        e[downstream] = 1.0
    else:
        e[downstream] = np.exp(-(x[downstream] - x_source) / x0)

    return e




def error_function(x, E0, sigma, box_width=20e3, shift=0.0, slope=0.0,
                   offset=0.0):
    """\
    An error function plus a linear function.

    The error function is the convolution of Gaussian and box function. The
    integral of the error function is E0.

    sigma - standard deivation of the Gaussian
    box_width - widht of the box function
    slope - slope of the linear function
    offset - offset of the linear function
    """
    delta = 0.5 * box_width
    a = sigma * np.sqrt(2.0)

    x1 = (x - shift + delta) / a
    x2 = (x - shift - delta) / a

    g = E0 * ( erf(x1) - erf(x2) ) / (4.0 * delta)
    g += x * slope + offset

    return g
