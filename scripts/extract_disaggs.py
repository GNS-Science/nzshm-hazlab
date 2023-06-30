import h5py
import numpy as np
import pandas as pd
from pathlib import Path

from openquake.commonlib import datastore


def extract_disagg(filename):
    
    dstore = datastore.read(filename)
    oqparam = vars(dstore['oqparam'])
    imtls = oqparam['hazard_imtls']
    inv_time = oqparam['investigation_time']
    # sites = find_site_names(dstore.read_df('sitecol'),dtol=0.001)
    dstore.close()
    
    # if len(sites)==1:
    #     site = sites.index.values[0]
    # else:
    #     raise NameError('hdf5 includes more than one site location.')
        
    if len(imtls)==1:
        imt = list(imtls.keys())[0]
    else:
        raise NameError('hdf5 includes more than one IMT.')
        
    if len(imtls[imt])==1:
        imtl = imtls[imt][0]
    else:
        raise NameError(f'hdf5 includes more than one IMTL for {imt}.')
    
    with h5py.File(filename) as hf:
        poe = np.squeeze(hf['poe4'][:])
        
        full_disagg = np.squeeze(hf['disagg']['Mag_Dist_TRT_Eps'][:])
        full_disagg_contribution = full_disagg / poe
        
        mag_dist_disagg = np.squeeze(hf['disagg']['Mag_Dist'][:])
        mag_dist_disagg_contribution = mag_dist_disagg / poe

        dist_bin_edges = hf['disagg-bins']['Dist'][:]
        mag_bin_edges = hf['disagg-bins']['Mag'][:]
        eps_bin_edges = hf['disagg-bins']['Eps'][:]
        breakpoint()

        trt_bins = [x.decode('UTF-8') for x in hf['disagg-bins']['TRT'][:]]
        dist_bins = (dist_bin_edges[1:]-dist_bin_edges[:-1])/2 + dist_bin_edges[:-1]
        eps_bins = (eps_bin_edges[1:]-eps_bin_edges[:-1])/2 + eps_bin_edges[:-1]
        mag_bins = (mag_bin_edges[1:]-mag_bin_edges[:-1])/2 + mag_bin_edges[:-1] 

    disagg = {}
    # disagg['site'] = site
    disagg['imt'] = imt
    disagg['imtl'] = imtl
    disagg['poe'] = poe
    disagg['inv_time'] = inv_time
    disagg['disagg_matrix'] = full_disagg
    disagg['bins'] = {'mag_bins':mag_bins,
                      'dist_bins':dist_bins,
                      'trt_bins':trt_bins,
                      'eps_bins':eps_bins}
    disagg['bin_edges'] = {'mag_bin_edges':mag_bin_edges,
                           'dist_bin_edges':dist_bin_edges,
                           'eps_bin_edges':eps_bin_edges}
    breakpoint()
    
    return disagg


disagg = extract_disagg('/home/chrisdc/oqdata/calc_79.hdf5')
breakpoint()

