
from datetime import timedelta
import os


import numpy as np
import pandas
import scipy.ndimage
import skimage.draw
import skimage.morphology
import xarray

import cartopy.crs as ccrs
import numpy as np
import f90nml



def select_source(data, source):
    """
    Select source in data but also compute new fields for other plumes and multiple sources.
    """
    this = data.sel(source=source).copy()
    this['other_sources'] = data['detected_plume'].any('source') & ~this['detected_plume']
    this['multiple_sources'] = data['detected_plume'].sum('source') > 1
    
    return this



class Domain:
    def __init__(self, name, startlon, startlat, stoplon, stoplat,
                 ie=None, je=None, pollon=None, pollat=None):
        """
        to add: dlon, dlat, ie, je
        """
        self.name = name

        self.startlat = startlat
        self.stoplat = stoplat
        self.startlon = startlon
        self.stoplon = stoplon

        self.ie = ie
        self.je = je

        self.rlon = None
        self.rlat = None
        self.lon = None
        self.lat = None

        self.pollon = pollon
        self.pollat = pollat

        self.is_rotpole =  pollon is not None and pollat is not None
        is_grid = self.ie is not None and self.je is not None

        if is_grid:
            self.dlon = (self.stoplon - self.startlon) / (self.ie - 1)
            self.dlat = (self.stoplat - self.startlat) / (self.je - 1)
        else:
            self.dlon, self.dlat = None, None


        if self.is_rotpole:
            self.proj = ccrs.RotatedPole(pole_latitude=pollat,
                                         pole_longitude=pollon)

            if is_grid:
                self.rlon = np.linspace(self.startlon, self.stoplon, self.ie)
                self.rlat = np.linspace(self.startlat, self.stoplat, self.je)

                rlon, rlat = np.meshgrid(self.rlon, self.rlat)
                
                self.lon, self.lat = transform_coords(rlon, rlat, self.proj,
                                                      ccrs.PlateCarree(),
                                                      use_xarray=False)
        else:
            self.proj = ccrs.PlateCarree()

            if is_grid:
                self.lon = np.linspace(self.startlon, self.stoplon, self.ie)
                self.lat = np.linspace(self.startlat, self.stoplat, self.je)


    @property
    def shape(self):
        return self.je, self.ie


    @classmethod
    def from_nml(cls, filename):
        with open(filename) as nml_file:
            nml = f90nml.read(nml_file)

        pollon = nml['lmgrid']['pollon']
        pollat = nml['lmgrid']['pollat']
        startlon = nml['lmgrid']['startlon_tot']
        startlat = nml['lmgrid']['startlat_tot']
        dlon = nml['lmgrid']['dlon']
        dlat = nml['lmgrid']['dlat']
        ie = nml['lmgrid']['ie_tot']
        je = nml['lmgrid']['je_tot']

        stoplat = startlat + (je-1) * dlat
        stoplon = startlon + (ie-1) * dlon

        return cls(filename, startlon, startlat, stoplon, stoplat,
                   ie, je, pollon, pollat)



    
    
def kgs_to_Mtyr(x, inverse=False):
    """ Convert kg/s to Mt/yr. """
    SECONDS_PER_YEAR = 31557600.0 # with 365.25 days
    factor = 1e9 / SECONDS_PER_YEAR
    if inverse:
        return x * factor
    else:
        return x / factor




def read_point_sources():
    """\
    Read list of point sources and converts them to format used by the
    plume detection algorithm.
    """
    filename = os.path.join(os.path.dirname(__file__), 'data', 'sources.csv')
    
    point_sources = pandas.read_csv(filename, index_col=0,
                              names=['UTF-8', 'longitude', 'latitude', 'type'],
                              header=0)
    
    sources = xarray.Dataset(coords={'source': point_sources.index})
    sources['lon_o'] = xarray.DataArray(point_sources['longitude'], dims='source',
                                        attrs={'name': 'longitude of point source'})
    sources['lat_o'] = xarray.DataArray(point_sources['latitude'], dims='source',
                                        attrs={'name': 'latitude of point source'})
    sources['type'] = xarray.DataArray(point_sources['type'], dims='source',
                                       attrs={'name': 'type of point source'})
    
    sources['UTF-8'] = xarray.DataArray(point_sources['UTF-8'], dims='source')

    # size of point sources (used for finding overlap of detected plumes)
    sources['radius'] = xarray.DataArray(
        np.where(point_sources['type'] == 'city', 15.0, 5.0),
        attrs={'name': 'Radius of point source around location', 'units': 'km'},
        dims='source')
    
    return sources


def transform_coords(x, y, input_crs, output_crs, use_xarray=True, names=('x', 'y')):
    """
    Convert easting and northing in EPSG to WGS84.
    """
    if use_xarray:
        dims = x.dims
        
    x = np.asarray(x)
    y = np.asarray(y)
    shape = x.shape
        
    res = output_crs.transform_points(input_crs, x.flatten(), y.flatten())
    xnew, ynew = res[:,0].reshape(shape), res[:,1].reshape(shape)
    
    if use_xarray:
        xnew = xarray.DataArray(xnew, name=names[0], dims=dims)
        ynew = xarray.DataArray(ynew, name=names[1], dims=dims)
        
    return xnew, ynew
    

    if np.ndim(x) == 0:
        res = output_crs.transform_point(lon, lat, input_crs)
        xnew, ynew = res[0], res[1]
        
    elif np.ndim(x) in [1,2]:
        res = out.transform_points(in_, lon, lat)
        xnew, ynew = res[...,0], res[...,1]
        
    else:
        shape = x.shape
        res = output_crs.transform_points(input_crs, x.flatten(), y.flatten())
        x, y = x[:,0].reshape(shape), y[:,1].reshape(shape)
        
        
        


def wgs2epsg(lon, lat, epsg, inverse=False):
    """
    Transforms lon/lat to EPSG.
    """
    if inverse:
        out = ccrs.PlateCarree()
        in_ = ccrs.epsg(epsg)
    else:
        out = ccrs.epsg(epsg)
        in_ = ccrs.PlateCarree()

    if np.ndim(lon) == 0:
        res = out.transform_point(lon, lat, in_)
        return res[0], res[1]
    elif np.ndim(lon) in [1,2]:
        res = out.transform_points(in_, lon, lat)
        return res[...,0], res[...,1]
    else:
        shape = lon.shape
        res = out.transform_points(in_, lon.flatten(), lat.flatten())
        return res[:,0].reshape(shape), res[:,1].reshape(shape)
    
    
def has_multiple_sources(data, source):
    """
    Returns if the plume detected for "source" has also added to other
    sources in the dataset.
    """
    return bool(np.any(data['detected_plume'].sel(source=source) &
                       (data['detected_plume'].sum('source') > 1)))


def compute_plume_area(data, crs, distance=25e3):
    """
    distance in meters, source used to draw circle around
    """
    n = int(distance // 1e3 + 1)
    r = int(distance // 2e3 + 1) 
    
    shape = (n, n)
    kernel = np.zeros(shape, dtype=bool)

    rr,cc = skimage.draw.circle(r-1,r-1,r)
    kernel[rr,cc] = True

    # set pixels within distance from detected pixels to True
    detected_plume = np.array(data['detected_plume'])
    area = skimage.morphology.dilation(detected_plume, kernel)

    # set area 50 km around source to True
    x_o = float(data['x_o'])
    y_o = float(data['y_o'])

    area[ np.sqrt((data.x - x_o)**2 + (data.y - y_o)**2) < distance] = True
    
    return area


def cubic_equation(a,b,c,d):
    """
    Find roots of cubic polynomial:
        a * x**3 + b * x**2 + c * x + d = 0
    """
    dtype = np.complex256
    a = np.asarray(a).astype(dtype)
    b = np.asarray(b).astype(dtype)
    c = np.asarray(c).astype(dtype)
    d = np.asarray(d).astype(dtype)

    d0 = b**2 - 3 * a * c
    d1 = 2 * b**3 - 9 * a * b * c + 27 * a**2 * d

    C = ((d1 + np.sqrt(d1**2 - 4 * d0**3)) / 2.0)**(1/3)

    xi = (-1.0 + np.sqrt(-3.0 + 0j)) / 2.0
    s = lambda k: xi**k * C

    roots = [-1.0/ (3.0 * a) * (b + s(k) + d0 / s(k)) for k in range(3)]

    return np.array(roots)






def get_plume_width(data, dy=5e3, area='detected_plume'):

    # distance from center line
    if isinstance(area, str):
        yp = data['yp'].values[data[area]]
    else:
        yp = data['yp'].values[area]

    ymin = np.floor((yp.min() - 2 * dy) / dy) * dy
    ymax = np.ceil((yp.max() + 2 * dy) / dy) * dy

    return ymin, ymax


def compute_polygons(data, source_type='point'):
    """
    Compute [xa,xb] and [ya,yb] intervals for polygons.
    """
    if source_type in ['point', 'power plant']:
        dmin = 0.0
        delta = 5e3
        add_upstream_box = True
        
    elif source_type == 'city':
        dmin = -25e3
        delta = 10e3
        add_upstream_box = False
    else:
        raise ValueError(f'Source type {source_type} not in [point, city].')
        
    dmax = np.nanmax(data.xp.values[data.detected_plume])
    distances = np.arange(dmin, dmax+delta, delta)
   
    if add_upstream_box:
        xa_values = np.concatenate([[-12e3], distances[:-1]])
        xb_values = np.concatenate([[-2e3], distances[1:]])
    else:
        xa_values = distances[:-1]
        xb_values = distances[1:]
    
    ya, yb = get_plume_width(data, dy=2e3)
    
    return xa_values, xb_values, np.full_like(xa_values, ya), np.full_like(xb_values, yb)



def normalized_convolution(values, kernel, mask=None):

    if mask is None:
        mask = ~np.isfinite(values)

    values = values.copy()
    certainty = 1.0 - mask

    values[certainty == 0.0] = 0.0

    return scipy.ndimage.convolve(values, kernel) / scipy.ndimage.convolve(certainty, kernel)




def read_true_emissions(date, species, source, tmin=10, tmax=11, data_path='.'):
    """
    Read true emissions for `tracer` for given date between [`tmin`,`tmax`].
    Units are Mt/yr for CO2 and kt/yr for NO2.
    """
    em = pandas.read_csv(os.path.join(data_path, f'ts_{species}_emissions.dat'),
                         sep='\t', index_col=0, parse_dates=True)
    
    em = em[f'{source} (Mt/yr)']

    em = em[[pandas.Timestamp(date.strftime('%Y%m%d')) + timedelta(hours=h)
             for h in range(tmin,tmax+1)]]

    # NO2: Mt/yr -> kt/yr
    if species == 'NO2':
        em = 1e3 * em

    return em



def compute_plume_age_and_length(ld):
    """
    Estimate plume age and length based on wind speed and arc length of
    detected pixels.
    """
    values = ld.x.values[ld.is_plume.values]

    if np.size(values) > 0:
        plume_length = ld.x.values[ld.is_plume.values].max() / 1e3
    else:
        plume_length = 0.0
        
    plume_age = plume_length / (ld.CO2_flux_fit.attrs['wind_speed'] * 3600 / 1000)
    
    return plume_age, plume_length




def compute_angle_between_curve_and_wind(curve, wind_direction, crs):
    """
    Compute the angle between wind vector and curve tangent, which can be
    used as a warning flag for large misfits.
    
    Parameter: 
    - source: name of point source
    - curves: dict with curves
    """
    # compute curve angle (lon-lat angle)
    u, v = curve.compute_tangent(curve.t_o)
    
    u, v = transform_coords(
        np.array([curve.x_o, curve.x_o - u]),
        np.array([curve.y_o, curve.y_o - v]),
        crs, ccrs.PlateCarree(), use_xarray=False
    )
    u = np.diff(u)
    v = np.diff(v)

    curve_angle = float( np.rad2deg(np.arctan2(u,v)) )

    return smallest_angle(wind_direction, curve_angle)


def smallest_angle(x,y):
    return min(abs(x - y), 360 - abs(x - y))
    
