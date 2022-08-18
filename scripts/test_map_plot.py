import oq_hazard_report.map_plotting_functions
import oq_hazard_report.read_oq_hdf5
import oq_hazard_report.prepare_design_intensities
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
from zipfile import ZipFile

PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625

poe = .02
investigation_time = 50.0

hazard_achive_path = '/home/chrisdc/NSHM/DEV/nzshm_hazlab/data/openquake_hdf5_archive-T3BlbnF1YWtlSGF6YXJkVGFzazoxMDIwMjA=.zip'
with ZipFile(hazard_achive_path,'r') as zip:
            for n in zip.namelist():
                if 'calc' in n:
                    hdf_file = zip.extract(n,path='.')

data = oq_hazard_report.read_oq_hdf5.retrieve_data(hdf_file)
rps = np.array([-investigation_time/math.log(1 - poe),])


intensity_type = 'acc'
im_hazard, stats_im_hazard = oq_hazard_report.prepare_design_intensities.calculate_hazard_design_intensities(data,rps,intensity_type)
#im_hazard [site,imt,rp,realizations,? (always inexed to 0)]
#stats_im_hazard [site,imt,rp,stats (mean, p10,p50,p90)]
data['hazard_design'] = {intensity_type:dict()}
data['hazard_design'][intensity_type]['im_hazard'] = im_hazard
data['hazard_design'][intensity_type]['stats_im_hazard'] = stats_im_hazard
data['hazard_design']['hazard_rps'] = [rp,]

sites = pd.DataFrame(data['metadata']['sites'])
imtls = data['metadata'][f'{intensity_type}_imtls']
quantiles = data['metadata']['quantiles']

hazard_rps = np.array(data['hazard_design']['hazard_rps'])
im_hazard = np.array(data['hazard_design'][intensity_type]['im_hazard'])
stats_im_hazard = np.array(data['hazard_design'][intensity_type]['stats_im_hazard'])

fig, ax = plt.subplots(1,1)
fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
oq_hazard_report.map_plotting_functions.plot_map(ax,'PGA',rp,investigation_time, data, intensity_type)
plt.savefig('map.png', bbox_inches="tight")
plt.close(fig)