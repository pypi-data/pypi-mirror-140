
import warnings

from scipy.constants import N_A

import numpy as np
import pandas
import scipy.ndimage
import scipy.optimize
import xarray

import ddeq


def get_plume_width(data, dy=5e3, area='detected_plume'):

    # distance from center line
    if isinstance(area, str):
        yp = data['yp'].values[data[area]]
    else:
        yp = data['yp'].values[area]

    ymin = np.floor((yp.min() - 2 * dy) / dy) * dy
    ymax = np.ceil((yp.max() + 2 * dy) / dy) * dy

    return ymin, ymax



def expand_dimension(data, dim, size):
        
    coords = {}
    for key in data.dims:
        if key == dim:
            coords[key] = np.arange(size)
        else:
            coords[key] = data[key]
    
    new = xarray.Dataset(coords=coords, attrs=data.attrs)
    
    for key in data:
        var = data[key]
        
        if dim in var.dims:
            fill_value = False if var.dtype == np.bool else np.nan
            values = np.concatenate([var.values, np.full(size-var[dim].size, fill_value, dtype=var.dtype)])     
        else:
            values = data[key].values
            
        new[key] = xarray.DataArray(values, dims=var.dims, attrs=var.attrs) 

    
    return new



def concat_polygons(polygons):
    size = max(p['pixels'].size for p in polygons)
    values = [expand_dimension(p, 'pixels', size) for p in polygons]
    return xarray.concat(values, dim='along')


def sort_and_remove_nans(y, c, c_std):
    """
    Sort for y and remove nans.
    """
    sort = np.argsort(y)
    y = y[sort]
    c = c[sort]
    c_std = c_std[sort]

    valids = np.isfinite(y) & np.isfinite(c)

    return y[valids], c[valids], c_std[valids]


def fit_two_gaussian(polygon, share_mu=False):

    def co2_func(x, *a):
        """
        """
        q = a[0]
        sigma = a[1]
        mu = a[2]
        return ddeq.functions.gauss(x, q, sigma, mu)


    def no2_func(x, *a):
        q = a[3]
        sigma = a[1] # use same sigma as for co2
        if share_mu:
            mu = a[2]
        else:
            mu = a[4]
        return ddeq.functions.gauss(x, q, sigma, mu)


    # sort and remove nans
    y1, c1, c_std1 = sort_and_remove_nans(polygon.y, polygon.CO2, polygon.CO2_std)
    y2, c2, c_std2 = sort_and_remove_nans(polygon.y, polygon.NO2, polygon.NO2_std)

    # concat
    y = np.concatenate([y1, y2])
    c = np.concatenate([c1, c2])
    c_std = np.concatenate([c_std1, c_std2])
    
    
    def cost_function(x, *a):
        return np.concatenate([co2_func(y1, *a), no2_func(y2, *a)])

    if share_mu:
        p0 = np.array([
            100.0,   # CO2 line density (kg m-1)
             10e3,   # sigma of CO2 and NO2 function (m)
              0.0,   # CO2/NO2 center shift
              0.1,   # NO2 line density (kg m-1)
        ])
        # some bounds for parameter
        bounds= [0, 1e3, -20e3, 0], [1000, 100e3, 20e3, 1000]
    else:
        p0 = np.array([
            100.0,   # CO2 line density (kg m-1)
             10e3,   # sigma of CO2 and NO2 function (m)
             0.0,    # CO2 center shift
              0.1,   # NO2 line density (kg m-1)
              0.0    # NO2 center shift
        ])
        # some bounds for parameter
        bounds= [0, 1e3, -20e3, 0, -20e3], [1000, 100e3, 20e3, 1000, 20e3]

    if y.size < p0.size:
        p = np.full_like(p0, np.nan)
        cov_p = np.full((p0.size, p0.size), np.nan)
        sigma = None

    else:
        if np.all(np.isnan(c_std)):
            sigma = None
        elif np.any(np.isnan(c_std)):
            raise ValueError
        else:
            sigma = c_std

        warnings.simplefilter("error", scipy.optimize.OptimizeWarning)
        try:
            p, cov_p = scipy.optimize.curve_fit(cost_function, y, c, p0, sigma=sigma, bounds=bounds,
                                                absolute_sigma=sigma is not None)

        except (scipy.optimize.OptimizeWarning, RuntimeError):
            p = np.full_like(p0, np.nan)
            cov_p = np.full((p0.size, p0.size), np.nan)
            
    # check if any uncertainty is zero
    
    # sometimes curve_fit finds the negative solution (should not happen anymore with bounds)
    if p[0] < 0 and p[1] < 0 and p[3] < 0:
        p[0] *= -1.0
        p[1] *= -1.0
        p[3] *= -1.0
    
    p_std = np.sqrt(cov_p.diagonal())
    
    if y1.size == 0 or np.isclose(p_std[0], 0.0): # no not enough CO2 observations
        p[0] = np.nan
        p_std[0] = np.nan
        
    if y2.size == 0 or np.isclose(p_std[3], 0.0): # no NO2 observations
        p[3] = np.nan
        p_std[3] = np.nan

    
    if np.any(np.isclose(p_std, 0.0)):
        print('Estimated sigma is equal to zero', p_std)
        p[:] = np.nan
        p_std[:] = np.nan

    # fits
    polygon['CO2_fit'] = co2_func(polygon['y_fit'], *p)
    polygon['NO2_fit'] = no2_func(polygon['y_fit'], *p)

    # CO2 line denisty
    polygon['CO2_line_density'] = p[0]
    polygon['CO2_line_density_std'] = np.nan if sigma is None else p_std[0]
    polygon['CO2_line_density'].attrs['units'] = 'Mt yr-1'

    # NO2 line density
    polygon['NO2_line_density'] = p[3]
    polygon['NO2_line_density_std'] = np.nan if sigma is None else p_std[3]
    polygon['NO2_line_density'].attrs['units'] = 'Mt yr-1'
    
    polygon['CO2_line_density_mu'] = p[2]
    polygon['CO2_line_density_mu_std'] = p_std[2]
    
    if share_mu:
        polygon['NO2_line_density_mu'] = p[2]
        polygon['NO2_line_density_mu_std'] = p_std[2]
    else:
        polygon['NO2_line_density_mu'] = p[4]
        polygon['NO2_line_density_mu_std'] = p_std[4]
    
    polygon['CO2_line_density_sigma'] = p[1]
    polygon['CO2_line_density_sigma_std'] = p_std[1]
    polygon['NO2_line_density_sigma'] = p[1]
    polygon['NO2_line_density_sigma_std'] = p_std[1]
    
    return polygon




def get_values_from_areas(values, sub_areas):
    return np.array([values[a.values] if np.any(a) else np.array([]) for a in sub_areas],
                   dtype='object')


def extract_pixels(data, tracer, xa, xb, ya, yb, dy=None, get_wind=False,
                   verbose=False):
    """
    Extract pixels within a polygon given by plume coords for along-plume
    direction [xa,xb] and across-plume direction [ya,yb] (units: meters).
    """
    name = tracer[:3]
    polygon = xarray.Dataset()

    # only use pixels that are valid observations
    xp = data['xp'].values
    yp = data['yp'].values

    area = (xa <= xp) & (xp < xb) & (ya <= yp) & (yp <= yb)
    
    polygon['polygon_mask'] = xarray.DataArray(area, dims=data.xp.dims)
    polygon['xa'] = xa
    polygon['xb'] = xb
    polygon['ya'] = ya
    polygon['yb'] = yb
    
    

    isfinite = data['%s_isfinite' % tracer[:3]].values[area]
    
    if 'other_sources' in data and np.any(data['other_sources'].values[area]):
        if verbose:
            print('Mask other plume pixels in polygon [%f,%f].' % (xa,xb))
        isfinite[data['other_sources'].values[area]] = False
    
    # pixel in area
    polygon['x'] = xarray.DataArray(data.xp.values[area], name='x',
                                    dims='pixels')
    polygon['y'] = xarray.DataArray(data.yp.values[area], name='y',
                                    dims='pixels')

    c = data[tracer].values[area]
    c[~isfinite] = np.nan
    p = data['detected_plume'].values[area]
    
    
    
    polygon[name] = xarray.DataArray(c, name=name, dims='pixels')
    polygon['is_plume'] = xarray.DataArray(p, name='is_plume', dims='pixels')

    if get_wind:
        if 'wind_eff_%s' % tracer[:3] in data:
            wind = data['wind_eff_%s' % tracer[:3]].values[area]
        elif 'u_eff_%s' % tracer[:3] in data:
            ueff = data['u_eff_%s' % tracer[:3]].values[area]
            veff = data['v_eff_%s' % tracer[:3]].values[area]
            wind = np.sqrt(ueff**2 + veff**2)
        else:
            wind = np.full(isfinite.shape, np.nan)

        wind[~isfinite] = np.nan

        polygon['wind'] = xarray.DataArray(wind, name='wind', dims='pixels')



    # estimate noise
    noise_level = data[tracer].attrs.get('noise_level', np.nan)

    c_std = np.full(np.shape(c), noise_level)
    polygon['%s_std' % name] = xarray.DataArray(c_std, name='%s_std' % name, dims='pixels')


    polygon['subpolygons'] = xarray.DataArray(
        np.arange(ya + 0.5 * dy, yb, dy), dims='subpolygons'
    )

    sub_areas = [(y0 - 0.5 * dy <= polygon['y']) &
                 (polygon['y'] < y0 + 0.5 * dy)
                 for y0 in polygon['subpolygons']]

    xx = get_values_from_areas(polygon['x'], sub_areas)
    yy = get_values_from_areas(polygon['y'], sub_areas)
    
    c = get_values_from_areas(polygon[name], sub_areas)
    c_std = get_values_from_areas(polygon['%s_std'%name], sub_areas)

    for name in ['x', 'y', name, '%s_std'%name, 'is_plume']:

        if name == 'is_plume':
            function = np.sum
        elif name == '%s_std' % name:
            function = standard_error_of_the_mean
        else:
            function = np.nanmean

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'Mean of empty slice')
            values = [function(v) for v in get_values_from_areas(polygon[name].values, sub_areas)]

        polygon['%s_sub' % name] = xarray.DataArray(values, dims='subpolygons')

    return polygon




def extract_line_density(data, tracer, xa, xb, ya=None, yb=None, dy=5e3,
                         method='both', show=False, show_true=True,
                         share_mu=False, extra_width=5e3, add_errors=False,
                         ax=None, verbose=False):
    """
    Extract line densitiy of trace gas in data within polygon given by along-plume
    interval [xa, xb] and across-plume interval [ya, yb]. If ya or yb is None
    estimate plume width from detected pixels. The plume center line is
    described by the `curve`.

    The function uses two methods:
        - fitting a Gaussian curve
        - summing mean values in sub-areas in across-plume direction using
          sub-areas with width `dy`
          
    share_mu: fitting two gaussian share mean value
    """
    if ya is None or yb is None:
        ya, yb = get_plume_width(data, dy=extra_width)
    else:
        ya = ya[0]
        yb = yb[0]
        
    if verbose:
        print('Extract for x in [%.1f,%.1f] and y in [%.1f,%1.f]'
              % (xa,xb,ya,yb))
        
        
    # extract pixels in area
    polygon = extract_pixels(data, tracer, xa, xb, ya, yb, dy=dy, get_wind=True,
                             verbose=verbose)
    polygon['y_fit'] = xarray.DataArray(np.linspace(ya, yb, 501), dims='y_fit')
    polygon['CO2_fit'] = xarray.full_like(polygon['y_fit'], np.nan)
    polygon['NO2_fit'] = xarray.full_like(polygon['y_fit'], np.nan)
    polygon['method'] = method
   
    # NO2 values
    if tracer.replace('CO2', 'NO2') in data:
        tracers = ['CO2', 'NO2']
        polygon.update(extract_pixels(data, tracer.replace('CO2', 'NO2'), xa, xb,
                       ya, yb, dy=dy, get_wind=True))
    else:
        tracers = ['CO2']
    

    if method in ['gauss', 'gaussian']:

        for tracer in tracers:

            # fit function (Gaussian or Error function)
            if np.any((polygon['is_plume_sub'] > 0) & np.isnan(polygon['%s_sub' % tracer])):
                polygon['%s_line_density' % tracer] = np.nan
                polygon['%s_line_density' % tracer] = np.nan
            else:
                mass_gauss, mass_gauss_std, fit_gauss = fit_function(polygon['y'],
                                                                     polygon[tracer],
                                                                     polygon['%s_std' % tracer],
                                                                     polygon['y_fit'],
                                                                     function='gauss')

                polygon['%s_line_density' % tracer] = mass_gauss
                polygon['%s_line_density_std' % tracer] = mass_gauss_std
                polygon['%s_fit' % tracer][:] = fit_gauss

            # set not used parameters to nan
            polygon['%s_line_density_mu' % tracer] = np.nan
            polygon['%s_line_density_sigma' % tracer] = np.nan
            polygon['%s_line_density_mu_std' % tracer] = np.nan
            polygon['%s_line_density_sigma_std' % tracer] = np.nan
                

    elif method in ['sub-areas']:

        for tracer in tracers:

            if np.any((polygon['is_plume_sub'] > 0) & np.isnan(polygon['%s_sub' % tracer])):
                polygon['%s_line_density' % tracer] = np.nan
                polygon['%s_line_density' % tracer] = np.nan
            else:

                valids = np.isfinite(polygon['CO2_sub'].values)

                ss = polygon['subpolygons'].values
                area_means = polygon['%s_sub' % tracer].values
                area_means_std = polygon['%s_std_sub' % tracer].values

                if np.all(~valids):
                    area_means[:] = np.nan
                else:
                    area_means = np.interp(ss, ss[valids], area_means[valids],
                                           left=0.0, right=0.0)

                polygon['%s_line_density' % tracer] = np.sum(area_means * dy)
                
                # FIXME
                n = np.sum(valids)
                polygon['%s_line_density_std' % tracer] = np.sqrt( np.nansum(area_means_std**2 * dy**2) ) / np.sqrt(n)

            # set not used parameters to nan
            polygon['%s_line_density_mu' % tracer] = np.nan
            polygon['%s_line_density_sigma' % tracer] = np.nan
            polygon['%s_line_density_mu_std' % tracer] = np.nan
            polygon['%s_line_density_sigma_std' % tracer] = np.nan

    elif method in ['two-gauss']:
        polygon = fit_two_gaussian(polygon, share_mu=share_mu)
        
    elif method == 'none':
        pass
        
    else:
        raise ValueError

    # x_sub and y_sub have only nans if no pixels are inside subpolygon, 
    # i.e. sub-polygon is not in swath
    # FIXME: does not work when plume is wider than plume area (~10 km)
    #not_fully_in_swath = np.any(np.isnan(polygon['x_sub']) & (np.abs(polygon['subpolygons']) <= 10.0))
    not_fully_in_swath = np.any(np.isnan(polygon['x_sub']))
    
    #if verbose and not_fully_in_swath:
    if not_fully_in_swath:
        print('Polygon not fully in swath')
        
    # only use fits with at least one observation per sub-polygon, 
    # if pixels have been detected
    for tracer in tracers:
        if not_fully_in_swath or (np.any((polygon['is_plume_sub'] > 0)
                                         & np.isnan(polygon['%s_sub' % tracer]))):
            
            if verbose:
                print('Set %s LD to nan: not in swath or no pixels in sub-polygon with plume detection' % tracer)
            
            polygon['%s_line_density' % tracer] = np.nan
            polygon['%s_line_density_std' % tracer] = np.nan
            
            if method == 'two-gauss':
                polygon['%s_fit' % tracer][:] = np.nan


    # set unrealistic low/high values to nan
    if method != 'none':
        if (
            polygon[f'{tracer}_line_density'] < -1000.0 or polygon[f'{tracer}_line_density'] > 1000.0 or
            polygon[f'{tracer}_line_density_std'] > 1000.0
        ):
            if verbose:
                print('Fit failed:', polygon[f'{tracer}_line_density'], polygon[f'{tracer}_line_density_std'])
            polygon[f'{tracer}_line_density'] = np.nan
            polygon[f'{tracer}_line_density_std'] = np.nan
            if method == 'two-gauss':
                polygon[f'{tracer}_fit'][:] = np.nan

                
    return polygon



def gaussian(x, sigma):
    g = 1 / (np.sqrt(2.0 * np.pi) * sigma) * np.exp(-x**2 / (2.0 * sigma**2))

    return g



def city_plume_model(x, Q, sigma, x0=None, x_source=0.0, B=0.0, dx=1e3):
    """
    x : along-plume distance (in meters)
    sigma: width of gaussian
    x_source : plume source
    x0: decay distance

    B: background
    """
    # high-resolution x-distance
    xhigh = np.arange(x[0]-50e3, x[-1]+200e3, dx)

    # decay function
    e = ddeq.functions.decay_function(xhigh, x_source, x0)

    # gaussian
    xgauss = np.arange(-50e3, +50e3+dx/2, dx)
    g = gaussian(xgauss, sigma)

    # convolution
    f = scipy.ndimage.convolve(e, g, mode='nearest')

    # scaling with source strength assumed
    M = Q * f / f.max() + B

    # interpolate
    M = np.interp(x, xhigh, M)

    return M


def point_plume_model(x, Q, x0):
    e = Q * ddeq.functions.decay_function(x, 0.0, x0)
    return e




def fit_emissions(tracer, xvalues, flux, flux_std=None,
                  dmin_fit=10e3, dmax_fit=np.inf, is_point_source=True,
                  absolute_sigma=True):
    """
    Estimate NO2 emissions from fluxes by fitting an exponential decay
    function.
    """
    # check valid values
    valids = np.isfinite(flux) & (xvalues < dmax_fit) & (xvalues > dmin_fit)

    if flux_std is None or np.all(np.isnan(flux_std)) or np.all(flux_std == 0.0):
        sigma = None
    else:
        sigma = flux_std[valids]

    # starting vector
    if tracer == 'NO2':
        
        if is_point_source:
            p0 = np.array([
                10.0,    # source strength in kg/s (~10 for NOx and 1000 for CO2)
                100e3,   # decay distance: x0 = wind_speed * decay_time
            ])
            model = point_plume_model
            bounds= [0.0, 0.0], [np.inf, 432000.0] #24 hours
            
            
            
        else:
            p0 = np.array([
                10.0,    # source strength in kg/s (~10 for NOx and 1000 for CO2)
                10e3,    # width of city gaussian
                100e3,   # decay distance: x0 = win_speed * decay_time
            ])
            model = city_plume_model
            bounds= [0.0, 0.0, 0.0], [np.inf, np.inf, np.inf]

    else:
        p0 = np.array([
            1000.0, # source strength in kg/s (~10 for NOx and 1000 for CO2)
        ])
        model = lambda x, q: np.full(x.shape, q)
        bounds= [0.0], [np.inf]


    if np.sum(valids) < {'NO2': 1, 'CO2': 1}[tracer]:
        print('Too few valid line densities (%d) for fitting curve.' %
              sum(valids))

        return np.nan, np.nan, np.full(xvalues.shape, np.nan), np.full_like(p0, np.nan), np.full_like(p0, np.nan)
        
    
    if tracer == 'CO2' and np.sum(valids) == 1:
        x = np.array([flux[valids][0]])
        x_std = np.array([flux_std[valids][0]])
        
    elif tracer == 'NO2' and np.sum(valids) < 3 and np.any(xvalues[valids] < 10e3):
        x = np.array([np.mean(flux[valids]), np.nan])
        x_std = np.array([np.mean(flux_std[valids]), np.nan])
        
    else:
        try:
            x, cov_x = scipy.optimize.curve_fit(model, xvalues[valids],
                                                flux[valids], p0=p0,
                                                bounds=bounds, 
                                                sigma=sigma, absolute_sigma=absolute_sigma)

        except RuntimeError as e:
            print('Fit fluxes:', e)
            return np.nan, np.nan, np.full(xvalues.shape, np.nan), np.full_like(p0, np.nan), np.full_like(p0, np.nan)
    
        except scipy.optimize.OptimizeWarning as e:
            print('Fit fluxes:', e)
            return np.nan, np.nan, np.full(xvalues.shape, np.nan), np.full_like(p0, np.nan), np.full_like(p0, np.nan)

            


        # estimate uncertainty assuming a good fit
        x_std = np.sqrt(np.diag(cov_x))

    if tracer == 'NO2':
        if is_point_source:
            if np.isnan(x[1]): # no decay time
                fit = np.full(xvalues.shape, x[0])
            else:
                fit = point_plume_model(xvalues, *x)
                
            fit[xvalues < 0.0] = np.nan
        else:
            fit = city_plume_model(xvalues, *x)
    else:
        fit = np.full(xvalues.shape, np.nan)
        fit[xvalues >= dmin_fit] = x[0]

    fit = ddeq.misc.kgs_to_Mtyr(fit)

    # in kt yr-1 or Mt yr-1
    if tracer == 'NO2':
        q = 1e3 * ddeq.misc.kgs_to_Mtyr(x[0])
        q_std = 1e3 * ddeq.misc.kgs_to_Mtyr(x_std[0])
        fit = 1e3 * fit
        
    else:
        q = ddeq.misc.kgs_to_Mtyr(x[0])
        q_std = ddeq.misc.kgs_to_Mtyr(x_std[0])
        

    return q, q_std, fit, x, x_std




def compute_emissions_and_uncertainties(tracer, along, line_density, line_density_std, wind, wind_std,
                                       is_point_source=True):
    """\
    Compute emissions (q in kg/s) and for NO2 decay times (tau in hours) as well as their uncertainties.
    
    tracer             CO2 or NO2
    along              along-plume coords in meters
    line_density       CO2 or NO2 line densities
    line_density_std   uncertainty of line densities
    wind               estimate of wind speed in plume
    wind_std           uncertainty of wind speed
    
    """
    # compute flux and uncertainty (not including wind_std yet)
    flux = wind * line_density
    flux_std = wind * line_density_std
    
    if is_point_source:
        _, _, fit, p, p_std = fit_emissions(tracer, along, flux, flux_std, dmin_fit=0.0, dmax_fit=np.inf,
                                            is_point_source=True)
    else:
        if tracer == 'CO2':
            _, _, fit, p, p_std = fit_emissions(tracer, along, flux, flux_std, dmin_fit=15e3, dmax_fit=np.inf,
                                                is_point_source=False)
        else:
            _, _, fit, p, p_std = fit_emissions(tracer, along, flux, flux_std, dmin_fit=-25e3, dmax_fit=np.inf,
                                                is_point_source=False)
            
        
    
    # only LD uncertainty
    q = p[0]
    q_std = np.sqrt(p_std[0]**2 + (p[0] / wind)**2 * wind_std**2 )
       
    # decay time
    if tracer == 'NO2':
        tau = p[1] / wind / 3600
        tau_std = np.sqrt(p_std[1]**2 / wind**2 + p[1]**2 / wind**4 * wind_std**2) / 3600
    else:
        tau = np.nan
        tau_std = np.nan
        
    return q, q_std, tau, tau_std, fit




def do_mass_balance(data, curve, trace_gases, wind_speed, wind_direction=None,
                    method='two-gauss', crs=None):
    """
    Estimate emissions by applying a mass-balance approach.
    """
    # add one polygon [-10 km - -2 km] upstream for checking for upstream sources
    source_type = str(data['type'].values)
    xa_values, xb_values, ya, yb = ddeq.misc.compute_polygons(data, source_type=source_type)
    

    
    results = []
    
    for xa, xb in zip(xa_values, xb_values):
            
        if method == 'two-gauss':
            
            # use "sub-areas" upstream where no plume should exists 
            this_method = 'two-gauss' if xa >= 0.0 else 'sub-areas'
                
            ld = extract_line_density(data, 'CO2_minus_estimated_background_mass', 
                                      xa=xa, xb=xb, ya=ya, yb=yb, 
                                      method=this_method, share_mu=True)
            results.append(ld)
            
            
        else:
            ld = extract_line_density(data, 'CO2_minus_estimated_background_mass', 
                                      xa=xa, xb=xb, method=method)
            results.append(ld)
            
    if len(results) == 0:
        return None
   

    results = concat_polygons(results)
    results['along'] = xarray.DataArray(0.5 * (results.xa + results.xb), dims='along')
    
    for tracer in ['CO2', 'NO2']: # TODO
        
        if '%s_line_density' % tracer not in results:
            continue
       
        wind_speed_std = 0.5
        
        is_point_source = False if source_type == 'city' else True 
        q, q_std, tau, tau_std, fit = compute_emissions_and_uncertainties(tracer, 
                                                                          results['along'].values,
                                                                          results[f'{tracer}_line_density'].values,
                                                                          results[f'{tracer}_line_density_std'].values,
                                                                          wind_speed,
                                                                          wind_speed_std,
                                                                          is_point_source=is_point_source
                                                                         )
        
        # compute flux and its stds adding wind speed std
        results[f'{tracer}_flux'] = wind_speed * results[f'{tracer}_line_density']
        results[f'{tracer}_flux_std'] = np.sqrt(
            wind_speed**2 * results[f'{tracer}_line_density_std']**2 + 
            wind_speed_std**2 * results[f'{tracer}_line_density']**2
        )
        
        # compute uncertainty of emissions including wind speed
        scaling = 1.0 if tracer == 'CO2' else 1e3
        q = scaling * ddeq.misc.kgs_to_Mtyr(q)
        q_std = scaling * ddeq.misc.kgs_to_Mtyr(q_std)
        
    
        angle = ddeq.misc.compute_angle_between_curve_and_wind(curve, wind_direction, crs)
        results.attrs['angle_between_curve_and_wind'] = angle
        
        results['%s_flux_fit' % tracer] = xarray.DataArray(fit, dims='along')
        results['%s_flux_fit' % tracer].attrs['emissions'] = q
        results['%s_flux_fit' % tracer].attrs['emissions_std'] = q_std
        results['%s_flux_fit' % tracer].attrs['wind_speed'] = wind_speed
        results['%s_flux_fit' % tracer].attrs['wind_direction'] = wind_direction
        
        if tracer == 'NO2':
            results['%s_flux_fit' % tracer].attrs['decay_time'] = tau
            results['%s_flux_fit' % tracer].attrs['decay_time_std'] = tau_std
            
            
    return results
    

