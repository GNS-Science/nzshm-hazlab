import math
import geopandas
import shapely
from zipfile import ZipFile
import numpy as np
import pandas as pd
from nzshm_hazlab.base_functions import *


def plot_map(ax, imt, rp, inv_time, results, intensity_type='acc'):

    sites = pd.DataFrame(results['metadata']['sites'])
    imtls = results['metadata'][f'{intensity_type}_imtls']
    quantiles = results['metadata']['quantiles']
    
    hazard_rps = np.array(results['hazard_design']['hazard_rps'])
    im_hazard = np.array(results['hazard_design'][intensity_type]['im_hazard'])
    stats_im_hazard = np.array(results['hazard_design'][intensity_type]['stats_im_hazard'])
    
    site_idx = sites.loc[site,'sids']
    rp_idx = np.where(hazard_rps==rp)[0]

    poe = 1-np.exp(-inv_time/rp)

    periods = [period_from_imt(imt) for imt in imtls.keys()]

    coast_file_path = '/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp'
    inversion_solution_file = '/home/chrisdc/NSHM/DEV/nzshm_hazlab/examples/NZSHM22_InversionSolution-QXV0b21hdGlvblRhc2s6MTAxNjU5.zip'

    nz = geopandas.read_file(coast_file_path)

    with ZipFile(inversion_solution_file, 'r') as zip:
        fault_sections_file = zip.open('ruptures/fault_sections.geojson')
        fault_sections = geopandas.read_file(fault_sections_file)

    nz.boundary.plot(ax=ax)
    fault_sections.plot(ax=ax,facecolor="none",edgecolor='black',linewidth=0.3)

    _ = ax.plot(periods,np.squeeze(stats_im_hazard[site_idx,:,rp_idx,0]),color='k',lw=lw,ls=ls)

