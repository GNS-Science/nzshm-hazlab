from shutil import get_unpack_formats
import numpy as np
import pandas as pd
from pathlib import Path

import oq_hazard_report.read_oq_hazstore
import oq_hazard_report.plotting_functions
from oq_hazard_report.hazard_data import HazardData
from oq_hazard_report.data_functions import compute_hazard_at_poe


import matplotlib.pyplot as plt


def get_sensitivity(haz_datas, imt, metric, poe):
    '''
    hazard_ids = [low_id, mid_id, high_id]
    low_id can be None if there are only two parameter values to compare
    '''
    
    locs = haz_datas[-1].locs

    dhazard = []
    hds = {}
    for haz_data in haz_datas:
        if haz_data:
            print('id = ',haz_data.haz_sol_id)
            locs = locs.intersection(haz_data.locs)

    sensitivity = []
    for loc in locs:

        hazard = []
        for haz_data in haz_datas:
            if not haz_data:
                hazard.append(np.nan)
            else:
                values = haz_data.values(location=loc,imt=imt,realization='mean')
                hazard.append(compute_hazard_at_poe(values.lvls,values.vals,poe,50))
        sensitivity.append([hazard[0] - hazard[1], hazard[2] - hazard[1]])
        # breakpoint()
    
    # breakpoint()
    sensitivity = np.array(sensitivity)
    if not haz_datas[0]:
        sensitivity = np.vstack((sensitivity[:,1], sensitivity[:,1])).T
    
    if metric == 'max':
        dhazard = np.abs(sensitivity[:,0] - sensitivity[:,1])
        sens = sensitivity[np.argmax(dhazard),:]
    elif metric == 'mean':
        sens = np.mean(sensitivity,axis=0)
        # breakpoint()
    else:
        raise Exception(f'metric {metric} not supported')

    return sens

def get_all_uncertainties(categories, imt, metric, poe):
    '''
    categories is a pandas DataFrame
    '''

    cats = categories.copy()
    sensitivity = []
    length = []
    for index, category in cats.iterrows():
        hazard_ids = category['hazard_ids']
        s = get_sensitivity(hazard_ids,imt,metric,poe)
        sensitivity.append(s)
        if s[1] == s[0]:
            length.append(abs(s[1]))
        else:
            length.append(abs(s[1]-s[0]))
    cats['sensitivity'] = sensitivity
    cats['sens_length'] = length
    return cats


def plot_tornado(categories, ax):
   
    
    plt.rc('ytick', labelsize=12)  # fontsize of the tick labels

    # sort
    categories = categories.sort_values('sens_length',ascending=False)
    
    
    # plot
    hi = []
    low = []
    for index, category in categories.iterrows():
        low.append(category['sensitivity'][0])
        hi.append(category['sensitivity'][1])
    names = list(categories['name'])
    y_pos = np.arange(len(names))
    length = list(categories['sens_length'])
    ax.barh(y_pos, hi)
    ax.barh(y_pos, low)

    ax.set_yticks(y_pos, labels=names,fontsize=12)
    ax.invert_yaxis()

    ax.axvline(color='k')

    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.xaxis.set_ticks_position('top')



def compare_hazard_curves(haz_jobs,plot_dir):


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

    imts = ['PGA','SA(0.5)','SA(1.5)','SA(5.0)']



    plot_dir = Path(plot_dir)
    if not plot_dir.exists():
        plot_dir.mkdir()

    scales = {'linear':xlim,'log':xlim_log}



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



