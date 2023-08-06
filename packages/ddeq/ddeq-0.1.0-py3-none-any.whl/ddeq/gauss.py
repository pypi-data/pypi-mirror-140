

import numpy as np
import scipy.optimize
import xarray

import ddeq


def fit_plume_model(data, source, wind_speed, trace_gas='CO2'):
    """
    Estimate emissions by fitting a 2D Gauss plume to the observations.
    """
    this = ddeq.misc.select_source(data, source)
    
    mask = np.isfinite(this['xp']) & np.isfinite(this['yp']) \
           & np.isfinite(this[f'{trace_gas}_minus_estimated_background_mass'])

    x = this['x'].values[mask]
    y = this['y'].values[mask]
    
    xp = this['xp'].values[mask]
    yp = this['yp'].values[mask]

    obs_field = this[f'{trace_gas}_minus_estimated_background_mass'].values[mask]

    
    model = ddeq.gauss.PlumeModel(x=xp, y=yp, u=float(wind_speed))

    if trace_gas == 'CO2':
        p0 = np.array([100.0, 100.0, 0.0])
        p, cov = scipy.optimize.curve_fit(model, None, obs_field, p0=p0)

        Q, K, BG = p
        Q_std, K_std, BG_std = np.sqrt(np.diag(cov))
        
        tau = np.nan
        tau_std = np.nan
    
    elif trace_gas == 'NO2':
        p0 = np.array([100.0, 100.0, 0.0, 20000.0])
        p, cov = scipy.optimize.curve_fit(model, None, obs_field, p0=p0)

        Q, K, BG, tau = p
        Q_std, K_std, BG_std, tau_std = np.sqrt(np.diag(cov))
        
    else:
        raise ValueError('trace_gas needs to be CO2 or NO2')
        

    model_field = model(None, *p)
    
    Q = ddeq.misc.kgs_to_Mtyr(Q)
    Q_std = ddeq.misc.kgs_to_Mtyr(Q_std)
    
    # TODO: incl. wind error
    # TODO: return xarray 
    this[f'{trace_gas}_plume_model_mass'] = xarray.full_like(this[f'{trace_gas}_minus_estimated_background_mass'], np.nan)
    this[f'{trace_gas}_plume_model_mass'].values[mask] = model_field
    this[f'{trace_gas}_plume_model_mass'].attrs.update(
        {
            'source strength [Mt/yr]': Q,
            'source strength uncertainty [Mt/yr]': Q_std,
            'wind speed [m/s]': wind_speed,
            'background [kg/m2]': BG,
            'background uncertainty [kg/m2]': BG_std,
            'eddy diffusion coefficient [m2/s]': K,
            'eddy diffusion coefficient uncertainty [m2/s]': K_std,
            'decay time []': tau,
            'decay time uncertainty []': tau_std,
        }
    )
        
    return this
    
    


class PlumeModel:
    def __init__(self, x, y, u, x0=0.0, y0=0.0):
        """\
        Computes Gaussian plume (units: kg/m2).

        x: distance from origin in m
        y: distance from center line in m
        u: wind speed in m/s

        x0: x-coordinate of origin
        y0: y-coordinate of origin

        TODO:
        - decay time

        """
        self.x = x
        self.y = y
        self.u = u
        
        # location of origin
        self.x0 = x0
        self.y0 = y0
    
    
    def __call__(self, foo, Q, K, BG=0.0, tau=None):
        """
        Q: emission strength in kg/s
        K: eddy diffusion coefficient in m²/s
        BG: background in kg/m²
        """
        # dispersion along the plume
        down = self.x > self.x0
        sigma = np.sqrt(2.0 * K * (self.x[down] - self.x0) / self.u)

        # compute Gaussian plume
        c = Q / (np.sqrt(2.0 * np.pi) * sigma * self.u) * np.exp(-0.5 * (self.y[down] - self.y0)**2 / sigma**2)
        
        if tau is not None:
            c = c * ddeq.functions.decay_function(self.x, self.x0, tau)[down]

        plume = np.full(self.x.shape, BG)
        plume[down] += c

        return plume