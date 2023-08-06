
import numpy as np
import pandas
import xarray

import ucat
import ddeq


def compute_plume_signal(data, trace_gas):
    """
    Compute plume signal for trace gas
    """
    name = f'{trace_gas}_minus_estimated_background'
    signal = data[trace_gas] - data[f'{trace_gas}_estimated_background']

    data[name] = xarray.DataArray(signal, dims=data[trace_gas].dims,
                                  attrs=data[trace_gas].attrs)
    return data


def prepare_data(data, trace_gas='CO2'):
    """
    Prepare mass-balance approach:
    - estimate CO2 and NO2 background
    - convert units to mass column densities (kg/m²)
    """
    data[f'{trace_gas}_isfinite'] = np.isfinite(data[trace_gas])

    # estimate background
    data = ddeq.background.estimate(data, trace_gas)
    

    # compute CO2/NO2 enhancement
    data = compute_plume_signal(data, trace_gas)
    
    # convert ppm to kg/m2
    for variable in [trace_gas, f'{trace_gas}_estimated_background', f'{trace_gas}_minus_estimated_background']:
    
        values = data[variable]
        attrs = values.attrs

        name = f'{variable}_mass'
        
        if data[trace_gas].attrs['units'] == 'molecules cm-2':
            input_unit = 'cm-2'
        elif data[trace_gas].attrs['units'] == 'ppm':
            input_unit = 'ppmv'
        else:
            raise ValueError('No units in dataset')
            
        
        data[name] = xarray.DataArray(
            ucat.convert_columns(values, input_unit, 'kg m-2',
                                 p=data['psurf'], molar_mass=trace_gas),
            dims=values.dims, attrs=values.attrs
        )
       
        if 'noise_level' in attrs:
            noise_level = attrs['noise_level']

            # noise scenarios from SMARTCARB project
            if isinstance(noise_level, str):
                if trace_gas == 'CO2':
                    noise_level = {'low': 0.5, 'medium': 0.7, 'high': '1.0'}[noise_level]
                elif trace_gas == 'NO2':
                    noise_level = {'low': 1.0e15, 'high': 2e15, 'S5': 1.3e15}[noise_level]
                else:
                    raise ValueError

            attrs['noise_level'] = ucat.convert_columns(noise_level,
                                                            input_unit, 'kg m-2',
                                                            molar_mass=trace_gas,
                                                            p=np.nanmean(data['psurf'])),
            
        data[name].attrs.update(attrs)
        data[name].attrs['units'] = 'kg m-2'    
            
    return data



def estimate(data, curve, source, trace_gases=('CO2', 'NO2'), method='mass-balance',
             wind_speed=None, wind_direction=None, crs=None):
    """
    Estimate fluxes from satellite image.
    
    trace_gases: 'CO2', 'NO2' or ['CO2', 'NO2']
    
    method {submethod}:
    - mass-balance {one-gauss, two-gauss, sub-areas}
    - 2d-gauss-model
    
    subpolygons
    """
    time = pandas.Timestamp(data['time'].values)
   
    if np.any(np.isnan(data.xp.values[data.detected_plume])):
        return None
        
    if method == 'mass-balance':
        results = ddeq.massbalance.do_mass_balance(data, curve, trace_gases=trace_gases,
                                                   wind_speed=wind_speed,
                                                   wind_direction=wind_direction,
                                                   crs=crs)
        
    else:
        raise NotImplementedError
    
    
    return results
