from compare_hazard import compare_hazard_curves

plot_dir = '/home/chrisdc/NSHM/oqresults/hikN'


id_N14p3 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODE2'
id_N18p3 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODMy'
id_N22p3 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODM0'
id_N17p8 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODM3'
id_N22p8 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODM4'
id_N27p8 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODM5'


haz_jobs = {
            'N = 14.3, b = 0.979':{'id':id_N14p3},
            'N = 18.3, b = 0.979':{'id':id_N18p3},
            'N = 22.3, b = 0.979': {'id':id_N22p3},
            'N = 17.8, b = 1.101': {'id':id_N17p8},
            'N = 22.8, b = 1.101': {'id':id_N22p8},
            'N = 27.8, b = 1.101': {'id':id_N27p8}
            }


compare_hazard_curves(haz_jobs,plot_dir)
