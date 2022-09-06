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
# sites = ['Wellington','Dunedin','Auckland','Christchurch','Blenheim',
#             'Franz Josef','Queenstown','Greymouth','Gisborne','Taupo',
#             'Whakatane','Tauranga','Hamilton','New Plymouth','Otira']
sites = ['Auckland',
        'Blenheim',
        'Christchurch',
        'Dunedin',
        'Gisborne',
        'Greymouth',
        'Hawera',
        'Hamilton',
        'Invercargill',
        'Kaikoura',
        'Kerikeri',
        'Levin',
        'Mount Cook',
        'Masterton',
        'Napier',
        'New Plymouth',
        'Nelson',
        'Palmerston North',
        'Te Anau',
        'Timaru',
        'Tokoroa',
        'Tauranga',
        'Thames',
        'Taupo',
        'Whakatane',
        'Franz Josef',
        'Wellington',
        'Westport',
        'Whanganui',
        'Turangi',
        'Otira',
        'Haast',
        'Hanmer Springs',
        'Queenstown'
        ]


# sites = ['Franz Josef']
plot_dir = Path('/home/chrisdc/NSHM/oqresults/crustalN_scaling')
if not plot_dir.exists():
    plot_dir.mkdir()

scales = {'linear':xlim,'log':xlim_log}


id_N1p99 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjAz'
id_N7p46 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjA3'
id_N3p64 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjEw'
id_N4p64 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjEz'
id_N3p03 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjE2'

id_N3p35 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjE5'
id_N4p87= 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjIy'
id_N2p39= 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjI1'
id_N4p75= 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjI4'

id_N5p85 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjMx'
id_N6p06 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjM2'


haz_jobs = {
            # 'N=1.99, b=0.849':{'id':id_N1p99},
            # 'N=7.46, b=1.06':{'id':id_N7p46},
            'N=3.64, b=0.952':{'id':id_N3p64}, #core
            # 'N=4.64, b=1.06':{'id':id_N4p64}, # core
            # 'N=3.03, b=0.849':{'id':id_N3p03}, # core

            # 'N=3.95, b=0.849':{'id':id_N3p35},
            # 'N=4.87, b=0.849':{'id':id_N4p87},
            'N=2.39, b=0.952':{'id':id_N2p39},
            'N=4.75, b=0.952':{'id':id_N4p75},

            'N=5.85, b=0.952':{'id':id_N5p85},

            # 'N = 6.06, b = 1.06':{'id':id_N6p06}
            }

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
                # color = 'C0'
                print(id)               
                oq_hazard_report.plotting_functions.plot_hazard_curve(ax=ax, site_list=[site,], imt=imt,
                                                                        xlim=xlim,ylim=ylim,
                                                                        results=data,
                                                                        legend_type='site', color=color,
                                                                        xscale=scale,
                                                                        quant=True,
                                                                        mean=False,
                                                                        median=True,
                                                                        show_rlz=False, ref_lines=ref_lines,
                                                                        custom_label=label)

            _ = ax.set_title(f'{site} {imt}')
            plt.savefig(str(plot_path), bbox_inches="tight")
            plt.close(fig)



