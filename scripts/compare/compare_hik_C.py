from compare_hazard import compare_hazard_curves

plot_dir = '/home/chrisdc/NSHM/oqresults/hikC'



id_C3p9 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODQw'
id_C4p0 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODQ3'
id_C4p1 = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODQ4'

haz_jobs = {
            'C = 3.9':{'id':id_C3p9},
            'C = 4.0':{'id':id_C4p0},
            'C = 4.1':{'id':id_C4p1},
            }




compare_hazard_curves(haz_jobs,plot_dir)
