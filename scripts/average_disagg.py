import json
from pathlib import Path
import matplotlib.pyplot as plt
from zipfile import ZipFile
import io
from collections import namedtuple
import csv
import numpy as np

from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL, WORK_PATH)
from runzi.automation.scaling.hazard_output_helper import HazardOutputHelper

import oq_hazard_report.disagg_plotting_functions as dpf
import oq_hazard_report.disagg_data_functions as ddf

MASTER_KEYS = ['Active Shallow Crust', 'Subduction Interface', 'Subduction Intraslab']
MASTER_NAMES = ['ASC','INT','SLAB']


# ███████╗██╗░░░██╗███╗░░██╗░█████╗░████████╗██╗░█████╗░███╗░░██╗░██████╗
# ██╔════╝██║░░░██║████╗░██║██╔══██╗╚══██╔══╝██║██╔══██╗████╗░██║██╔════╝
# █████╗░░██║░░░██║██╔██╗██║██║░░╚═╝░░░██║░░░██║██║░░██║██╔██╗██║╚█████╗░
# ██╔══╝░░██║░░░██║██║╚████║██║░░██╗░░░██║░░░██║██║░░██║██║╚████║░╚═══██╗
# ██║░░░░░╚██████╔╝██║░╚███║╚█████╔╝░░░██║░░░██║╚█████╔╝██║░╚███║██████╔╝
# ╚═╝░░░░░░╚═════╝░╚═╝░░╚══╝░╚════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═════╝░

def plot_magdist2d(Mags, Dists, Avg_md_disagg, nrows, ncols, skip):

    ndisaggs = Avg_md_disagg.shape[0]

    fig, ax = plt.subplots(nrows,ncols)
    fig.set_size_inches(18,10)    
    fig.set_facecolor('white')
    cmap = 'OrRd'
    xlim = (5,9)
    ylim = (0,350)
    for i in range(ndisaggs):

        if i%skip == 0:
            j = int(i/skip)
            pcm = ax[int(j/ncols),j%ncols].pcolormesh(Mags,Dists,Avg_md_disagg[i,...],vmin=0,vmax=0.05,shading='auto',cmap=cmap)
            ax[int(j/ncols),j%ncols].set_title(f'weighted avg of {i+1} closest rlz',fontsize=8,y=1.0,pad=-14)
            ax[int(j/ncols),j%ncols].set_xlim(xlim)
            ax[int(j/ncols),j%ncols].set_ylim(ylim)
            ax[int(j/ncols),j%ncols].tick_params(axis='both', labelsize=8)
            
    return fig, ax


def plot_trt_bars(avg_trt_disagg, nrows, ncols, skip):

    ndisaggs = avg_trt_disagg.shape[0]

    fig, ax = plt.subplots(nrows,ncols)
    fig.set_size_inches(18,10)    
    fig.set_facecolor('white')

    for i in range(ndisaggs):

        if i%skip == 0:
            j = int(i/skip)
            ax[int(j/ncols),j%ncols].bar(MASTER_NAMES,avg_trt_disagg[i,:])
            ax[int(j/ncols),j%ncols].set_title(f'weighted avg of {i+1} closest rlz',fontsize=8,y=1.0,pad=-10)
            ax[int(j/ncols),j%ncols].tick_params(axis='both', labelsize=8)

    return fig, ax

def plot_stacked_bar(data):
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(15,8)    
    fig.set_facecolor('white')
    x = np.array([d['rank'] for d in data])
    sint = np.array([d['trt_data']['Subduction Interface']*d['weight'] for d in data])
    slab = np.array([d['trt_data']['Subduction Intraslab']*d['weight'] for d in data])
    crust = np.array([d['trt_data']['Active Shallow Crust']*d['weight'] for d in data])
    sorter = np.argsort(x)
    x = x[sorter]
    sint = sint[sorter]
    slab = slab[sorter]
    crust = crust[sorter]
    ax.bar(x,crust,label='Active Shallow Crust')
    ax.bar(x,sint, label='Subduction Interface')
    ax.bar(x,slab, label='Subduction Intraslab')
    ax.set_xlabel('distance rank')
    ax.set_ylabel('contribution')
    ax.legend()
    ax.set_title('weighted contribution by TRT')

    return fig, ax

def plot_trt_evolution(avg_trt_disagg, data):
    x = np.array([d['rank'] for d in data])
    sorter = np.argsort(x)
    x = x[sorter]

    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(15,8)    
    fig.set_facecolor('white')
    ax.plot(x,avg_trt_disagg[:,0],lw=3,label='Active Shallow Crust')
    ax.plot(x,avg_trt_disagg[:,1], lw=3,label='Subduction Interface')
    ax.plot(x,avg_trt_disagg[:,2], lw=3,label='Subduction Intraslab')
    ax.set_xlabel('number of realizations in weighted mean')
    ax.set_ylabel('contribution')
    ax.legend(loc='lower left')
    ax.set_title('Deaggregation by TRT')
    ax.grid(color='lightgray')

    return fig, ax

def plot_weights(data):
    # plot the weights as a function of rank
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(8,8)    
    fig.set_facecolor('white')
    x = np.array([d['rank'] for d in data])
    y = np.array([d['weight'] for d in data])
    sorter = np.argsort(x)
    x = x[sorter]
    y = y[sorter]
    ax.stem(x,y,'o')
    ax.set_xlabel('distance rank')
    ax.set_ylabel('branch weight')

    return fig, ax


def calc_running_average(mags, dists, data, rank):
    tmp_m, tmp_d, tmp_r = ddf.meshgrid_disaggs_v2(mags, dists, data[0]['md_data'])
    ndisaggs = len(rank)
    avg_trt_disagg = np.zeros((ndisaggs,3))
    avg_md_disagg = np.zeros((ndisaggs,len(mags)))
    Avg_md_disagg = np.zeros( (ndisaggs,tmp_r.shape[0], tmp_r.shape[1] ) )


    for i in range(ndisaggs):
        if list(data[i]['trt_data'].keys()) != MASTER_KEYS:
            raise Exception(f'keys out of order {i}')

        for j in range(0,i+1):
            avg_trt_disagg[i,:] += ( np.array(list(data[rank.index(j)]['trt_data'].values())) * data[rank.index(j)]['weight'] )
            avg_md_disagg[i,:] += ( data[rank.index(j)]['md_data'] * data[rank.index(j)]['weight'] )
        
        avg_md_disagg[i,...] /= sum(avg_md_disagg[i,...])
        avg_trt_disagg[i,:] /= sum(avg_trt_disagg[i,:])
        
        Mags, Dists, Rates = ddf.meshgrid_disaggs_v2(mags,dists,avg_md_disagg[i,:])
        Avg_md_disagg[i,...] = Rates

    return avg_trt_disagg, Mags, Dists, Avg_md_disagg


def load_data(disaggs, site_name, imt, poe):
    data = []
    rank = []
    for i, disagg in enumerate(disaggs['hazard_solutions']):
        if (disagg['site_name'] == site_name) & (disagg['imt'] == imt) & (disagg['poe'] == poe):
            r = disagg['rank']
            weight = disagg['weight']
            rank.append(r)

            hazard_solution_id = disagg['hazard_solution_id']
            h = HazardOutputHelper(toshi_api)
            hazard_solutions = h.download_csv([hazard_solution_id],WORK_PATH)
            csv_archive = list(hazard_solutions.values())[0]['filepath']

            mags,dists,rates_int,rates_slab,rates_cru = ddf.get_disagg_MDT(csv_archive)
            rates_tot = rates_int + rates_slab + rates_cru
            
            data.append(
                dict(
                    csv = csv_archive,
                    rank = r,
                    weight = weight,
                    trt_data = ddf.get_disagg_trt(csv_archive),
                    md_data = rates_tot
                )
            )
            
            print(f'loaded {i} of {len(disaggs["hazard_solutions"])}')

    return rank, data, mags, dists




# ███╗░░░███╗░█████╗░██╗███╗░░██╗
# ████╗░████║██╔══██╗██║████╗░██║
# ██╔████╔██║███████║██║██╔██╗██║
# ██║╚██╔╝██║██╔══██║██║██║╚████║
# ██║░╚═╝░██║██║░░██║██║██║░╚███║
# ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝╚═╝░░╚══╝


headers={"x-api-key":API_KEY}
toshi_api = ToshiApi(API_URL, None, None, with_schema_validation=True, headers=headers)


site_name = 'Auckland'
poe = 0.02
imt = 'PGA'
save = True

# disagg_result_file = Path('/home/chrisdc/NSHM/Disaggs/disagg_result_R2VuZXJhbFRhc2s6MTEzOTky.json') #10
# disagg_result_file = Path('/home/chrisdc/NSHM/Disaggs/disagg_result_R2VuZXJhbFRhc2s6MTE0MDIz.json') #100
disagg_result_file = Path('/home/chrisdc/NSHM/Disaggs/disagg_result_R2VuZXJhbFRhc2s6MTE0MzI0.json') #250
with open(disagg_result_file,'r') as jsonfile:
    disaggs = json.load(jsonfile)


rank, data, mags, dists = load_data(disaggs, site_name, imt, poe)
avg_trt_disagg, Mags, Dists, Avg_md_disagg = calc_running_average(mags, dists, data, rank)

fig1, ax = plot_weights(data)
fig2, ax = plot_stacked_bar(data)
fig3, ax = plot_trt_evolution(avg_trt_disagg, data)

nrows = 4
ncols = 4
skip = 16
fig4, ax = plot_trt_bars(avg_trt_disagg, nrows, ncols, skip)
fig5, ax = plot_magdist2d(Mags, Dists, Avg_md_disagg, nrows, ncols, skip)

if save:
    filename_template = f'{site_name}_{imt}_{int(poe*100):d}'
    
    fig1.savefig('weights_' + filename_template + '.png')
    plt.close(fig1) 
    fig2.savefig('trtbar_' + filename_template + '.png')
    plt.close(fig2) 
    fig3.savefig('trtevol_' + filename_template + '.png')
    plt.close(fig3) 
    fig4.savefig('2dbar_' + filename_template + '.png')
    plt.close(fig4) 
    fig5.savefig('magdist_' + filename_template + '.png')
    plt.close(fig5) 
else:
    plt.show()        

