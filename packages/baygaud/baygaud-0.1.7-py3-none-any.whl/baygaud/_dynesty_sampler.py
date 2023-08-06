#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#|-----------------------------------------|
#| _dynesty_sampler.py
#|-----------------------------------------|
#| by Se-Heon Oh
#| Dept. of Physics and Astronomy
#| Sejong University, Seoul, South Korea
#|-----------------------------------------|


#|-----------------------------------------|
import numpy as np
from numpy import sum, exp, log, pi
from numpy import linalg, array, sum, log, exp, pi, std, diag, concatenate

import numba
from numba import jit

#|-----------------------------------------|
import dynesty
from dynesty import NestedSampler
from dynesty import plotting as dyplot
from dynesty import plotting as dyplot
from dynesty import utils as dyfunc

import gc
import ray

#|-----------------------------------------|
# run dynesty for each line profile
@ray.remote(num_cpus=1)
#@ray.remote
def run_dynesty_sampler(_x, _inputDataCube, _is, _ie, i, _js, _je, _max_ngauss):

    gfit_results = np.zeros(((_je-_js), _max_ngauss, 2*(2+3*_max_ngauss)+7), dtype=np.float32)
        
    #for k in range(_max_ngauss-1, _max_ngauss):
    for j in range(0, _je -_js):
        for k in range(0, _max_ngauss):
            ngauss = k+1  # set the number of gaussian
            ndim = 3*ngauss + 2
            nparams = ndim
    
#            if(ndim * (ndim + 1) // 2 > 100):
#                _nlive = 1 + ndim * (ndim + 1) // 2 # optimal minimum nlive
#            else:
#                _nlive = 100
    
            # run dynesty
            print("processing: %d %d gauss-%d" % (i, j+_js, ngauss))
            sampler = NestedSampler(loglike_d, uniform_prior_d, ndim, sample='unif',
                vol_dec = 0.2, vol_check = 2, facc=0.5, rwalk=1000, nlive=100, max_move=100,
                logl_args=[_inputDataCube[:,j+_js,i], _x, ngauss], ptform_args=[ngauss])

            #sampler.reset()
            numba.jit(sampler.run_nested(dlogz=0.5, maxiter=5000, maxcall=50000, print_progress=False), nopython=True, cache=True, nogil=True, parallel=True)
            _gfit_results_temp, _logz = get_dynesty_sampler_results(sampler)
            gfit_results[j][k][:2*nparams] = array(_gfit_results_temp)

            gfit_results[j][k][2*(3*_max_ngauss+2)+0] = _logz
            gfit_results[j][k][2*(3*_max_ngauss+2)+1] = _is
            gfit_results[j][k][2*(3*_max_ngauss+2)+2] = _ie
            gfit_results[j][k][2*(3*_max_ngauss+2)+3] = _js
            gfit_results[j][k][2*(3*_max_ngauss+2)+4] = _je
            gfit_results[j][k][2*(3*_max_ngauss+2)+5] = i
            gfit_results[j][k][2*(3*_max_ngauss+2)+6] = _js + j
    
    del(ndim, nparams, ngauss, sampler)
    gc.collect()
    return gfit_results

    # Plot a summary of the run.
#    rfig, raxes = dyplot.runplot(sampler.results)
#    rfig.savefig("r.pdf")
    
    # Plot traces and 1-D marginalized posteriors.
#    tfig, taxes = dyplot.traceplot(sampler.results)
#    tfig.savefig("t.pdf")
    
    # Plot the 2-D marginalized posteriors.
    #cfig, caxes = dyplot.cornerplot(sampler.results)
    #cfig.savefig("c.pdf")



#|-----------------------------------------|
def get_dynesty_sampler_results(_sampler):
    # Extract sampling results.
    samples = _sampler.results.samples  # samples
    weights = exp(_sampler.results.logwt - _sampler.results.logz[-1])  # normalized weights
    
    # Compute 10%-90% quantiles.
    quantiles = [dyfunc.quantile(samps, [0.1, 0.9], weights=weights)
                for samps in samples.T]
    
    # Compute weighted mean and covariance.
    mean, cov = dyfunc.mean_and_cov(samples, weights)

    # Resample weighted samples.
    #samples_equal = dyfunc.resample_equal(samples, weights)
    
    # Generate a new set of results with statistical+sampling uncertainties.
    #results_sim = dyfunc.simulate_run(_sampler.results)

    #mean_std = np.concatenate((mean, diag(cov)**0.5))
    #return mean_std # meand + std of each parameter: std array is followed by the mean array
    del(samples, weights, quantiles)
    gc.collect()

    return concatenate((mean, diag(cov)**0.5)), _sampler.results.logz[-1]



#|-----------------------------------------|
def multi_gaussian_model_d(_x, _params, ngauss): # params: cube
    #_bg0 : _params[1]
    g = ((_params[3*i+4] * exp( -((_x - _params[3*i+2]) / _params[3*i+3])**2)) for i in range(0, ngauss))
    return sum(g, axis=0) + _params[1]


#|-----------------------------------------|
def multi_gaussian_model_d_new(_x, _params, ngauss): # _x: global array, params: cube

    _gparam = _params[2:].reshape(ngauss, 3).T
    #_bg0 : _params[1]
    return (_gparam[2].reshape(ngauss, 1)*exp(-((_x-_gparam[0].reshape(ngauss, 1)) / _gparam[1].reshape(ngauss, 1))**2)).sum(axis=0) + _params[1]


#|-----------------------------------------|
def multi_gaussian_model_d_classic(_x, _params, ngauss): # params: cube
    _bg0 = _params[1]
    _y = np.zeros_like(_x, dtype=np.float32)
    for i in range(0, ngauss):
        _x0 = _params[3*i+2]
        _std0 = _params[3*i+3]
        _p0 = _params[3*i+4]

        _y += _p0 * exp( -((_x - _x0) / _std0)**2)
        #y += _p0 * (scipy.stats.norm.pdf(_x, loc=_x0, scale=_std0))
    _y += _bg0
    return _y



#|-----------------------------------------|
# parameters are sigma, bg, _x01, _std01, _p01, _x02, _std02, _p02...
def uniform_prior_d(*args):

    # args[0] : sigma
    # args[1] : bg0
    # args[2] : x0
    # args[3] : std0
    # args[4] : p0


    # sigma
    _sigma0 = 0
    _sigma1 = 0.03 
    # bg
    _bg0 = -0.02
    _bg1 = 0.02
    # _x0
    _x0 = 0
    _x1 = 0.8
    # _std0
    _std0 = 0.0
    _std1 = 0.5
    # _p0
    _p0 = 0.0
    _p1 = 0.5

    # partial[2:] copy cube to params_t --> x, std, p ....
    params_t = args[0][2:].reshape(args[1], 3).T

    # vectorization
    # x
    params_t[0] = _x0 + params_t[0]*(_x1 - _x0)
    # sigma
    params_t[1] = _std0 + params_t[1]*(_std1 - _std0)
    # p
    params_t[2] = _p0 + params_t[2]*(_p1 - _p0)

    # sigma and bg
    args[0][0] = _sigma0 + args[0][0]*(_sigma1 - _sigma0)            # bg: uniform prior between 0:1
    args[0][1] = _bg0 + args[0][1]*(_bg1 - _bg0)            # bg: uniform prior between 0:1

    params_t_conc = np.concatenate((params_t[0], params_t[1], params_t[2]), axis=0)
    args[0][2:] = params_t_conc

    #del(_bg0, _bg1, _x0, _x1, _std0, _std1, _p0, _p1, _sigma0, _sigma1, params_t, params_t_conc)
    return args[0]



#|-----------------------------------------|
def loglike_d(*args):
    # args[0] : params
    # args[1] : _spect : input velocity profile array [N channels]
    # args[2] : _x
    # args[3] : ngauss
    # _bg, _x0, _std, _p0, .... = params[1], params[2], params[3], params[4]
    # sigma = params[0] # loglikelihoood sigma

    npoints = args[2].size
    sigma = args[0][0] # loglikelihoood sigma

    gfit = multi_gaussian_model_d(args[2], args[0], args[3])
    log_n_sigma = -0.5*npoints*log(2.0*pi) - 1.0*npoints*log(sigma)
    chi2 = sum((-1.0 / (2*sigma**2)) * ((gfit - args[1])**2))

    return log_n_sigma + chi2



