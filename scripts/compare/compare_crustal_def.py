from compare_hazard import compare_hazard_curves

plot_dir = '/home/chrisdc/NSHM/oqresults/crustal_def'


id_geologic = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODcw'
id_geodetic = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODcx'
id_geodetic_wp = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTA0ODcy'


haz_jobs = {
            'Geologic':{'id':id_geologic},
            'Geodetic NO prior': {'id':id_geodetic},
            'Geodetic WITH prior': {'id':id_geodetic_wp}
            }


compare_hazard_curves(haz_jobs,plot_dir)
