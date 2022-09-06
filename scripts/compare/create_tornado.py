import pandas as pd
import matplotlib.pyplot as plt

import compare_hazard

from oq_hazard_report.hazard_data import HazardData

PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625

names = ['crustal C', 
        'crustal def',
        # 'crustal Nb',
        'Hik Nb',
        'Hik C',
        'Hik def',
        'Hik N scaling',
        ]

hazard_ids = [ [HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzOTU3'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0Mjk0'), HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzOTc4')],
                [HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODcw'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODcy'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODcx')],
                # [HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjE2'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjEw'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMjEz')],
                [None,HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODMy'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODM4')],
                [HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODQw'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODQ3'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODQ4')],
                [None,HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODU2'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODU3')],
                [HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODE2'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODMy'),HazardData('T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODM0')],
            ]
var_values = [ ['4.1','4.3'],
                ['Geologic','Geodetic'],
                # ['N=3.03, b=0.849','N=4.64, b=1.06'],
                ['N=18.3, b=0.979','N=22.8, b=1.101'],
                ['C=3.9', 'C=4.1'],
                ['locked','creeping'],
                ['0.78','1.22'],
            ]

d = {'name':names,'hazard_ids':hazard_ids,'var_values':var_values}
categories = pd.DataFrame(d)
categories_max2 = compare_hazard.get_all_uncertainties(categories,'PGA','max',0.02)
categories_max10 = compare_hazard.get_all_uncertainties(categories,'PGA','max',0.1)
categories_avg2 = compare_hazard.get_all_uncertainties(categories,'PGA','mean',0.02)
categories_avg10 = compare_hazard.get_all_uncertainties(categories,'PGA','mean',0.1)

title_fs = 14
xlabel_fs = 12

fig, ax = plt.subplots(2,2)
fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
compare_hazard.plot_tornado(categories_max2,ax[0,0])
ax[0,0].set_title('2% in 50, PGA max hazard difference (g)',fontsize=title_fs)
ax[0,0].tick_params(axis='x', which='major', labelsize=10)
compare_hazard.plot_tornado(categories_max10,ax[1,0])
ax[1,0].set_title('10% in 50, PGA max hazard difference (g)',fontsize=title_fs)
ax[1,0].tick_params(axis='x', which='major', labelsize=10)
compare_hazard.plot_tornado(categories_avg2,ax[0,1])
ax[0,1].set_title('2% in 50, PGA mean hazard difference (g)',fontsize=title_fs)
ax[0,1].tick_params(axis='x', which='major', labelsize=10)
compare_hazard.plot_tornado(categories_avg10,ax[1,1])
ax[1,1].set_title('10% in 50, PGA mean hazard difference (g)',fontsize=title_fs)
ax[1,1].tick_params(axis='x', which='major', labelsize=10)

fig.show()


