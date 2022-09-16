import json
from pathlib import Path, PurePath
import os

from nzshm_common.location.location import LOCATIONS_BY_ID
from oq_hazard_report.disagg_report_builder import DisaggReportBuilder
from runzi.automation.scaling.local_config import (WORK_PATH, API_KEY, API_URL, S3_URL, S3_REPORT_BUCKET)
from runzi.util.aws.s3_folder_upload import upload_to_bucket

ROOT_PATH = 'openquake/DATA'
MODEL_ID = 'SLT_v8_gmm_v2'


def add_to_list(model_id, report_folder, location_key, vs30, imt, poe):
    return dict(
        hazard_model = model_id,
        location_key = location_key,
        imt = imt,
        vs30=vs30,
        poe = int(poe)/100,
        inv_time = 50,
        report_url = S3_REPORT_BUCKET + '.s3-website-ap-southeast-2.amazonaws.com' + '/' + '/'.join( (ROOT_PATH,model_id,str(report_folder.name)) )
        )


def main(configs):

    print(S3_REPORT_BUCKET)

    disaggs = []
    for config in configs:

        disagg_filepath = config
        model_id = MODEL_ID

        disagg_filepath = Path(disagg_filepath)
        junk, latlon, vs30, imt, poe = disagg_filepath.stem.split('_')
        lat,lon = latlon.split('~')
        location_key = [key for key,loc in LOCATIONS_BY_ID.items() if (loc['latitude'] == float(lat)) & (loc['longitude'] == float(lon))]
        if not location_key:
            site_name = location_key.replace('~',',')
            location_key = latlon.replace('~','')
        else:
            location_key = location_key[0]
            site_name = LOCATIONS_BY_ID[location_key]['name']

        title = f'{site_name}, Vs30={vs30}m/s, {imt}, {poe}% in 50 years'
        imt_tmp = imt.replace('(','').replace(')','').replace('.','')

        report_folder = Path(WORK_PATH, model_id, f'{location_key}-{vs30}-{imt_tmp}-{poe}'.lower())
        report_folder.mkdir(parents=True, exist_ok=True)
        
        
        drb = DisaggReportBuilder(title,disagg_filepath,report_folder)
        drb.run()

        upload_to_bucket(model_id, S3_REPORT_BUCKET,root_path=ROOT_PATH, force_upload=True)
        disaggs.append(add_to_list(model_id, report_folder, location_key, vs30, imt, poe))

    with open('disaggs.json','w') as jf: #TODO: increment file or concat
        json.dump(disaggs,jf,indent=2)




if __name__ == "__main__":

    disaggs = [
        'deagg_-36.870~174.770_400_PGA_10.npy',
        'deagg_-41.300~174.780_400_PGA_2.npy',
        'deagg_-41.300~174.780_400_SA(3.0)_10.npy',
        'deagg_-43.530~172.630_400_PGA_2.npy',    
        'deagg_-45.870~170.500_400_PGA_10.npy',
        'deagg_-36.870~174.770_400_PGA_2.npy',  
        'deagg_-41.300~174.780_400_SA(1.5)_10.npy',
        'deagg_-41.300~174.780_400_SA(3.0)_2.npy',
        'deagg_-43.530~172.630_400_SA(1.5)_2.npy',
        'deagg_-45.870~170.500_400_PGA_2.npy',
        'deagg_-41.300~174.780_400_PGA_10.npy', 
        'deagg_-41.300~174.780_400_SA(1.5)_2.npy',
        'deagg_-43.530~172.630_400_PGA_10.npy',   
        'deagg_-43.530~172.630_400_SA(3.0)_2.npy',
    ]
    
    main(disaggs)

    
