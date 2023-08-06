
# FIXME
#import emiss
#from emiss.gauss import (
#    compute_xy_coords, compute_plume_area, plume_signal_and_gaps,
#    convert_ppm_to_mass, convert_molec_to_mass,
#    create_center_line, compute_plume_coords
#)


import cartopy.crs as ccrs
import numpy as np
import scipy.optimize
import skimage
import xarray

import ddeq.misc



def compute_xy_coords(data, crs):
    """
    Compute xy coordinates (in meters) for pixel centers and corners using
    provided coordinate reference system (cartopy.crs). 
    """
    wgs84 = ccrs.PlateCarree()
    
    data['x'], data['y'] = ddeq.misc.transform_coords(data.lon, data.lat,
                                                      input_crs=wgs84,
                                                      output_crs=crs,
                                                      use_xarray=True)
    
    data['x_o'], data['y_o'] = ddeq.misc.transform_coords(data.lon_o, data.lat_o,
                                                      input_crs=wgs84,
                                                      output_crs=crs,
                                                      use_xarray=True)
    if 'lonc' in data and 'latc' in data:
        data['xc'], data['yc'] = ddeq.misc.transform_coords(data.lonc, data.latc,
                                                            input_crs=wgs84,
                                                            output_crs=crs,
                                                            use_xarray=True)
    return data



def compute_plume_coords(data, curve, source, do_corners=False):
    """
    Compute plume coordinates for center and corner pixels within plume area.
    """
    index = int(np.argmax(data.source.values == source))
    source_data = data.sel(source=source)

    # center pixels in plume coords
    if 'xp' not in data or 'yp' not in data:
        shape = data.nobs.size, data.nrows.size, data.source.size
        
        data['xp'] = xarray.DataArray(np.full(shape, np.nan), dims=('nobs', 'nrows', 'source'))
        data['yp'] = xarray.DataArray(np.full(shape, np.nan), dims=('nobs', 'nrows', 'source'))
        
        data.xp.attrs['long name'] = 'along plume coordiate'
        data.yp.attrs['long name'] = 'across plume coordinate'

    data['xp'][:,:,index], data['yp'][:,:,index] = compute_plume_coordinates(source_data,
                                                                                        curve,
                                                                                        which='centers')

    # compute for all ground pixels distance to center line
    # pixel corners
    if do_corners:
        if 'xcp' not in data or 'ycp' not in data:
            shape = data.nobs.size, data.nrows.size, data.ncorners.size, data.source.size
            data['xcp'] = xarray.DataArray(np.full(shape, np.nan), dims=('nobs', 'nrows', 'ncorners', 'source'))
            data['ycp'] = xarray.DataArray(np.full(shape, np.nan), dims=('nobs', 'nrows', 'ncorners', 'source'))
            data.xcp.attrs['long name'] = 'along plume corner coordinates'
            data.ycp.attrs['long name'] = 'across plume corner coordinates'

        data['xcp'][:,:,:,index], data['ycp'][:,:,:,index] = compute_plume_coordinates(
            source_data, curve, which='corners')

        # check if pixels still valid polygons (can happen if curve is
        # over- or undershooting
        for i,j in np.ndindex(source_data.plume_area.shape):

            if not source_data.plume_area[i,j]:
                continue

            coords = np.transpose([data['xcp'][i,j,:,index],data['ycp'][i,j,:,index]])
            px = shapely.geometry.Polygon(coords)

            if np.any(np.isnan(coords)) or not px.is_valid \
               or np.abs(px.area - px.convex_hull.area) > 1.0:
                print('Error: Mask invalid pixel corners (%d,%d).' % (i,j))
                data['xcp'][i,j,:,index] = np.nan
                data['ycp'][i,j,:,index] = np.nan


    # update plume area by masking nans
    invalids = np.isnan(data.xp[:,:,index]) | np.isnan(data.yp[:,:,index])
    
    if do_corners:
        invalids |= np.any(np.isnan(data.xcp[:,:,index]), axis=2)
        invalids |= np.any(np.isnan(data.ycp[:,:,index]), axis=2)

    area = np.array(data.plume_area.sel(source=source))
    area[invalids] = False
    data['plume_area'][:,:,index] = area

    return data


class Poly2D:
    def __init__(self, x, y, w, degree=2, x_o=0.0, y_o=0.0,
                 x0=0.0, y0=0.0, force_source=True):
        """\
        A 2D curve fitted on the point cloud given by x and y.

        Parameters
        ----------
        x,y,w: x,y coords and weights used for fitting the data

        degree: degrees if the two polynomials x(t) and y(t)

        x_o, y_o: location of source (will be added to x,y and given
                  high weight such that curves goes through source if
                  force_origin is True)

        x0, y0: origin of coordinate system
        """
        self.x = x
        self.y = y
        self.w = w
        self.degree = degree
        self.force_source = force_source

        self.x_o = x_o
        self.y_o = y_o
        self.t_o = np.nan

        self.x0 = x0
        self.y0 = y0

        self.c = np.zeros(2 * (degree + 1))

        self._fit()

        # arc length to origin
        self.t_o = self.get_parameter(self.x_o, self.y_o)

        # 
        self.tmin = 0.0
        self.tmax = np.max(self.get_parameter(self.x, self.y))
        self.interpolator = None


    def to_file(self, filename, group=None, mode='a'):
        """
        Convert Poly2D to netCDF file.
        """
        data = xarray.Dataset()

        for name in ['x', 'y', 'w', 'degree', 'x_o', 'y_o', 'x0', 'y0']:

            value = getattr(self, name)

            if np.ndim(value) == 0:
                data.attrs[name] = value

            else:
                data[name] = xarray.DataArray(value, dims='pixels')

        try:
            data.to_netcdf(filename, mode=mode, group=group)
        except FileNotFoundError:
            data.to_netcdf(filename, mode='w', group=group)
            
        return data


    @classmethod
    def from_file(cls, filename, group=None):
        """
        Read curve from netCDF file.
        """
        with xarray.open_dataset(filename, group=group) as data:
            args = dict((key, np.array(data[key])) for key in data)
            args.update(data.attrs)

        return cls(**args)


    def _fit(self):

        def objective(c, w, x, y):
            xt,yt = self._compute_curve(c,x,y)
            return np.concatenate([
                w * (xt - x), w * (yt - y)
            ])

        # add origin
        if self.force_source:
            x = np.append(self.x, self.x_o)
            y = np.append(self.y, self.y_o)
            w = np.append(self.w, 1000.)
        else:
            x = np.append(self.x, self.x0) # force origin of coords
            y = np.append(self.y, self.y0)
            w = np.append(self.w, 1000.)

        # angle around origin (not used)
        #phi = np.arctan2(y - y0, x - x0)

        # curve fit
        res = scipy.optimize.leastsq(objective, x0=self.c, args=(w,x,y), full_output=True)
        self.c = res[0]
        self.cov_x = res[1] # TODO
        ierr = res[4]

        if ierr not in [1,2,3,4]:
            print('least square failed with error code: ', res)


    def arc2parameter(self, arc):

        if self.interpolator is None:
            ta = np.arange(self.tmin - 50e3, 2 * self.tmax, 500.0)
            la = [arc_length_of_2d_curve(self, self.t_o, v) for v in ta]
            self.interpolator = scipy.interpolate.interp1d(la, ta)

        return self.interpolator(arc)


    def get_parameter(self, x, y):
        return np.sqrt((x - self.x0)**2 + (y - self.y0)**2)


    def compute_tangent(self, t0, norm=False):
        v = np.array(self(t=t0, m=1))
        if norm:
            v /= np.linalg.norm(v, axis=0)
        return v
    
    
    def compute_angle(self, t=None):
        """
        Compute tangent angle for curve.
        """
        if t is None:
            t = self.t_o
            
        u, v = self.compute_tangent(t)
        return np.rad2deg(np.arctan2(u,v))


    def get_coefficients(self, c=None, m=0):

        if c is None:
            c = self.c

        k = c.size // 2
        cx = c[:k]
        cy = c[k:]

        if m != 0:
            cx = np.polyder(cx, m)
            cy = np.polyder(cy, m)

        return cx, cy


    def compute_normal(self, t0, x=None, y=None, t=None):

        x0, y0 = self(t=t0)

        # tangent vector
        v = self.compute_tangent(t0, norm=True)

        # rotate 90 degree
        n = np.dot([[0,-1],[1,0]], v)

        cx = np.array([-n[0], x0])
        cy = np.array([-n[1], y0])

        if t is None:
            s = np.sign(v[0] * (y - y0) - v[1] * (x - x0))
            t = s * np.sqrt((x-x0)**2 + (y-y0)**2)

        return compute_poly_curve(cx, cy, t)
    

    def _compute_curve(self, c, x=None, y=None, t=None, m=0):

        if t is None:
            t = self.get_parameter(x,y)
        else:
            if x is not None or y is not None:
                print('Warning: `x` and `y` will be ignored as `t` was given.')

        cx, cy = self.get_coefficients(c=c, m=m)

        return compute_poly_curve(cx, cy, t)


    def __call__(self, x=None, y=None, t=None, m=0):
        return self._compute_curve(self.c, x, y, t, m)


def compute_poly_curve(cx,cy,t):
    """
    Compute poly curve.
    """
    return np.polyval(cx,t), np.polyval(cy,t)



def create_line(data, source, degree=2, force_source=False,
                tracer=None, source_distance=50e3, crs=None):
    """
    source_distance: distance of the origin from the source in reverse
                     direction of the detected plume (default: 50e3 meters)
    """
    data = data.sel(source=source)
    
    plume = data['detected_plume'].values

    # Compute weights
    if data.attrs['trace_gas'] == 'NO2':
        weights = data['local_NO2_mean'] - data['NO2_local_median']
        weights = weights.values / 1e15

        weights[data.plume_area & ~plume] = 0.2
        weights[weights < 0.2] = 0.2
    else:
        weights = data['local_CO2_mean'] - data['CO2_local_median']
        weights = weights.values

        weights[data.plume_area & ~plume] = 0.05
        weights[weights < 0.05] = 0.05


    # get location of plume and XCO2 values (plus wind etc.)
    is_plume = ddeq.misc.compute_plume_area(data, distance=5e3, crs=crs)

    x = np.asarray(data.x)[is_plume]
    y = np.asarray(data.y)[is_plume]
    w = np.asarray(weights)[is_plume]
    
    # location of the source
    x_o, y_o = float(data.x_o), float(data.y_o)

    # origin of center line (50 km upstream of source)
    x0 = np.mean( data.x.values[plume] )
    y0 = np.mean( data.y.values[plume] )
    delta = np.sqrt((x0 - x_o)**2 + (y0 - y_o)**2)
    
    x1 = x_o - (x0 - x_o) / delta * source_distance
    y1 = y_o - (y0 - y_o) / delta * source_distance
    
    # fit 2d curve
    curve = Poly2D(x, y, w, degree, x_o=x_o, y_o=y_o, x0=x1, y0=y1,
                   force_source=force_source)

    return curve


#
# Across- and along-plume coords
#


def integral_sqrt_poly(x, a, b, c):
    """
    Integral over sqrt(a*x**2 + b*x + c)
    """
    s = np.sqrt( a * x**2 + b * x + c)

    A = (b + 2 * a * x) / (4 * a) * s
    B = (4 * a * c - b**2) / (8 * a**(3/2))
    C = np.abs(2 * a * x + b + 2 * np.sqrt(a) * s)

    return A + B * np.log(C)


def compute_arc_length(curve, smin, smax):
    a, b = curve.get_coefficients()

    c0 = 4 * a[0]**2 + 4 * b[0]**2
    c1 = 4 * a[0] *a[1] + 4 * b[0] * b[1]
    c2 = a[1]**2 + b[1]**2

    smin = integral_sqrt_poly(smin, c0, c1, c2)
    smax = integral_sqrt_poly(smax, c0, c1, c2)

    return smax - smin


def arc_length_of_2d_curve(curve, a, b):

    t = np.linspace(a,b, 50001)
    xt, yt = curve(t=t, m=1)

    v = np.sqrt( xt**2 + yt**2)

    l = scipy.integrate.simps(v,t)
    return l




def compute_plume_coordinates(data, curve, show=False,
                              which='centers'):
    """
    Computes along- and across-plume coordinates analytically
    if curve.degree == 2.

    Parameters
    ----------
    data : satellite data incl. x, y and plume_area
    curve : center curve
    which : process either pixel 'centers' or 'corners'.

    """
    if curve.degree != 2:
        raise ValueError('Degree of curve needs to be 2 not %d' % curve.degree)

    a, b = curve.get_coefficients()

    # parameter for minimum distance to curve
    if 'plume_area' in data:
        area = data.plume_area.values
    else:
        area = np.ones(data.x.shape, bool)

    if which == 'centers':
        qx = data.x.values[area]
        qy = data.y.values[area]
    else:
        qx = data.xc.values[area].flatten()
        qy = data.yc.values[area].flatten()

    # coefficients for analytical solution
    c0 = 4*a[0]**2 + 4*b[0]**2
    c1 = 6*a[0]*a[1] + 6*b[0]*b[1]
    c2 = 4*a[0]*a[2] - 4*a[0]*qx + 2*a[1]**2 + 4*b[0]*b[2] - 4*b[0]*qy + 2*b[1]**2
    c3 = 2*a[1]*a[2] - 2*a[1]*qx + 2*b[1]*b[2] - 2*b[1]*qy

    roots = ddeq.misc.cubic_equation(c0, c1, c2, c3)
    real = np.abs(roots.imag) < 1e-6

    tmin = []
    n_no_solutions = 0
    n_multiple_solutions = 0


    for i in range(qx.size):

        n_solutions = np.sum(real[:,i])

        if n_solutions == 0:
            tmin.append(np.nan)
            n_no_solutions += 1

        elif n_solutions == 1:
            tmin.append( float(roots[:,i][real[:,i]].real) )

        elif n_solutions > 1:
            # use shortest arc length (which might fail for strongly bend plumes) 
            # using shortest distance fails, if curve bends back to source location
            j = np.argmin(roots[:,i].real)
            tmin.append(roots[j,i].real)

            n_multiple_solutions += 1

        else:
            raise ValueError

    if n_no_solutions > 0:
        name = ' '.join('%s' % v for v in [data.time.values, data.orbit, data.lon_eq])
        print('No real solution for some points in "%s"' % name)
        #raise ValueError('No real solution for some points in "%s"' %
        #                 name)

    if n_multiple_solutions > 0:
        name = ' '.join('%s' % v for v in [data.time.values, data.orbit, data.lon_eq])
        print('%d multiple solutions in %s (source: %s)' % (n_multiple_solutions, name, data.source.values))


    tmin = np.array(tmin)
    px, py = curve(t=tmin)

    # sign of distance (negative left of curve from source)
    t = curve.get_parameter(qx, qy)
    v = curve.compute_tangent(t, norm=True)
    n = np.array([px-qx, py-qy])
    cross = np.cross(v, n, axis=0)
    sign = np.sign(cross)

    if which == 'centers':

        # compute distance
        distance = xarray.full_like(data.x, np.nan)
        distance.values[area] = sign * np.sqrt((px - qx)**2 + (py - qy)**2)

        # arc-length
        arc = xarray.full_like(data.x, np.nan)
        arc.values[area] = compute_arc_length(curve, curve.t_o, tmin)

    else:
        # distance
        d = sign * np.sqrt((px - qx)**2 + (py - qy)**2)
        distance = xarray.full_like(data.xc, np.nan)
        distance.values[area] = d.reshape(d.size//4, 4)

        # arc-length
        a = compute_arc_length(curve, curve.t_o, tmin)
        arc = xarray.full_like(data.xc, np.nan)
        arc.values[area] = a.reshape(a.size//4, 4)

    if show:
        fig = plt.figure()
        ax = plt.subplot(aspect='equal')

        for i, (x,y) in enumerate(zip(qx, qy)):
            px, py = curve(t=tmin[i])
            ax.plot([px, x], [py, y], 'o-')

        ax.plot(*curve(t=np.linspace(0, tmin.max())), 'k-')


    return arc, distance




def compute_plume_line_and_coords(data, crs, plume_area=25e3):

    if 'detected_plume' not in data:
        return data, {}

    # convert to coordinate system using meters
    data = compute_xy_coords(data, crs=crs)
    
    # area around plume used for fitting center curve
    data['plume_area'] = xarray.zeros_like(data.detected_plume)

    curves = {}
    
    for source in data.source.values:
        
        # select source
        source_data = data.sel(source=source)
        
        # area for which data are prepared for mass-balance approach
        area = ddeq.misc.compute_plume_area(source_data, distance=plume_area, crs=crs)
        
        # use index, because sel method might fail according to documentation
        index = int(np.argmax(data.source.values == source))
        data['plume_area'][:,:,index] = area
        
        # compute curve
        if source_data['detected_plume'].sum() == 0 or ddeq.misc.has_multiple_sources(data, source):
            curves[source] = None

        else:
            if 'local_NO2_mean' in source_data:
                weights = source_data['local_NO2_mean'].values / 1e15
                weights[source_data.plume_area & ~source_data.detected_plume] = 0.2
                weights[weights < 0.2] = 0.2
            else:
                weights = source_data['local_CO2_mean'].values
                weights[source_data.plume_area & ~source_data.detected_plume] = 0.05
                weights[weights < 0.05] = 0.05

            # fit curve to detected plume plus surroundings
            if source in ['Berlin']:
                source_distance = 50e3
            else:
                source_distance = 20e3

            # source_distance, force_source, ... should be taken from source_data['type']
            curves[source] = create_line(data, source=source, degree=2,
                                         source_distance=20e3,
                                         force_source=True)

            data = compute_plume_coords(data=data, curve=curves[source],
                                        source=source, do_corners=False)
    
    
    
    return data, curves
    
