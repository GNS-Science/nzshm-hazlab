import argparse
import json
from pathlib import Path, PurePath
import os

from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_hazlab.hazard_report.disagg_report_builder import DisaggReportBuilder
from runzi.automation.scaling.local_config import (WORK_PATH, API_KEY, API_URL, S3_REPORT_BUCKET)
from runzi.util.aws.s3_folder_upload import upload_to_bucket

ROOT_PATH = 'openquake/DATA'
MODEL_ID = 'SLT_v8_gmm_v2_FINAL'
S3_URL = 'nshm-static-reports.gns.cri.nz'
DISAGG_INFO_FILEPATH = Path(os.environ['NZSHM22_DISAGG_REPORT_LIST'])

def list_entry(model_id, report_folder, location_key, vs30, imt, poe):
    return dict(
        hazard_model = model_id,
        location_key = location_key,
        imt = imt,
        vs30=vs30,
        poe = int(poe)/100,
        inv_time = 50,
        report_url = S3_URL + '/' + '/'.join( (ROOT_PATH,model_id,str(report_folder.name)) )
        )


def main(disagg_filepaths, dry_run=False):

    print(S3_REPORT_BUCKET)
    disagg_filepaths = list(disagg_filepaths)
    ndisaggs = len(disagg_filepaths)

    # disagg_info_filepath = Path('/home/chrisdc/NSHM/Disaggs/THP_Output/disaggs.json')

    if DISAGG_INFO_FILEPATH.exists():
        with DISAGG_INFO_FILEPATH.open() as ojf:
            old_disaggs = json.load(ojf)
    else:
        old_disaggs = []
    
    disaggs = []
    for i, disagg_filepath in enumerate(disagg_filepaths):

        print(f'generating report for disagg {i} of {ndisaggs}')
        bin_filepath = Path(disagg_filepath.parent, 'bins' + disagg_filepath.name[5:]) 
        model_id = MODEL_ID

        # disagg_filepath = Path(disagg_filepath)
        j0,j1,j2,j3,j4,j5, latlon, vs30, imt, poe, j6 = disagg_filepath.stem.split('_')
        lat,lon = latlon.split('~')
        location_key = [key for key,loc in LOCATIONS_BY_ID.items() if (loc['latitude'] == float(lat)) & (loc['longitude'] == float(lon))]
        if not location_key:
            site_name = location_key.replace('~',',') #TODO: this won't work
            location_key = latlon.replace('~','')
        else:
            location_key = location_key[0]
            site_name = LOCATIONS_BY_ID[location_key]['name']

        title = f'{site_name}, Vs30={vs30}m/s, {imt}, {poe}% in 50 years'
        imt_tmp = imt.replace('(','').replace(')','').replace('.','')

        report_folder = Path(WORK_PATH, model_id, f'{location_key}-{vs30}-{imt_tmp}-{poe}'.lower())

        disagg = list_entry(model_id, report_folder, location_key, vs30, imt, poe)
        if disagg in old_disaggs:
            print(f'skipping {location_key}-{vs30}-{imt_tmp}-{poe}')
            continue
        
        print(f'generating report for {location_key}-{vs30}-{imt_tmp}-{poe}')

        if not dry_run:
            report_folder.mkdir(parents=True, exist_ok=True)
            drb = DisaggReportBuilder(title, disagg_filepath, bin_filepath, report_folder)
            drb.run()

            upload_to_bucket(model_id, S3_REPORT_BUCKET,root_path=ROOT_PATH, force_upload=True)
            disaggs.append(disagg)

    if not dry_run:
        disaggs = old_disaggs + disaggs

        with DISAGG_INFO_FILEPATH.open(mode='w') as jf: 
            json.dump(disaggs, jf, indent=2)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="run disagg report generation and upload to S3")
    parser.add_argument('-d', '--dry-run', action='store_true') 
    args = parser.parse_args()

    disagg_dir = Path('/home/chrisdc/mnt/glacier/NZSHM-WORKING/PROD/deaggs')
    disaggs = disagg_dir.glob('deagg*npy')
    # disaggs = disagg_dir.glob('deagg_SLT_v8_gmm_v2_FINAL_-43.530~172.630_750_SA(0.5)_2_eps-dist-mag-trt.npy')

    main(disaggs, args.dry_run)

    
