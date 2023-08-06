#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#|-----------------------------------------|
#| _baygaud_params.py
#|-----------------------------------------|
#| by Se-Heon Oh
#| Dept. of Physics and Astronomy
#| Sejong University, Seoul, South Korea
#|-----------------------------------------|

import sys
import numpy as np

#|-----------------------------------------|
# global parameters
global _inputDataCube
global _is, _ie, _js, _je
global parameters
global nparams
global ngauss
global ndim
global max_ngauss
global gfit_results
global _x

_x = np.linspace(0, 1, 143, dtype=np.float32)

#_is = int(sys.argv[1])
#_ie = int(sys.argv[2])
#_js = int(sys.argv[3])
#_je = int(sys.argv[4])
#max_ngauss = int(sys.argv[5])

#gfit_results = np.zeros(((_je-_js), max_ngauss, 2*(2+3*max_ngauss)+7), dtype=np.float32)


# TO CHANGE DEFAULT VALUES, EDIT DICTIONARY BELOW
#|-----------------------------------------|
_params = {
    'main_baygaud':'/opt/baygaud.v1.3.0/src/bin/baygaud',

    'bayes_factor_limit':10,
    'hanning_window_pre_sgfit':5,
    'hanning_window_ngfit':1,

    'ins':1,
    'const_eff_mode':0,
    'nlive':100,
    'mmodal':0,
    'efr':0.1,
    'tol':0.3,
    'feedback':0,
    'write_multinest_outputfile':1,
    'max_iter':0,

    'acceptance_rate_limit':0.0001,

    'profile_sn_limit':1.0,
    'acceptance_rate_grad_limit':0.001,

    'ncolm_per_core':'',
    'nsegments_nax2':'',
    'ncores_total':'',

    'nax1_s0':'',
    'nax1_e0':'',
    'nax2_s0':'',
    'nax2_e0':'',

    'wdir':'',
    'cube':'NGC4631-LR-cube.fits',
    'cube_name':'NGC4631-LR-cube.fits',
    'ref_vf':'',

    'ifresume':0, # DO NOT CHANGE
    'mode':0,
    'galaxies':1
    }


