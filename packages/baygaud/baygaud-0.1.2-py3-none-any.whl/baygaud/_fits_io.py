#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#|-----------------------------------------|
#| _fits_io.py
#|-----------------------------------------|
#| by Se-Heon Oh
#| Dept. of Physics and Astronomy
#| Sejong University, Seoul, South Korea
#|-----------------------------------------|

#|-----------------------------------------|
import numpy as np
import fitsio
import astropy.units as u
from astropy.io import fits
from spectral_cube import SpectralCube

#|-----------------------------------------|
def read_datacube(_params, _i, _j):
    global _inputDataCube

    with fits.open(_params['cube'], 'update') as hdu:
        hdu = hdu[0]
        try:
            hdu.header['RESTFREQ'] = hdu.header['FREQ0'] # THIS IS NEEDED WHEN INPUTING FITS PROCESSED WITH GIPSY
        except:
            pass

        try:
            if(hdu.header['CUNIT3']=='M/S' or hdu.header['CUNIT3']=='m/S'):
                hdu.header['CUNIT3'] = 'm/s'
        except KeyError:
            hdu.header['CUNIT3'] = 'm/s'
        
    cube = SpectralCube.read(_params['cube']).with_spectral_unit(u.km/u.s)

    _inputDataCube = fitsio.read(_params['cube'], dtype=np.float32)
    #_spect = _inputDataCube[:,516,488]
    return _inputDataCube

    #plot profile
    #plt.figure(figsize=(12, 5))
    #plt.plot(_x, _spect, color='black', marker='x', 
    #        ls='none', alpha=0.9, markersize=10)
    #plt.plot(_x, _spect, marker='o', color='red', ls='none', alpha=0.7)
    #plt.xlabel('X')
    #plt.ylabel('Y')
    #plt.tight_layout()
    #plt.show()



#|-----------------------------------------|
def write_fits_seg(_segarray, _segfitsfile):
    hdu = fits.PrimaryHDU(data=_segarray)
    hdu.writeto(_segfitsfile, overwrite=True)


