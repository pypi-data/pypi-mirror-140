#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#|-----------------------------------------|
#| baygaud.py
#|-----------------------------------------|
#| by Se-Heon Oh
#| Dept. of Physics and Astronomy
#| Sejong University, Seoul, South Korea
#|-----------------------------------------|


#|-----------------------------------------|
# Python 3 compatability
from __future__ import division, print_function

#|-----------------------------------------|
# system functions
import time, sys, os
from datetime import datetime

#|-----------------------------------------|
# python packages
import numpy as np
from numpy import array
import psutil
from multiprocessing import cpu_count


#|-----------------------------------------|
# import ray
import ray

#|-----------------------------------------|
# load baygaudpy modules
#|-----------------------------------------|
# _params.py
from ._baygaud_params import _params, _x
#|-----------------------------------------|
# _dynesty_sampler.py
from ._dynesty_sampler import run_dynesty_sampler
#|-----------------------------------------|
# _fits_io.py
from ._fits_io import read_datacube
#|-----------------------------------------|
# combine_segs.py
#import combine_segs 



#|-----------------------------------------|
#if __name__ == "__main__":
def run(_is, _ie, _js, _je, max_ngauss):
    # read the input datacube
    start = datetime.now()

#    _is = int(sys.argv[1])
#    _ie = int(sys.argv[2])
#    _js = int(sys.argv[3])
#    _je = int(sys.argv[4])
#    max_ngauss = int(sys.argv[5])

    gfit_results = np.zeros(((_je-_js), max_ngauss, 2*(2+3*max_ngauss)+7), dtype=np.float32)


    #ray.init(num_cpus=3, num_gpus=3)
    #ray.init(num_cpus=1, ignore_reinit_error=True, object_store_memory=2*10**9)
    required_num_cpus = _ie - _is
    num_cpus = psutil.cpu_count(logical=False)
    #ray.init(num_cpus=num_cpus)
    ray.init(num_cpus=50)
    # no ray.put : copy traffic
    #results = [run_dynesty_sampler.remote(_inputDataCube, i, j, max_ngauss) for i in range(500, 502) for j in range(500, 502)]

    #a = ray.get(read_datacube.remote(_params, 500, 500)) # --> _inputDataCube
    #_inputDataCube_id = ray.put(a)

    # load the input datacube
    _inputDataCube = read_datacube(_params, 500, 500) # --> _inputDataCub=

    # ray.put : speed up
    _inputDataCube_id = ray.put(_inputDataCube)
    _x_id = ray.put(_x)
    _is_id = ray.put(_is)
    _ie_id = ray.put(_ie)
    max_ngauss_id = ray.put(max_ngauss)
    #_y_id = ray.put(_y)

    #i_start = 500
    #i_end = 550
    #_js = 500
    #_je = 505
    _segdir_ = '/home/seheon/research/libs/dynesty/output'
    _nparams = 3*max_ngauss + 2

    results_ids = [run_dynesty_sampler.remote(_x_id, _inputDataCube_id, _is_id, _ie_id, i, _js, _je, max_ngauss_id) for i in range(_is, _ie)]

    while len(results_ids):
        time.sleep(0.1)
        done_ids, results_ids = ray.wait(results_ids)
        if done_ids:
            # _xs, _xe, _ys, _ye : variables inside the loop
            _xs = int(ray.get(done_ids)[0][0][max_ngauss-1][2*_nparams+1])
            _xe = int(ray.get(done_ids)[0][0][max_ngauss-1][2*_nparams+2])
            _ys = int(ray.get(done_ids)[0][0][max_ngauss-1][2*_nparams+3])
            _ye = int(ray.get(done_ids)[0][0][max_ngauss-1][2*_nparams+4])
            _curi = int(ray.get(done_ids)[0][0][max_ngauss-1][2*_nparams+5])
            _curj = int(ray.get(done_ids)[0][0][max_ngauss-1][2*_nparams+6])

            print(_xs, _curi, _ys, _curj)
            _segid = _curi-_is+1 # current_i - i_start
            #makedir_for_curprocess('%s/_seg%d/output_xs%dxe%dys%dye%di%d'
            #    % (_segdir_, _segid, xs, _xe, _ys, _ye, _segid))
            #makedir_for_curprocess('%s/_seg%d' % (_segdir_, _segid))
            print(ray.get(done_ids))
            print(array(ray.get(done_ids)).shape)
            # save the fits reults to a binary file
            np.save('%s/G%02d.x%d.ys%dye%d' % (_segdir_, max_ngauss, _curi, _ys, _ye), array(ray.get(done_ids)))

    #results_compile = ray.get(results_ids)
    #print(results_compile)
    ray.shutdown()
    print("duration =", datetime.now() - start)

