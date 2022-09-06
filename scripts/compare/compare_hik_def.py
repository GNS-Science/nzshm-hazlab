from compare_hazard import compare_hazard_curves

plot_dir = '/home/chrisdc/NSHM/oqresults/hik_def'


id_locked = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODU2'
id_creeping = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODU3'


haz_jobs = {
            'Locked':{'id':id_locked},
            'Creeping': {'id':id_creeping}
            }


compare_hazard_curves(haz_jobs,plot_dir)
