from pathlib import Path

import oq_hazard_report.read_oq_hazstore
import oq_hazard_report.plotting_functions

import matplotlib.pyplot as plt


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



plot_dir = Path('/home/chrisdc/NSHM/oqresults/crustalC')
if not plot_dir.exists():
    plot_dir.mkdir()

scales = {'linear':xlim,'log':xlim_log}


id_C4p1 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzOTU3'
id_C4p2 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0Mjk0'
id_C4p3 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzOTc4'


haz_jobs = {
            'C = 4.1':{'id':id_C4p1},
            'C = 4.2':{'id':id_C4p2},
            'C = 4.3':{'id':id_C4p3}
            }

#----------------------------------------------------------------------
for label in haz_jobs.keys():
    print(haz_jobs[label]['id'])
    haz_jobs[label]['data'] = oq_hazard_report.read_oq_hazstore.retrieve_data(haz_jobs[label]['id'],load_rlz=False)

#------------------------------------------------------------------------------------------
for site in sites:
    for imt in imts:
        for scale,xlim in scales.items():
            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            plot_path = Path(plot_dir,f'{site}_{imt}_{scale}.png')

            for i, (label,d) in enumerate(haz_jobs.items()):

                id = d['id']
                data = d['data']
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



