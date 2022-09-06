from weakref import ref
import runzi.automation.scaling.hazard_output_helper
from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL, WORK_PATH)

import oq_hazard_report.report_builder
import oq_hazard_report.plotting_functions
import matplotlib.pyplot as plt

from pathlib import Path

#============================================================================================================#
general_task_id = 'R2VuZXJhbFRhc2s6MTAyNDE3'
headers={"x-api-key":API_KEY}
toshi_api = ToshiApi(API_URL, None, None, with_schema_validation=True, headers=headers)

h = runzi.automation.scaling.hazard_output_helper.HazardOutputHelper(toshi_api)
sub = h.get_hazard_ids_from_gt(general_task_id)
hazard_solutions = h.download_hdf(sub,str(WORK_PATH))
hdf5_paths = dict([[info['hazard_id'],info['filepath']]  for hd5,info in hazard_solutions.items()])
#============================================================================================================#

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
imts = ['PGA','SA(1.5)']
sites = ['Wellington','Auckland','Blenheim','Franz Josef','Queenstown','Greymouth','Gisborne','Taupo','Whakatane']
plot_dir = '/home/chrisdc/NSHM/oqresults/polygons'
scales = {'linear':xlim,'log':xlim_log}


id_all_nopoly = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyNDMy'
id_all_poly = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyNDUw'
id_cru_nopoly = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyNDY4'
id_cru_poly = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyNDg0'
haz_jobs = {
            # 'all no polygons':id_all_nopoly,
            # 'all with polygons':id_all_poly,
            'crustal only no polygons':id_cru_nopoly,
            'crustal only with polygons':id_cru_poly}

#----------------------------------------------------------------------



#------------------------------------------------------------------------------------------
for site in sites:
    for imt in imts:
        for scale,xlim in scales.items():
            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            plot_path = Path(plot_dir,f'{site}_{imt}_{scale}.png')

            for i, id in enumerate(haz_jobs):

                label = id
                color = f'C{i}'
                rb_1km = oq_hazard_report.report_builder.ReportBuilder()
                rb_1km.setHazardArchive(hdf5_paths[haz_jobs[id]])
                rb_1km.load_data()

                oq_hazard_report.plotting_functions.plot_hazard_curve(ax=ax, site_list=[site,], imt=imt,
                                                                        xlim=xlim,ylim=ylim,
                                                                        results=rb_1km.data,
                                                                        legend_type='site', color=color,
                                                                        xscale=scale,
                                                                        show_rlz=False, ref_lines=ref_lines,
                                                                        custom_label=label)

            _ = ax.set_title(f'{site} {imt}')
            plt.savefig(str(plot_path), bbox_inches="tight")
            plt.close(fig)



