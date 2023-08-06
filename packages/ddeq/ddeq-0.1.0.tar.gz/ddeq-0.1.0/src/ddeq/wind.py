
import os

import cdsapi
import numpy as np
import xarray


def calculate_wind_direction(u, v):
    return (270.0 - np.rad2deg(np.arctan2(v,u))) % 360


def get_wind(time, lon, lat, data_path, components='uv'):
    
    p, u, v = get_era5_wind_profile(time, lon, lat, data_path=data_path)
    
    # TODO: use weights
    u = u.mean('level')
    v = v.mean('level')
        
    if components == 'uv':
        return u, v
    
    else:
        wind_speed = np.sqrt(u**2 + v**2)
        wind_direction = calculate_wind_direction(u, v)
        return wind_speed, wind_direction
    

def download_era5_winds(time, data_path='.', overwrite=False):
    
    era5_filename = os.path.join(data_path, time.strftime('ERA5-wind-%Y%m%d_%H%M.nc'))
    
    if os.path.exists(era5_filename) and not overwrite:
        return
    
    
    cds = cdsapi.Client()

    r = cds.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': [
                'u_component_of_wind', 'v_component_of_wind',
            ],
            'pressure_level': [
                '800', '825', '850',
                '875', '900', '925',
                '950', '975', '1000',
            ],
            "date": time.strftime('%Y-%m-%d'),
            "time": time.strftime('%H:00'),
            "area": [90, -180, -90, 180], # north, east, south, west
        }, era5_filename
    )
    

def get_era5_wind_profile(time, lon, lat, data_path='.'):

    era5_filename = os.path.join(data_path, time.strftime('ERA5-wind-%Y%m%d_%H%M.nc'))
    download_era5_winds(time, data_path, overwrite=False)

    with xarray.open_dataset(era5_filename) as era5:
        era5 = era5.load().sel(time=time, longitude=lon, latitude=lat, method='nearest')

    pressure = era5['level']
    u_profile = era5['u']
    v_profile = era5['v']  
    
    return pressure, u_profile, v_profile


