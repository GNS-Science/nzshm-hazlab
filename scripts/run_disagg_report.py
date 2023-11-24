import argparse
import itertools
import json
from pathlib import Path, PurePath
import os
from typing import List, Tuple

from nzshm_common.grids.region_grid import load_grid
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.location.location import LOCATION_LISTS, location_by_id, LOCATIONS_BY_ID
from nzshm_hazlab.hazard_report.disagg_report_builder import DisaggReportBuilder
from runzi.automation.scaling.local_config import (WORK_PATH, API_KEY, API_URL, S3_REPORT_BUCKET)
from runzi.util.aws.s3_folder_upload import upload_to_bucket
from toshi_hazard_store import model, query

from nzshm_hazlab.locations import get_locations, lat_lon

ROOT_PATH = 'openquake/DATA'
DISAGG_INFO_FILEPATH = Path(os.environ['NZSHM22_DISAGG_REPORT_LIST'])
hazard_agg = model.AggregationEnum.MEAN

def list_entry(model_id, report_folder, location_key, vs30, imt, poe):
    return dict(
        hazard_model = model_id,
        location_key = location_key,
        imt = imt,
        vs30=vs30,
        poe = int(poe)/100,
        inv_time = 50,
        report_url = S3_REPORT_BUCKET.replace('nzshm22','nshm') +\
            '.gns.cri.nz' + '/' + '/'.join( (ROOT_PATH,model_id,str(report_folder.name)) )
        )


location_lookup = {CodedLocation(*lat_lon(lid), 0.001).code: lid for lid in LOCATIONS_BY_ID.keys()}

def main(hazard_model_id, vs30s, location_names, imts, poes, upload=False):

    print(S3_REPORT_BUCKET)

    if DISAGG_INFO_FILEPATH.exists():
        with DISAGG_INFO_FILEPATH.open() as ojf:
            disagg_entries_old = json.load(ojf)
    else:
        disagg_entries_old = []
    
    locations = [loc.code for loc in get_locations(location_names)]
    
    disaggs = []
    for vs30, location, imt, poe in itertools.product(
        vs30s, locations, imts, poes
    ): 

        poe_string = poe.name.split('_')[1]
        site_id = location_lookup.get(location)
        if site_id:
            site_name = location_by_id(site_id)['name']
        else:
            site_id = location
            site_name = location

        title = f'{site_name}, Vs30={vs30}m/s, {imt}, {poe_string}% in 50 years'
        imt_tmp = imt.replace('(','').replace(')','').replace('.','')

        report_folder = Path(WORK_PATH, hazard_model_id, f'{site_id}-{vs30}-{imt_tmp}-{poe_string}'.lower())

        disagg_entry = list_entry(hazard_model_id, report_folder, site_id, vs30, imt, poe_string)
        if upload and disagg_entry in disagg_entries_old:
            print(f'skipping {site_id}-{vs30}-{imt_tmp}-{poe_string}')
            continue
        
        print(f'generating report for {site_id}-{vs30}-{imt_tmp}-{poe_string}')

        disagg = next(
            query.get_disagg_aggregates(
                [hazard_model_id],
                [hazard_agg],
                [hazard_agg],
                [location],
                [vs30],
                [imt],
                [poe],
            )
        )

        report_folder.mkdir(parents=True, exist_ok=True)
        drb = DisaggReportBuilder(title, disagg.shaking_level, disagg.disaggs, disagg.bins, report_folder)
        drb.run()

        if upload:
            upload_to_bucket(hazard_model_id, S3_REPORT_BUCKET,root_path=ROOT_PATH, force_upload=True)
            disaggs.append(disagg_entry)

    if upload:
        disaggs = disagg_entries_old + disaggs

        with DISAGG_INFO_FILEPATH.open(mode='w') as jf: 
            json.dump(disaggs, jf, indent=2)



if __name__ == "__main__":

    upload = True
    hazard_model_id = 'NSHM_v1.0.4'
    vs30s = [275]
    # locations = ["NZ", "srg_164"]
    # locations = ["-45.400~170.400"]
    locations = ["srg_182", "srg_185"]

    # imts = ['PGA', "SA(0.2)", "SA(0.5)", "SA(1.5)", "SA(3.0)"]
    imts = ["PGA"]
    poes = [
        model.ProbabilityEnum._2_PCT_IN_50YRS,
        model.ProbabilityEnum._5_PCT_IN_50YRS,
        model.ProbabilityEnum._10_PCT_IN_50YRS,
        model.ProbabilityEnum._18_PCT_IN_50YRS,
        model.ProbabilityEnum._39_PCT_IN_50YRS,
        model.ProbabilityEnum._63_PCT_IN_50YRS,
        model.ProbabilityEnum._86_PCT_IN_50YRS,
    ]
    main(hazard_model_id, vs30s, locations, imts, poes, upload)

    
