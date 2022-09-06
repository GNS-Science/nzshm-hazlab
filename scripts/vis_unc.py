import matplotlib.pyplot as plt
import numpy as np
from oq_hazard_report.hazard_data import HazardData
from oq_hazard_report.plotting_functions import plot_hazard_curve_wunc, plot_spectrum_wunc


def set_plot_formatting():    
    # set up plot formatting
    SMALL_SIZE = 12
    MEDIUM_SIZE = 16
    BIGGER_SIZE = 25

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    # plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    
set_plot_formatting()

xlim = [0,5]
xlim_log = [1e-2,1e1]
ylim = [1e-6,1]
TOSHI_ID = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODcw'
# TOSHI_ID = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzOTc4'
hd = HazardData(TOSHI_ID)

# plt.ioff()

fig, ax = plt.subplots(1,2)
fig.set_size_inches(16,8)
fig.set_facecolor('white')

location = 'WLG'
imt = 'PGA'
inset = {'poe':0.1,'inv_time':50}
plot_hazard_curve_wunc(hd,location,imt,ax[0], xlim_log,ylim,bandw=True,inset=inset)
plot_spectrum_wunc(hd, location, 0.1, 50, ax[1],bandw=True)

xticks = ax[0].get_xticks()
ax[0].set_xticks(xticks,labels=[])
yticks = ax[0].get_yticks()
ax[0].set_yticks(yticks,labels=[])
ax[0].set_xlabel('Shaking Intensity [g]',fontsize=16)
ax[0].set_ylabel('Probability of Exceedance',fontsize=16)
ax[0].set_xlim(xlim_log)


xticks = ax[1].get_xticks()
ax[1].set_xticks(xticks,labels=[])
yticks = ax[1].get_yticks()
ax[1].set_yticks(yticks,labels=[])
ax[1].set_xlabel('Period [s]')
ax[1].set_ylabel('Shaking Intensity [g]')

# plt.ion()


plt.show()

