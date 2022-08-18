import oq_hazard_report.plotting_functions
import matplotlib.pyplot as plt

vs30 = 250
site_list = ['WLG']
imt = 'PGA'
# xlim = [0,5]
xlim = [1e-2,1e1]
ylim = [1e-6,1]

TOSHI_ID = "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzOTc4"

fig,ax = plt.subplots(1,1)

oq_hazard_report.plotting_functions.plot_hazard_curve(TOSHI_ID,ax,site_list,imt,xlim,ylim,
                                                        legend_type='quant',show_rlz=False,mean=True,median=True,quant=True,xscale='log')

plt.savefig('hcurve.png')
plt.close(fig)
