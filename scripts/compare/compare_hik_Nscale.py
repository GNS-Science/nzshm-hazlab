from compare_hazard import compare_hazard_curves

plot_dir = '/home/chrisdc/NSHM/oqresults/hikNscaling'



id_N14p3 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODE2'
id_N18p3 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODMy'
id_N22p3 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODM0'

haz_jobs = {
            'N = 14.3, b = 0.979':{'id':id_N14p3},
            'N = 18.3, b = 0.979':{'id':id_N18p3},
            'N = 22.3, b = 0.979': {'id':id_N22p3},
            }




compare_hazard_curves(haz_jobs,plot_dir)
