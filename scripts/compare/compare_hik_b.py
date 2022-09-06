from compare_hazard import compare_hazard_curves

plot_dir = '/home/chrisdc/NSHM/oqresults/hikb'


id_N18p3 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODMy'
id_N22p8 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODM4'


haz_jobs = {
            'N = 18.3, b = 0.979':{'id':id_N18p3},
            'N = 22.8, b = 1.101': {'id':id_N22p8}
            }


compare_hazard_curves(haz_jobs,plot_dir)
