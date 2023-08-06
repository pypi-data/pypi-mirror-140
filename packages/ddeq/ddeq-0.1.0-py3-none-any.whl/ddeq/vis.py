
import os
import textwrap
import warnings

from matplotlib.colors import LinearSegmentedColormap, LogNorm

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import pandas


import ddeq.misc
import ddeq.massbalance

LON_EQ_TO_LETTER = {
    0: 'a',  401: 'b', 805: 'c', 1207: 'd', 1610: 'e', 2012: 'f'
}


def corners2grid(lon, lat):
    """
    Create lon, lat grid from four corners of pixel (n,m,4).
    """
    lonc = np.zeros((lon.shape[0], lon.shape[1]+1))
    lonc[:,:-1] = lon[:,:,0]
    lonc[:,-1] = lon[:,-1,1]

    latc = np.zeros((lat.shape[0], lat.shape[1]+1))
    latc[:,:-1] = lat[:,:,0]
    latc[:,-1] = lat[:,-1,1]

    return lonc, latc


def create_map(domain, add_colorbar=False, edgecolor='black',
               admin_level=1, fig_size=6.0, dright=0.0, ax=None):
    """
    Make a map for given domain (ddeq.misc.Domain).
    """

    dx = (domain.stoplon - domain.startlon)
    dy = (domain.stoplat - domain.startlat)

    if add_colorbar:
        dc = 1.0
        ll, rr = 0.017, 0.8-dright
    else:
        dc = 0.0
        ll, rr = 0.02, 0.96

    if ax is None:
        fig = plt.figure(figsize=(fig_size+dc, fig_size*dy/dx))
        ax = fig.add_axes([ll,0.02,rr,0.96], projection=domain.proj)

    else:
        fig = ax.get_figure()

    ax.set_aspect('equal', adjustable='box')

    ax.set_xlim(domain.startlon, domain.stoplon)
    ax.set_ylim(domain.startlat, domain.stoplat)

    if add_colorbar:
        cax = fig.add_axes([2*ll+rr,0.02,0.04,0.96])
    else:
        cax = None

    ax.coastlines(resolution='10m', color=edgecolor, linewidth=1.0)
    lines = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_0_boundary_lines_land',
        scale='10m',
    )
    ax.add_feature(lines, edgecolor=edgecolor, facecolor='none', linewidth=1.0)

    if admin_level > 0:
        lines = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='10m',
        )
        ax.add_feature(lines, edgecolor=edgecolor, facecolor='none', linewidth=0.5)

    return fig, ax, cax


def make_field_map(data, trace_gas, domain=None, vmin=None, vmax=None,
                   cmap='viridis', border=0.00, label='',
                   fig=None, alpha=None, xlim=None, ylim=None,
                   edgecolor='black', add_colorbar=True,
                   fig_size=6.0, dright=0.0, admin_level=1,
                   origin='lower'):
    """
    Make a map of 2D field.
    """
    rlon, rlat = data['rlon'], data['rlat']
    field = data[trace_gas]
    
    dlon = rlon[1] - rlon[0]
    left = rlon[0] - dlon / 2.0
    right = rlon[-1] + dlon / 2.0

    dlat = rlat[1] - rlat[0]
    bottom = rlat[0] - dlat / 2.0
    top = rlat[-1] + dlat / 2.0

    if fig is None:
        fig,ax,cax = create_map(domain, add_colorbar, edgecolor=edgecolor,
                                fig_size=fig_size, dright=dright,
                                admin_level=admin_level)
    else:
        ax, cax = fig.get_axes()
        cax.cla()

        # remove cosmo data
        ax.axes.get_images()[0].remove()

    
    c = ax.imshow(field, norm=None, vmin=vmin, vmax=vmax, cmap=cmap, zorder=-1,
                  aspect=ax.get_aspect(), origin=origin, 
                  extent=(left, right, bottom, top), transform=domain.proj)

    if add_colorbar:
        cb = plt.colorbar(c, cax=cax)
        cb.set_label(label)

    if alpha is not None:
        cm = LinearSegmentedColormap.from_list('alpha', [(1,1,1,0),(1,1,1,1)], 256)
        ax.imshow(alpha, vmin=0, vmax=1, cmap=cm, zorder=-1,
                  aspect=ax.get_aspect(), origin=origin,
                  extent=(left, right, bottom, top), transform=domain.proj)


    ax.set_xlim(left + border * dlon, right - border * dlon)
    ax.set_ylim(bottom + border * dlat, top - border * dlat)


    if xlim is not None:
        ax.set_xlim(*xlim)

    if ylim is not None:
        ax.set_ylim(*ylim)


    return fig





def make_level2_map(lon, lat, values, domain=None, fig=None,
                    vmin=None, vmax=None, label='', alpha=1.0,
                    cmap='viridis', clct=None, xlim=None, ylim=None,
                    edgecolor='black', is_discrete=False,
                    cb_labels=None, cb_labelsize='small',
                    truncate_cmap=False, do_zoom=False, zoom_area=None,
                    fig_size=6.0, dright=0.0, bg_color='silver',
                    admin_level=1, add_colorbar=True):
    """\
    Make a map of Level-2 satellite data.

    lon, lat :: longitude and latitude of pixel corners
    values   :: 2d field of level-2 data

    is_discrete :: bool (default False)
        if True uses colormap with discrete levels with one colour per values
        in fields
    """
    lon = np.asarray(lon)
    lat = np.asarray(lat)
    values = np.asarray(values)

    if values.dtype == bool:
        is_discrete = True

    if fig is None:
        fig,ax,cax = create_map(domain, add_colorbar=add_colorbar,
                                edgecolor=edgecolor,
                                fig_size=fig_size, dright=dright,
                                admin_level=admin_level)
    else:
        if isinstance(fig, plt.Figure):
            print('figure')
            ax, cax = fig.get_axes()
        else:
            ax, cax = fig
            fig = ax.get_figure()

    # draw background
    if bg_color is not None:
        bg_color = 255 * np.array(mpl.colors.to_rgb(bg_color))
        bg = np.tile(np.array(bg_color, dtype=np.uint8), [2,2,1])
        ax.imshow(bg, origin='upper', aspect=ax.get_aspect(),
                transform=ccrs.PlateCarree(),
                extent=[-180, 180, -180, 180]
        )

    if is_discrete:
        if hasattr(values, 'mask'):
            v = values[~values.mask].flatten()
        else:
            v = values.flatten()

        if cb_labels is None:
            n = len(set(v))
        else:
            n = len(cb_labels)

        if isinstance(cmap, list):
            cmap = LinearSegmentedColormap.from_list('list', cmap)
        else:
            cmap = plt.cm.get_cmap(cmap)

        bounds = np.arange(-0.5,n+0.5)
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    else:
        cmap = plt.cm.get_cmap(cmap)
        cmap.set_bad('#a0a0a0')

        norm = None

    if truncate_cmap:
        cmap = LinearSegmentedColormap.from_list(
                'new', cmap(np.linspace(0.25, 1.0, 101))
        )

    # create tiled grid
    if np.ndim(lon) == 3 and np.ndim(lat) == 3:
        lonc, latc = corners2grid(lon,lat)

        # FIXME: pcolormesh causes crash if calling ax.legend
        c = ax.pcolormesh(lonc, latc, values, vmin=vmin, vmax=vmax, cmap=cmap,
                          norm=norm, alpha=alpha, transform=ccrs.PlateCarree(),
                          edgecolors='None')
        c.set_rasterized(True)

        if clct is not None:
            cm = LinearSegmentedColormap.from_list('alpha', [(1,1,1,0),(1,1,1,1)], 256)
            c2 = ax.pcolormesh(lonc, latc, clct, vmin=0, vmax=1, cmap=cm,
                               transform=ccrs.PlateCarree())
            c2.set_rasterized(True)

    else:
        c = ax.scatter(lon, lat, c=values, vmin=vmin, vmax=vmax, cmap=cmap,
                       alpha=alpha, transform=ccrs.PlateCarree())


    if xlim is not None and np.all(np.isfinite(xlim)):
        ax.set_xlim(*xlim)
    if ylim is not None and np.all(np.isfinite(ylim)):
        ax.set_ylim(*ylim)

    if add_colorbar:
        cb = plt.colorbar(c, cax=cax)
        cb.set_label(label)

        if is_discrete:
            cb.set_ticks(np.arange(0,n+1))

        if cb_labels is not None:
            cb.set_ticklabels(cb_labels)
            cb.ax.tick_params(labelsize=cb_labelsize)

    if do_zoom:
        if zoom_area is None:
            zoom_area = np.isfinite(values)

        xmin, xmax = np.min(lon[zoom_area]), np.max(lon[zoom_area])
        ymin, ymax = np.min(lat[zoom_area]), np.max(lat[zoom_area])

        xmin, ymin = domain.proj.transform_point(xmin, ymin, ccrs.PlateCarree())
        xmax, ymax = domain.proj.transform_point(xmax, ymax, ccrs.PlateCarree())

        ax.set_xlim(xmin - 0.1, xmax + 0.1)
        ax.set_ylim(ymin - 0.1, ymax + 0.1)

    return fig




def _iter_contours(x, y, binary, nmax=4, tolerance=1.0):
    """
    Iter over contours.
    """
    x = np.array(x)
    y = np.array(y)
    binary = np.array(binary)

    for contour in skimage.measure.find_contours(binary, 0.5):
        coords = skimage.measure.approximate_polygon(contour, tolerance=tolerance)

        n,_ = np.shape(coords)
        if n <= nmax:
            continue

        i,j = coords[:,0].astype(int), coords[:,1].astype(int)
        yield x[i,j], y[i,j]


        
def draw_contours(ax, x, y, binary, ls='-', color='k', label=None,
                  tolerance=1.0, transform=ccrs.PlateCarree()):
    """
    Draw contours for given x and y coords to axis used for example for
    drawing outer border of CO2 plume.
    """
    line = []
    for x,y in _iter_contours(x, y, binary, tolerance=tolerance):
        line = ax.plot(x,y, color=color, ls=ls, transform=ccrs.PlateCarree(),
                       label=label)

        label = '_none_'

    return line

    

def add_hot_spots(ax, color='black', size='medium', suffixes=None, sources=None,
                  va='flex', ha='left', fontdict=None, bbox=None, ms=None,
                  do_path_effect=False, mec=None, add_labels=True,
                  add_wind=False, domain=None, time=None):
    """
    Add marker and name of hot spots to map.
    """
    
    if add_labels:
        if add_wind:
            ax.plot(0, -90, '>', color=color, transform=ccrs.PlateCarree(), mec=mec,
                    ms=ms, label='point source (with wind direction)', zorder=0)
        else:
            ax.plot(0, -90, 'D', color=color, transform=ccrs.PlateCarree(), mec=mec,
                    ms=ms, label='city', zorder=0)
            ax.plot(0, -90, 'o', color=color, transform=ccrs.PlateCarree(), mec=mec,
                    ms=ms, label='power plant', zorder=0)
            
        
    for i, key in enumerate(sources['source'].values, 1):
        
        source = sources.sel(source=key)
            
        lon = float(source['lon_o'])
        lat = float(source['lat_o'])
        text = str(source['UTF-8'].values)
        type_ = str(source['type'].values)
       
        if add_wind:
            
            delta=0.022
            delta=0.044
            
            # use rotated pole coords to avoid distortion
            rlon, rlat = ddeq.misc.transform_coords(lon, lat, ccrs.PlateCarree(), domain.proj,
                                                    use_xarray=False)

            u, v = ddeq.wind.get_wind(time, lon, lat, data_path='.', components='uv')

            scaling = np.sqrt(u**2 + v**2)
            u = u / scaling
            v = v / scaling

            ax.arrow(rlon, rlat, delta * u, delta * v, shape='full',
                     head_width=2.0 * delta, head_length= 2.0 * delta,
                     length_includes_head=True, fc='k', ec='w',
                     lw=1, transform=domain.proj, zorder=2
            )
            
        else:
            marker = 'D' if type_ == 'city' else 'o'
            ax.plot(lon, lat, marker, color=color, transform=ccrs.PlateCarree(),
                    mec=mec, ms=ms, label='_none_', zorder=10)

            
        if isinstance(ha, str):
            align = ha
        else:
            align = ha[i]
            
        if key in ['Staudinger', 'Heyden', 'Melnik']:
            align = 'left'
            
        if key == 'Pocerady':
            va = 'bottom'
        elif key == 'Prunerov':
            va = 'top'
        else:
            va = 'center'
            
        t = ax.text(lon, lat, f'  {text}  ', va=va, ha=align, fontsize=size,
                    transform=ccrs.PlateCarree(), color=color, clip_on=True,
                    fontdict=fontdict, bbox=bbox)
        t.set_clip_on(True)
        if do_path_effect:
            t.set_path_effects([PathEffects.withStroke(linewidth=2.5,
                                                       foreground='w')])

            
            
def add_area(ax, data, curve, xa, xb, ya, yb, color='yellow',
             add_label=True, extra_width=5e3, lw=None,
             do_middle_lines=True, lds=None, crs=None):
    
    # polygon (outside) 
    x_left = []
    x_right = []
    y_left = []
    y_right = []
    

    for i in range(xa.size):

        # interpolate distance from arc(t)
        xmin = curve.arc2parameter(xa[i])
        xmax = curve.arc2parameter(xb[i])
        y = np.array([ya[i], yb[i]])
            

        # compute normals
        (x0, x1), (y0, y1) = curve.compute_normal(xmin, t=y)
        (x3, x2), (y3, y2) = curve.compute_normal(xmax, t=y)

        if i == 0:
            x_right.extend([x0, x1, x2])
            x_left.append(x0)
            y_right.extend([y0, y1, y2])
            y_left.append(y0)
        else:
            x_right.append(x2)
            x_left.append(x3)
            y_right.append(y2)
            y_left.append(y3)
        
        # plot box
        if do_middle_lines and i > 0:
            xx,yy = np.array([x0, x1]), np.array([y0, y1])
            add_curve(ax, xx, yy, ls='-', lw=lw,
                      color=color, label=None, alpha=0.5,
                     crs=crs)

    if len(xa) == 1:
        x_left.append(x3)
        y_left.append(y3)
        
    label = 'Plume polygons' if add_label else None
    xx = np.array(x_right + list(reversed(x_left)))
    yy = np.array(y_right + list(reversed(y_left)))
    add_curve(ax, xx, yy, ls='-', lw=lw,
              color=color, label=label, crs=crs)
            

            
def update_legend(legend, new_lines=None, new_labels=None):

    if new_lines is None or new_labels is None:
        new_lines = []
        new_labels = []

    ax = legend.axes
    handles, labels = ax.get_legend_handles_labels()

    handles += new_lines
    labels += new_labels

    legend._legend_box = None
    legend._init_legend_box(handles, labels)
    legend._set_loc(legend._loc)
    legend.set_title(legend.get_title().get_text())

    legend.get_figure().canvas.draw()
            


def visualize(data, do_zoom=True, show_clouds=True, alpha=None,
              is_sentinel_5=False, data7=None, vlim=(-2,2),
              legend_loc='upper right', simple_legend=True, add_multiple_sources=True,
              trace_gas=None, show_true_plumes=True,
              sources=None, names=None, figwidth=6.97, vmin=None, vmax=None, add_wind=False,
              zoom_on=None, min_height=None, ax=None, cax=None, cmap=None,
              marker='+', markersize=3, domain=None, label=None, variable=None):
    """
    Visualize detected plume. Image is "trace_gas"/"variable"
    

    do_zoom :: zoom on plume instead of showing full domain
    show_clouds :: if true overlay cloudy pixels
    """
    
    
    if isinstance(data.time, str):
        time = pandas.Timestamp(data.time)
    else:
        time = pandas.Timestamp(data.time.values)
   
    if ax is None and cax is None:
        fig = None
    else:
        fig = ax, cax
    
    # show clouds?
    if show_clouds:
        cloud_threshold = data[trace_gas].attrs['cloud_threshold']
        clouds = data.clouds >= cloud_threshold
        clouds.attrs['threshold'] = cloud_threshold
    else:
        clouds = None
    
    if trace_gas == 'CO2':
        
        values =  data['CO2'] if variable is None else data[variable]

        # compute vmin and vmax
        if vmin is None and vmax is None:
            mean_bg = np.nanmean(values)
            vmin = round(mean_bg + vlim[0])
            vmax = round(mean_bg + vlim[1])

        fig = make_level2_map(
            data.lonc, data.latc, values, vmin=vmin,
            vmax=vmax, label='XCO$_2$ [ppm]' if label is None else label,
            clct=clouds, alpha=alpha,
            domain=domain, fig_size=figwidth, fig=fig, cmap=cmap
        )
    else:
        values =  data['NO2'] / 1e15 if variable is None else data[variable]
        
        if vmin is None:
            vmin = 0.0
        if vmax is None:
            vmax = 10.0
            
        fig = make_level2_map(
            data.lonc, data.latc, values, vmin=vmin, vmax=vmax, truncate_cmap=True,
            label='NO$_2$ column [10$^{15}$ molecules per cm$^2$]' if label is None else label,
            clct=clouds, alpha=alpha,
            domain=domain, fig_size=figwidth, fig=fig, cmap=cmap
        )
        
    if ax is None:
        ax, cax = fig.get_axes()
   
    # if sources not provided use source array from dataset instead
    if sources is None and 'source' in data:
        sources = data.copy()
        
    if sources.source.ndim == 0:
        pass
        
    if names is not None:
        sources = sources.sel(source=names)
    
    if sources is not None:
        add_hot_spots(ax, color='black', mec='white', ms=5, ha='right',
                      size='small', sources=sources, do_path_effect=True,
                      add_wind=add_wind, domain=domain, time=time)
   

    # lines and labels
    if show_clouds:
        label = 'Cloud fraction > %d%%' % (100*clouds.threshold)
        ax.plot(domain.pollon, domain.pollat, marker='s', mec='k', mfc='w', ls='',
                transform=ccrs.PlateCarree(), label=label)

    # true plumes
    if show_true_plumes:
        for tracer, ls in [('CO2', '-'), ('NO2', '--')]:
            name = '%s_true_plume' % tracer

            if name not in data:
                continue

            if tracer == 'CO2':
                if is_sentinel_5:
                    thr = data7[name].attrs['signal threshold (ppm)']
                else:
                    thr = data[name].attrs['signal threshold (ppm)']
                label = 'CO$_2$ plume (>%.2f ppm)' % thr

            elif tracer == 'NO2':
                try:
                    thr = data[name].attrs['signal threshold (molecules cm-2)']
                    label = r'NO$_2$ plume (>%.1f$\times$10$^{15}$ molec. cm$^{-2}$)' % (thr / 1e15)
                except KeyError:
                    thr = None
                    label = None
            else:
                label = name

            if hasattr(data, name):
                tolerance = 0.5 if is_sentinel_5 else 1.0
                draw_contours(ax, data.lon, data.lat,
                              data[name], label=label, ls=ls,
                              tolerance=tolerance)
                continue

            if hasattr(data7, name):
                draw_contours(ax, data7.lon, data7.lat,
                              data7[name], label=label, ls=ls)

    # detected plumes
    if ('detected_plume' in data and data.detected_plume is not None and
        np.sum(data.detected_plume) > 0):
        
        if np.ndim(data.detected_plume) == 3:
            plume = data.detected_plume.values.astype(bool)
        else:
            plume = data.detected_plume.values[:,:,np.newaxis].astype(bool)

        # plot multiple detections
        multiple_sources = plume.sum(2) > 1
        
        if add_multiple_sources:
            lon0 = data.lon.values[multiple_sources]
            lat0 = data.lat.values[multiple_sources]
            n_pixels = np.sum(multiple_sources)

            ax.plot(lon0, lat0, marker=marker, color='r', alpha=0.5,
                    ms=markersize, ls='', transform=ccrs.PlateCarree(),
                    label='Multiple sources (%d px)' % n_pixels)
        
        # plot other plumes
        if zoom_on is not None:
            if 'other_sources' in data:
                other_sources = data['other_sources'].values
            else:
                other_sources = data.detected_plume.any('source') & ~data.detected_plume.sel(source=zoom_on)
                
            lon0 = data.lon.values[other_sources]
            lat0 = data.lat.values[other_sources]

            ax.plot(lon0, lat0, marker=marker, color='r', alpha=0.5,
                    ms=markersize, ls='', transform=ccrs.PlateCarree(),
                    label='Other sources')
        
        
        # zoom on detected or specific plume detection
        for source in sources['source'].values:

            if zoom_on is not None and zoom_on != source:
                continue
            
            try:
                name = str(sources.sel(source=source)['UTF-8'].values)
                this = data.sel(source=source)
            except KeyError:
                continue
             
            lon0 = data.lon.values[this.detected_plume & ~multiple_sources]
            lat0 = data.lat.values[this.detected_plume & ~multiple_sources]
            n_pixels = lon0.size

            if sources is None and n_pixels == 0:
                continue

            if simple_legend:
                label = '%s (%d px)' % (name, n_pixels)
            else:
                label = 'detected plume (q = %.3f, n = %d)\nwith %d pixels' 
                label %= (
                    data.attrs['probability for z-value'],
                    data.attrs['size of neighborhood'],
                    n_pixels
                )
            
            ax.plot(lon0, lat0, marker=marker, mec='k',
                    ms=2*markersize if is_sentinel_5 else markersize,
                    mfc='k', ls='',
                    transform=ccrs.PlateCarree(), label=label,
                    alpha=0.5 if zoom_on is None else 1.0)

        
    if do_zoom and 'detected_plume' in data:
        
        if zoom_on is not None and 'source' in data.dims:
            data = data.sel(source=zoom_on)
        
        if np.ndim(data['detected_plume']) == 3:
            lon_o = data['lon_o'].values
            lat_o = data['lat_o'].values
            
            lon = np.concatenate([lon_o, data.lon.values[data['detected_plume'].any('source')].flatten()])
            lat = np.concatenate([lat_o, data.lat.values[data['detected_plume'].any('source')].flatten()])
        else:
            if 'lon_o' in data:
                lon_o = data['lon_o'].values
                lat_o = data['lat_o'].values
            else:
                lon_o, lat_o, _ = misc.get_source_origin(source[0])
                
            lon = np.concatenate([[lon_o], data.lon.values[data['detected_plume']].flatten()])
            lat = np.concatenate([[lat_o], data.lat.values[data['detected_plume']].flatten()])

            
        rlon_0, rlat_0 = ddeq.misc.transform_coords(lon, lat, ccrs.PlateCarree(), domain.proj,
                                                    use_xarray=False)
        dy = 0.1
        dx = 0.1
        
        xmin, xmax = min(rlon_0) - dx, max(rlon_0) + dx
        ymin, ymax = min(rlat_0) - dy, max(rlat_0) + dy
        
        # make figure at least 200 km high
        if min_height is None:
            min_height = 2.0 if zoom_on is None else 1.0
            
        if ymax - ymin < min_height:
            ymid = ymin + 0.5 * (ymax - ymin)
            ymin = ymid - 0.5 * min_height
            ymax = ymid + 0.5 * min_height
   
        # make figure have same aspect ratio as model domain
        dx = 0.5 * (1.15 * (ymax - ymin) - (xmax - xmin))
        xmin = xmin - dx
        xmax = xmax + dx
        
        # shift limits when outside of domain boundary
        if xmin < domain.rlon[0]:
            shift = domain.rlon[0] - xmin
            xmin += shift
            xmax += shift
            
        if xmax > domain.rlon[-1]:
            shift = xmax - domain.rlon[-1]
            xmin -= shift
            xmax -= shift
        
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        
    else:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        ax.set_xlim(xmin+0.01*50, xmax-0.01*50)
        ax.set_ylim(ymin+0.01*50, ymax-0.01*50)

        
    legend = ax.legend(loc=legend_loc, numpoints=1, markerscale=1.5,
                       fontsize='small')

    #for lh in legend.legendHandles: 
    #    lh._legmarker.set_alpha(1)

    return fig




def add_curve(ax, x, y, crs, label=None,
              color=None, ls='-', lw=None, marker='', mec=None, ms=None,
              alpha=None, zorder=None):
    """\
    Add a curve to map.
    """
    lines = ax.plot(x, y, ms=ms, ls=ls, lw=lw, color=color, transform=crs,
                    label=label, marker=marker, mec=mec, alpha=alpha, zorder=zorder)

    #if label is not None:
    #    legend = ax.get_legend()
    #    update_legend(legend)
    #    for lh in ax.get_legend().legendHandles: 
    #        lh._legmarker.set_alpha(1)
                
    return lines




def show_detected_plumes(data, curves, variable, ld=None, add_polygons=True, zoom_on=None, figwidth=6.97,
                         ax=None, cax=None, cmap=None, alpha=None, min_height=None, add_multiple_sources=True,
                         vmin=None, vmax=None, add_wind=True, domain=None, add_origin=False, marker='+',
                         label=None, do_zoom=True, crs=None):
    """
    Show detected plumes in swath and add curves and control polygons if available.
    """
    first = True # first time adding polygons
    
    fig = visualize(data, do_zoom=do_zoom, show_clouds=True, legend_loc='upper left',
                    trace_gas=variable, zoom_on=zoom_on, figwidth=figwidth, ax=ax, cax=cax,
                    cmap=cmap, alpha=alpha, min_height=min_height, vmin=vmin, vmax=vmax,
                    add_multiple_sources=add_multiple_sources, add_wind=add_wind,
                    domain=domain, marker=marker, label=label)
    
    if ax is None:
        ax, cax = fig.get_axes()
        
       
    for i, source in enumerate(data.source.values):
        
    
        if zoom_on is not None and source != zoom_on:
            continue
    
        d = data.sel(source=source)

        if source in curves and curves[source] is not None:
            
            plume = d['detected_plume']
        
            if ld is None:
                source_type = str(d['type'].values)
                xa, xb, ya, yb = ddeq.misc.compute_polygons(d, source_type=source_type)
            else:
                xa, xb = ld.xa[i], ld.xb[i]
                ya, yb = ld.ya[i], ld.yb[i]
                
            # don't draw curves for overlapping plumes
            if ddeq.misc.has_multiple_sources(data, source):
                continue
                
            
            x = d['x'].values[plume]
            y = d['y'].values[plume]
            curve = curves[source]
         
            tmax = curve.arc2parameter(xb[-1])
            t = np.linspace(curve.t_o, tmax)            
            
            add_curve(ax, *curve(t=t), zorder=10, crs=crs,
                      color='black', label='Center lines' if first else None)
            
            if add_polygons:
                
                # polygon upstream
                add_area(ax, d, curve, xa[:1], xb[:1], ya[:1], yb[:1],
                              add_label=first, lw=1, crs=crs,
                              do_middle_lines=True)     
                
                # polygons downstream
                add_area(ax, d, curve, xa[1:], xb[1:], ya[1:], yb[1:],
                              add_label=False, lw=1, crs=crs,
                              do_middle_lines=True)     
                
            if add_origin:
                add_curve(ax, curve.x0, curve.y0, marker='D', crs=crs,
                          ls='', color='yellow', mec='k', ms=5,
                          label='Origin ($x_o$, $y_o$)' if first else None)
            first = False
            
    return fig       





def add_text(ax, data, ld, source, data_path):
    time = pandas.Timestamp(data.time.values)
    
    this = data.sel(source=source)
    plume_age, plume_length = ddeq.misc.compute_plume_age_and_length(ld)

    text = """\
        {satellite} ({time}, Orbit: {orbit})

        Instrument scenario:
        • CO$_2$: $\sigma_\\mathrm{{VEG50}}$ = 0.7 ppm
        • NO$_2$: $\sigma_\\mathrm{{ref}}$ = 2$\\times$10$^{{15}}$ molcules cm$^{{-2}}$

        Plume information:
        • Detection: {detection_tracer} (q = {q}, $\sigma_g$ = {ns} px)
        • Plume size: {plume_size:d} px
        • Plume length: {plume_length:.1f} km
        • Estimated plume age: {plume_age:.1f} h
        • Mean wind: {speed:.1f} m s$^{{-1}}$, {direction:.0f} degrees
        • Angle between curve and wind: {angle:.0f} degrees

        True emissions (10:30 UTC):
        • CO$_2$: {true_CO2_flux:.1f} Mt yr$^{{-1}}$
        • NO$_x$: {true_NO2_flux:.1f} kt yr$^{{-1}}$

        Estimated emissions:
        • CO$_2$ flux: {CO2_flux:.1f}$\pm${CO2_flux_std:.1f} Mt yr$^{{-1}}$
        • NO$_x$ flux: {NO2_flux:.1f}$\pm${NO2_flux_std:.1f} kt yr$^{{-1}}$
        • NO$_x$ decay time: {NOX_decay:.1f}$\pm${NOX_decay_std:.1f} h


    """.format(satellite='CO2M%s' % LON_EQ_TO_LETTER.get(data.lon_eq, ''),
               time=time.strftime('%d %b %Y, %H:%M UTC'),
               orbit=data.orbit,
               detection_tracer=data.attrs['trace_gas'].replace('2', '$_2$'),
               q=data.attrs['probability for z-value'],
               ns=data.attrs['filter_size'],
               speed=ld.CO2_flux_fit.attrs['wind_speed'],
               direction=ld.CO2_flux_fit.attrs['wind_direction'],
               angle=ld.attrs.get('angle_between_curve_and_wind', -9999),
               CO2_flux=ld.CO2_flux_fit.attrs['emissions'],           
               CO2_flux_std=ld.CO2_flux_fit.attrs['emissions_std'],  
               NO2_flux=ld.NO2_flux_fit.attrs['emissions'],           
               NO2_flux_std=ld.NO2_flux_fit.attrs['emissions_std'],       
               NOX_decay=ld.NO2_flux_fit.attrs['decay_time'],           
               NOX_decay_std=ld.NO2_flux_fit.attrs['decay_time_std'],
               plume_length=plume_length,
               plume_age=plume_age,
               plume_size=int(this.detected_plume.values.sum()),
               true_CO2_flux=ddeq.misc.read_true_emissions(time, 'CO2', source, tmin=10, tmax=11, data_path=data_path).mean(),
               true_NO2_flux=ddeq.misc.read_true_emissions(time, 'NO2', source, tmin=10, tmax=11, data_path=data_path).mean()
              )
    text = textwrap.dedent(text)
    plt.figtext(0.76, 0.47, text, va='top', linespacing=1.1)
    

    
def add_lines(ax, edgecolor='k'):
    ax.coastlines(resolution='10m', color=edgecolor, linewidth=1.0)
    lines = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_0_boundary_lines_land',
        scale='10m',
    )
    ax.add_feature(lines, edgecolor=edgecolor, facecolor='none', linewidth=1.0)

    lines = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='10m',
    )
    ax.add_feature(lines, edgecolor=edgecolor, facecolor='none', linewidth=0.5)
    
    
    
def plot_along_plume(ld, time, source, figwidth=6.97, ax1=None, ax2=None, no2_scaling=1.0, data_path='.'):

    if ax1 is None or ax2 is None:
        fig, (ax1, ax2) = plt.subplots(2,1, sharex=True, figsize=(6.97,4))
    else:
        fig = ax1.get_figure()

    factor = ddeq.misc.kgs_to_Mtyr(1.0)
    
    ax1.errorbar(ld['along'] / 1e3, factor * ld['CO2_flux'], factor * ld['CO2_flux_std'],
                 marker='o', ms=4, ls='', label='Along-plume estimates')
    ax2.errorbar(ld['along'] / 1e3, 1e3 * factor * ld['NO2_flux'], 1e3 * factor * ld['NO2_flux_std'],
                 marker='o', ms=4, ls='', label='Along-plume estimates')

    
    # CO2
    Q = ld['CO2_flux_fit'].attrs['emissions']
    u = ld['CO2_flux_fit'].attrs['wind_speed']
    Q_std = ld['CO2_flux_fit'].attrs['emissions_std']

    x = np.linspace(ld['along'][0] - 2.5e3, ld['along'][-1] + 2.5e3, 501)
    y = np.interp(x, ld['along'], ld['CO2_flux_fit'])
    
    label = 'Estimated emissions (Q = %.1f$\pm$%.1f Mt yr$^{-1}$, u = %.1f m s$^{-1}$)' % (Q, Q_std, u)
    label = 'Estimated emissions'
    ax1.plot(x / 1e3, y, label=label, color='C0', ls='--')

    # NO2
    Q = ld['NO2_flux_fit'].attrs['emissions']
    u = ld['NO2_flux_fit'].attrs['wind_speed']
    tau = ld['NO2_flux_fit'].attrs['decay_time']
    
    Q_std = ld['NO2_flux_fit'].attrs['emissions_std']
    tau_std = ld['NO2_flux_fit'].attrs['decay_time_std']
        
    x = np.linspace(ld['along'][0] - 2.5e3, ld['along'][-1] + 2.5e3, 501)
    y = np.interp(x, ld['along'], ld['NO2_flux_fit'])
        
    label = 'Estimated emissions (Q = %.1f$\pm$%.1f kt yr$^{-1}$, u = %.1f m s$^{-1}$, $\\tau$ = %.1f$\pm$%.1f h)' % (Q, Q_std, u, tau, tau_std)    
    label = 'Estimated emissions' 
    ax2.plot(x / 1e3, y, label=label, color='C0', ls='--')

    # true emissions
    q_CO2 = ddeq.misc.read_true_emissions(time, species='CO2', source=source, tmin=10, tmax=11, data_path=data_path).mean()
    q_NOx = no2_scaling * ddeq.misc.read_true_emissions(time, species='NO2', source=source, tmin=10, tmax=11, data_path=data_path).mean()   
    
    right = ld['along'][-1] / 1e3 + 2.5
    ax1.hlines([q_CO2], 0.0, right, color='C1', label='True emissions')# (Q = %.1f Mt yr$^{-1}$)' % q_CO2)
    ax2.hlines([q_NOx], 0.0, right, color='C1', label='True emissions')# (Q = %.1f kt yr$^{-1}$)' % q_NOx)

    # labels
    ax1.set_ylabel('CO$_2$ flux [Mt yr$^{-1}$]')
    ax2.set_ylabel('NO$_\mathrm{x}$ flux [kt yr$^{-1}$]')
    
    for ax in [ax1, ax2]:
        if q_NOx < 25:
            ax.set_ylim(-10, 60)        
        else:
            ax.set_ylim(-25, 100)
        ax.grid(True)

        ax.legend(fontsize='small', ncol=1)

        right = ld['along'].max() / 1e3 + 5.0
        xticks = np.array( sorted(set(list(ld.xa.values) + list(ld.xb.values))) ) / 1e3
        ax.set_xticks(xticks)
        ax.set_xlim(xticks[0], xticks[-1])
        
    ax2.set_xlabel('Along plume distance [km]')
        
    return fig



def plot_across_section(polygon, tracer='CO2', method='sub-areas',
                        show_true=False, add_errors=True, ax=None, no_twinx=True,
                        legend='standard'):
    """
    Plot across plume concentrations and line densities from means of
    sub-polygons or curve fits.
    """
    if tracer == 'NO2':
        fmt = '%.0f$\pm$%.0f$\,$g$\,$m$^{-1}$'
        true_fmt = '%.0f$\,$g$\,$m$^{-1}$'
        factor = 1e6

    elif tracer == 'CO2':
        fmt = '%.0f$\pm$%.0f$\,$kg$\,$m$^{-1}$'
        true_fmt = '%.0f$\,$kg$\,$m$^{-1}$'
        factor = 1e3

    elif tracer == 'both':
        fmt = '%.0f$\pm$%.0f$\,$g$\,$m$^{-1}$'
        true_fmt = '%.0f$\,$g$\,$m$^{-1}$'
        factor = 1e6
    else:
        raise ValueError # TODO



    if method in ['gauss', 'both']:
        
        raise NotImplementedError

        # third of page
        figsize = np.array(plt.rcParams['figure.figsize']) * 2 / 3
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes([0.16,0.17,0.82,0.8])

        y = polygon['y'].values
        c = polygon[tracer].values
        detection = polygon['is_plume'].values


        if show_true:
            ax.plot(y_true/1e3, factor*c_true, 'D', color='tab:blue', ms=3,
                    label='Model tracer (%s)' % true_fmt % true_density)

        if not add_errors:
            ax.plot(y[detection]/1e3, factor*c[detection],
                        ls='', marker='o', markersize=5, color='tab:red',
                        label='Inside detected plume')

            ax.plot(y[~detection]/1e3, factor*c[~detection],
                        ls='', marker='o', markersize=5, color='tab:red', mfc='none',
                        label='Outside detected plume')

        else:
            ax.errorbar(y[detection]/1e3, factor*c[detection], factor*c_std[detection],
                        ls='', marker='o', markersize=5, color='tab:red',
                        label='Inside detected plume')

            ax.errorbar(y[~detection]/1e3, facotr*c[~detection], factor*c_std[~detection],
                        ls='', marker='o', markersize=5, color='tab:red', mfc='none',
                        label='Outside detected plume')

        if method in ['sub-areas', 'both']:

            ss = polygon['subpolygons']
            area_means = polygon['c_sub']
            area_means_std = polygon['c_std_sub']

            mass_means = results['sub-areas']
            mass_means_std = results['sub-areas_std']

            ax.plot(ss/1e3, factor*area_means, lw=2, ds='steps-mid', color='black',
                    label='Sub-area means (%s)' % fmt % (factor*mass_means/1e3,
                                                         factor*mass_means_std/1e3))

        if method in ['both', 'gauss', 'gaussian']:

            mass_gauss = results['gauss']
            mass_gauss_std = results['gauss_std']

            ax.plot(results['y_fit']/1e3, factor * results['gauss_fit'], lw=2,
                    color='black', label='Gaussian function (%s)' % fmt %
                    (factor*mass_gauss/1e3, factor*mass_gauss_std/1e3), ls='--')


        ax.set_ylim(bottom=min(0.0, ax.get_ylim()[0]))

        ax.grid(True)
        ax.legend(fontsize='small', ncol=1)
        ax.set_xlabel('Across-plume direction (km)')

        if tracer.startswith('NO2'):
            ax.set_ylabel('%s$_2$ columns (mg m$^{-2}$)' % tracer[:2])
        else:
            ax.set_ylabel('%s$_2$ columns (g m$^{-2}$)' % tracer[:2])


    elif method in ['two-gauss', 'sub-areas']:

        figsize = plt.rcParams['figure.figsize']
        figsize = [figsize[0], figsize[1] * 2 / 3]

        if ax is None:
            fig = plt.figure(figsize=figsize)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = ax
            fig = ax.get_figure()
            
        if no_twinx:
            ax2 = ax1
            ax3 = ax1
        else:
            ax2 = ax1.twinx()
            ax3 = fig.add_axes(ax1.get_position(), sharex=ax1, sharey=ax1)
            ax3.set_axis_off()

        lines = []

        y = polygon['y']
        detection = polygon['is_plume'].values
        # CO2 measurements
        if tracer in ['CO2', 'both']:
            
            c1 = polygon['CO2']
            c1_std = polygon['CO2_std']
            
            if no_twinx:
                label = 'CO$_2$ [g m$^{-2}$]'
            else:
                label = 'CO$_2$'

            if add_errors:
                lines.append( ax1.errorbar(y/1e3, 1e3*c1, 1e3*c1_std, color='tab:red', mfc='none',
                                           marker='o', ms=5, ls='', label=label) )
            else:
                lines += ax1.plot(y/1e3, 1e3*c1, 'o', color='tab:red', mfc='none',
                                  ms=5, label=label)

        # NO2 measurements
        if tracer in ['NO2', 'both']:
            
            c2 = polygon['NO2']
            c2_std = polygon['NO2_std']

            if no_twinx:
                label = 'NO$_2$ [mg m$^{-2}$]'
            else:
                label = 'NO$_2$'

            if add_errors:
                ax2.errorbar(y[detection]/1e3, 1e6*c2[detection], 1e6*c2_std[detection],
                             color='tab:blue', mfc='tab:blue',
                             marker='s', ms=5, ls='')

                lines.append(ax2.errorbar(y[~detection]/1e3, 1e6*c2[~detection], 1e6*c2_std[~detection],
                                      color='tab:blue', mfc='none', marker='s', ls='',
                                      ms=5, label=label))
            else:
                ax2.plot(y[detection]/1e3, 1e6*c2[detection], 's',
                         color='tab:blue', ms=5)

                lines +=ax2.plot(y[~detection]/1e3, 1e6*c2[~detection], 's',
                                 color='tab:blue', mfc='none',
                                 ms=5, label=label)

        if method == 'sub-areas':
            
            
            for i, tracer in enumerate(['CO2', 'NO2']):
            
                factor = {'CO2': 1.0, 'NO2': 1e3}[tracer]
            
                ss = polygon['subpolygons']
                area_means = polygon['%s_sub' % tracer]
                area_means_std = polygon['%s_std_sub' % tracer]

                mass_means = polygon['%s_line_density' % tracer]
                mass_means_std = polygon['%s_line_density' % tracer]

                lines +=ax3.plot(ss/1e3, 1e3*factor*area_means, lw=2, ds='steps-mid', color='black',
                                 ls=['-', '--'][i],
                                 label='Sub-area means (%s)' % fmt % (factor*mass_means,
                                                                      factor*mass_means_std))

        else:
            # CO2 fit
            if 'CO2_line_density' in polygon:
                s = polygon['y_fit']
                co2 = polygon['CO2_fit']

                if legend == 'simple':
                    label = 'CO$_2$ fit'
                else:
                    fmt = '%.0f$\pm$%.0f$\,$kg$\,$m$^{-1}$'
                    label='CO$_2$ fit (%s)' % fmt % (polygon['CO2_line_density'], polygon['CO2_line_density_std'])

                lines += ax3.plot(s/1e3, 1e3*co2, 'k-', lw=2, label=label)

            # NO2 fit
            if 'NO2_line_density' in polygon:
                s = polygon['y_fit']
                no2 = polygon['NO2_fit']

                if legend == 'simple':
                    label='NO$_2$ fit'
                else:
                    if np.isnan(polygon['NO2_line_density_std']):
                        fmt = '%.0f$\,$g$\,$m$^{-1}$'
                        label = fmt % (1e3 * polygon['NO2_line_density'])
                    else:
                        fmt = '%.0f$\pm$%.0f$\,$g$\,$m$^{-1}$'
                        label = fmt % (1e3 * polygon['NO2_line_density'], 1e3 *
                                       polygon['NO2_line_density_std'])

                    label='NO$_2$ fit (%s)' % label

                lines += ax2.plot(s/1e3, 1e6*no2, 'k--', lw=2, label=label)

                
        if tracer == 'CO2':
            ax1.set_ylabel('CO$_2$ columns [g m$^{-2}$]')
            ax1.grid(True)
            
        elif tracer == 'NO2':
            ax1.set_ylabel('NO$_2$ columns [mg m$^{-2}$]')
            ax1.grid(True)
            
        else:
            if no_twinx:
                ax1.set_ylabel('Column densities')
                ax1.grid(True)

            else:
                ax1.set_ylabel('CO$_2$ columns [g m$^{-2}$]')
                ax1.grid(True)

                ax2.set_ylabel('NO$_2$ columns [mg m$^{-2}$]')

        
        # ylim
        if tracer == 'both': # TODO: implement for CO2 and NO2
            top = max(50.0, np.ceil(np.max(1e3 * c1))+10, np.ceil(np.max(1e3 * c2))+10)
            bottom = min(-25, np.floor(np.min(1e3 * c1))-10, np.floor(np.min(1e3 * c2))-10)
            top = np.ceil(top/25) * 25
            bottom = np.floor(bottom/25) * 25

            ax1.set_ylim(bottom, top)
            ax2.set_ylim(bottom, top)

        ncol = 1 if legend == 'simple' else 2
        loc = 'upper right' if legend == 'simple' else 0
        
        ax3.legend(lines, [l.get_label() for l in lines], fontsize='small',
                   ncol=ncol, loc=loc)

        ax1.set_xlabel('Across-plume direction [km]')

    else:
        raise ValueError
        
    return fig


    
    

def plot_mass_balance(data, curves, line_densities, source, no2_scaling=1.0, domain=None, crs=None, data_path='.'):
    time = pandas.Timestamp(data.time.values)

    with plt.style.context({'font.size': 10}):
        # figure size (13.94, 6.5) fits on wide screen power point and two figures per page in Copernicus journal.
        scaling = 1.0
        figsize= (13.94*scaling, 7.45 * scaling)
        fig = plt.figure(figsize=figsize)

        # size of level-2 image
        aspect = (domain.rlon[-1] - domain.rlon[0]) / (domain.rlat[-1] - domain.rlat[0])
        height = (figsize[1] - 0.7) / 2
        width =  height * aspect
        dy = 0.7 / 4 / figsize[1]
        rel_height = height / figsize[1]
        rel_width = width / figsize[0]

        axes = [None, None]
        caxes = [None, None]

        for i in [0,1]:
            axes[i] = fig.add_axes([
                0.01,
                dy + i * (rel_height + 2 * dy) - 0.005,
                rel_width,
                rel_height],
                projection=domain.proj
            )
            axes[i].set_aspect('equal', adjustable='box')
            axes[i].set_xlim(domain.startlon, domain.stoplon)
            axes[i].set_ylim(domain.startlat, domain.stoplat)
            add_lines(axes[i])

            axes[i].set_title('(%s)' % 'ba'[i])

            caxes[i] = fig.add_axes([
                0.02 + rel_width,
                dy + i * (rel_height + 2 * dy) - 0.005,
                0.01, 
                rel_height]
            )

            fig = show_detected_plumes(data, curves, ld=None, add_polygons=True, add_wind=True,
                                       domain=domain, variable=['NO2', 'CO2'][i],
                                       zoom_on=source, ax=axes[i], cax=caxes[i],
                                       crs=crs)

        # mass balance
        h = (dy + rel_height - 0.06 - 0.015) / 2
        left = 0.02 + rel_width + 0.12

        # other axes
        ax1 = fig.add_axes([
            left,
            0.06 + 0.015 + h,
            0.32,  #0.38,
            h,
        ])
        ax2 = fig.add_axes([
            left,
            0.06,
            0.32, #0.38,
            h])
        
    
        plot_along_plume(line_densities, time=time, source=source, ax1=ax1,
                         ax2=ax2, no2_scaling=no2_scaling, data_path=data_path)       
        ax1.set_xticklabels([])
        ax1.set_title('(d)')


        w = 0.02 + rel_width + 0.12 + 0.38 + 0.02
        
        #tax = fig.add_axes([
        #    w,
        #    0.01,
        #    1.0 - w - 0.02,     
        #    2*h + 0.015 + 0.05,
        #])
        #
        #tax.set_xticklabels([])
        #tax.set_yticklabels([])
        add_text(None, data, line_densities, source, data_path=data_path)
        
        if line_densities.pixels.size == 0:
            return fig
        
        
        # cross sections for first six cases (  0.98)
        axes = []
        
        # upper row
        for i in [0,1,2]:
            ax = fig.add_axes([
                left + i * (0.58/3 - 0.01 + 0.01),
                dy + (rel_height + 2 * dy) + 0.05 + h,
                0.58/3 - 0.01,
                h - 0.01,
            ])
            
            axes.append(ax)
        
        # lower row
        for i in [0,1,2]:            
            ax = fig.add_axes([
                left + i * (0.58/3 - 0.01 + 0.01),
                dy + (rel_height + 2 * dy) + 0.04,
                0.58/3 - 0.01,
                h - 0.01,
            ])
            axes.append(ax)
        
        # plot line densities
        n = line_densities.along.size
        
        if n <= 6:
            alongs = np.arange(n)
        else:
            alongs = [0, 1, 2, 3, n-2, n-1]
        
        for i, ax in zip(alongs, axes):
            
            if 0 <= i < line_densities.along.size:
                polygon = line_densities.isel(along=i)
                
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
                    
                    plot_across_section(polygon, tracer='both',
                                            method=polygon.method,
                                            show_true=False,
                                            add_errors=True, ax=ax, no_twinx=True,
                                            legend='simple')

                ax.text(0.01, 0.98, '%d-%d km' % (polygon.xa/1e3, polygon.xb/1e3),
                        va='top', ha='left', transform=ax.transAxes)
                
                ax.set_ylabel('Column densities')
            
        bottom = min(ax.get_ylim()[0] for ax in axes)
        top = max(ax.get_ylim()[1] for ax in axes)
        
        # update labels etc.
        for i, ax in enumerate(axes):
            ax.set_ylim(bottom, top)
            
            if i == 1:
                ax.set_title('(c)')
            
            if i in [0,1,2]:
                ax.set_xticklabels([])
                ax.set_xlabel('')
            
            if i not in [0,3]:
                ax.set_yticklabels([])
                ax.set_ylabel('')
                
            if i != 5:
                legend = ax.get_legend()
                
                if legend is not None:
                    legend.remove()
            else:
                ax.legend(ncol=4, loc='lower right')
        
        return fig
