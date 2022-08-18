from pathlib import Path

import runzi.automation.scaling.hazard_output_helper
from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL, WORK_PATH)

import oq_hazard_report.report_builder
import oq_hazard_report.plotting_functions
import matplotlib.pyplot as plt

from pathlib import Path

#----------------------------------------------------------------------
PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
xlim = [0,5]
xlim_log = [1e-2,1e1]
ylim = [1e-6,1]
POES = [0.1,0.02]
RPS = [25,50]
INVESTIGATION_TIME = 50
ref_lines = []
for poe in POES:
    ref_line = dict(type = 'poe',
                    poe = poe,
                    inv_time = INVESTIGATION_TIME)
    ref_lines.append(ref_line)
for rp in RPS:
    ref_line = dict(type='rp',
                    rp=rp,
                    inv_time=INVESTIGATION_TIME)
    ref_lines.append(ref_line)
#----------------------------------------------------------------------



#----------------------------------------------------------------------
imts = ['PGA','SA(0.5)','SA(1.5)','SA(5.0)']
sites = ['Wellington','Auckland','Christchurch','Blenheim','Franz Josef','Queenstown','Greymouth','Gisborne','Taupo','Whakatane','Tauranga']
plot_dir = Path('/home/chrisdc/NSHM/oqresults/jump_distance_v2')
if not plot_dir.exists():
    plot_dir.mkdir()

scales = {'linear':xlim,'log':xlim_log}


id_1km = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTQ5'
id_3km = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTY3'
id_5km = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTg1'
id_10km = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDAz'
id_15km = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDIx'
haz_jobs = {'3km':{'id':id_3km},
            '5km':{'id':id_5km},
            '10km':{'id':id_10km},
            '15km':{'id':id_15km}}

#----------------------------------------------------------------------
for label in haz_jobs.keys():
    haz_jobs[label]['rb'] = oq_hazard_report.report_builder.ReportBuilder()
    haz_jobs[label]['rb'].setHazardStore(haz_jobs[label]['id'])
    haz_jobs[label]['rb'].load_data()

#------------------------------------------------------------------------------------------
for site in sites:
    for imt in imts:
        for scale,xlim in scales.items():
            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            plot_path = Path(plot_dir,f'{site}_{imt}_{scale}.png')

            for i, (label,d) in enumerate(haz_jobs.items()):

                id = d['id']
                data = d['rb'].data
                color = f'C{i}'
                print(id)               
                oq_hazard_report.plotting_functions.plot_hazard_curve(ax=ax, site_list=[site,], imt=imt,
                                                                        xlim=xlim,ylim=ylim,
                                                                        results=data,
                                                                        legend_type='site', color=color,
                                                                        xscale=scale,
                                                                        show_rlz=False, ref_lines=ref_lines,
                                                                        custom_label=label)

            _ = ax.set_title(f'{site} {imt}')
            plt.savefig(str(plot_path), bbox_inches="tight")
            plt.close(fig)



