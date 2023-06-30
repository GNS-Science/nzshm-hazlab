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


def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

location_lookup = {CodedLocation(*lat_lon(lid), 0.001).code: lid for lid in LOCATIONS_BY_ID.keys()}

def get_locations(location_names: List[str]) -> List[str]:
    """Get list of locations.

    Parameters
    ----------
    config : AggregationConfig
        job configuration

    Returns
    -------
    locations : List[(float,float)]
        list of (latitude, longitude)
    """


    locations: List[Tuple[float, float]] = []
    for location_spec in location_names:
        if '~' in location_spec:
            locations.append(location_spec)
        elif '_intersect_' in location_spec:
            spec0, spec1 = location_spec.split('_intersect_')
            loc0 = set(load_grid(spec0))
            loc1 = set(load_grid(spec1))
            loc01 = list(loc0.intersection(loc1))
            loc01.sort()
            locations += [CodedLocation(*loc, 0.001).code for loc in loc01]
        elif '_diff_' in location_spec:
            spec0, spec1 = location_spec.split('_diff_')
            loc0 = set(load_grid(spec0))
            loc1 = set(load_grid(spec1))
            loc01 = list(loc0.difference(loc1))
            loc01.sort()
            locations += [CodedLocation(*loc, 0.001).code for loc in loc01]
        elif location_by_id(location_spec):
            locations.append(
                CodedLocation(*lat_lon(location_spec), 0.001).code
                )
        elif LOCATION_LISTS.get(location_spec):
            location_ids = LOCATION_LISTS[location_spec]["locations"]
            locations += [CodedLocation(*lat_lon(id),0.001).code for id in location_ids]
        else:
            locations += [CodedLocation(*loc, 0.001).code for loc in load_grid(location_spec)]
    return locations


def main(hazard_model_id, vs30s, location_names, imts, poes, upload=False):

    print(S3_REPORT_BUCKET)

    if DISAGG_INFO_FILEPATH.exists():
        with DISAGG_INFO_FILEPATH.open() as ojf:
            disagg_entries_old = json.load(ojf)
    else:
        disagg_entries_old = []
    
    locations = get_locations(location_names)
    
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

    upload = False
    hazard_model_id = 'NSHM_v1.0.4'
    vs30s = [750]
    # locations = ["NZ", "srg_164"]
    locations = ["AKL"]
    imts = ["SA(5.0)", "SA(10.0)"]
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

    
