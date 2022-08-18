import oq_hazard_report.map_plotting_functions
import oq_hazard_report.read_oq_hdf5
import oq_hazard_report.prepare_design_intensities
import oq_hazard_report.plotting_functions

import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
from zipfile import ZipFile

PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
xlim = [0,5]
ylim = [1e-6,1]

poe = .02
investigation_time = 50.0

hazard_achive_path = '/home/chrisdc/NSHM/DEV/nzshm_hazlab/data/openquake_hdf5_archive-T3BlbnF1YWtlSGF6YXJkVGFzazoxMDIwMjA=.zip'
with ZipFile(hazard_achive_path,'r') as zip:
            for n in zip.namelist():
                if 'calc' in n:
                    hdf_file = zip.extract(n,path='.')

data = oq_hazard_report.read_oq_hdf5.retrieve_data(hdf_file)

args = dict(ref_lines=[],xlim=xlim,ylim=ylim,quant=True,show_rlz=False,
            legend_type='quant',intensity_type='acc')

fig,ax = plt.subplots(1,1)
site = 'Wellington'
imt = 'PGA'
oq_hazard_report.plotting_functions.plot_hazard_curve(ax=ax, site_list=[site,], imt=imt,results=data, **args)

fig.savefig('hcurve.png')