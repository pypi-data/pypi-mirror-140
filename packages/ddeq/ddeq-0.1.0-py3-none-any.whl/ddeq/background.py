

import numpy as np
import scipy.ndimage
import xarray

import ddeq


def create_gaussian_kernel(sigma):
    """
    Creat a Gaussian kernel with standard deviation `sigma`. The size of the
    kernel is at least 11x11 but at least 5*sigma.
    """

    # size should be odd and at least 11 pixels
    size = max(11, int(5 * sigma))
    if size%2 == 0:
        size += 1

    kernel = np.zeros((size,size))
    kernel[size//2,size//2] = 1.0
    kernel = scipy.ndimage.gaussian_filter(kernel, sigma=sigma)

    return kernel




def estimate(data, variable, sigma=10.0):
    """\
    Estimate (smooth) CO2 background using normalized convolution.
    """
    c = np.array(data[variable])

    # only use pixels that are in plume area around plume without enhanced values
    valids = np.array(~data.is_hit)
    valids[~np.isfinite(c)] = False

    kernel = create_gaussian_kernel(sigma)

    c[~valids] = np.nan
    bg_est = ddeq.misc.normalized_convolution(c, kernel, mask=~valids)
    
    if np.ndim(data.detected_plume) != 3:
        bg_est[~area] = np.nan

    bg_est = xarray.DataArray(bg_est, name=f'{variable}_estimated_background',
                              dims=data[variable].dims)
    bg_est.attrs['long name'] = f'estimated {variable} background'
    bg_est.attrs['method'] = 'normalized convolution (sigma = %.1f px)' % sigma

    data[f'{variable}_estimated_background'] = bg_est
    
    
    return data
    
