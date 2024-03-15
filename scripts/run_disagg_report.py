import argparse
import itertools
import json
from pathlib import Path, PurePath
import os
import boto3
from typing import List, Tuple
import urllib.request
import datetime as dt
from botocore.errorfactory import ClientError
import mimetypes 
from multiprocessing.pool import ThreadPool



from nzshm_common.grids.region_grid import load_grid
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.location.location import LOCATION_LISTS, location_by_id, LOCATIONS_BY_ID
from nzshm_hazlab.hazard_report.disagg_report_builder import DisaggReportBuilder
# from runzi.util.aws.s3_folder_upload import upload_to_bucket
from toshi_hazard_store import model, query


from nzshm_hazlab.locations import get_locations, lat_lon

WORK_PATH = Path("/tmp/WORKING/PROD")
INDEX_KEY = 'DISAGGS/disaggs.json'
INDEX_LOCALPATH = WORK_PATH / 'disaggs.json'
INDEX_PROFILE = 'chrisdc'

ROOT_PATH = 'openquake/DATA'
hazard_agg = model.AggregationEnum.MEAN

S3_REPORT_BUCKET = os.getenv('NZSHM22_S3_REPORT_BUCKET', "None")
S3_INDEX_BUCKET = os.getenv("NZSHM22_S3_KORORAA_API_BUCKET", "None")
S3_UPLOAD_WORKERS = 50


def mimetype(local_path):
    mimetypes.add_type('text/markdown', '.md')
    mimetypes.add_type('application/json', '.geojson')
    mimetype, _ = mimetypes.guess_type(local_path)
    if mimetype is None:
        raise Exception("Failed to guess mimetype")
    return mimetype


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

def get_disagg_index():
    # make backup copy
    print(f'getting disagg index from S3 {S3_INDEX_BUCKET} / {INDEX_KEY}')

    backup_path = WORK_PATH / 'disaggs.json.bkup'
    session = boto3.Session(profile_name=INDEX_PROFILE)
    s3 = session.resource('s3')
    try:
        s3.meta.client.download_file(S3_INDEX_BUCKET, INDEX_KEY, str(INDEX_LOCALPATH))
    except Exception as e:
        raise e

    backup_path.write_bytes(INDEX_LOCALPATH.read_bytes())
    with INDEX_LOCALPATH.open() as index_file:
        return json.load(index_file)


def upload_to_bucket(data_id, bucket, root_path, force_upload=False):
    print(f"Beginning bucket upload... to {bucket}/{root_path}/{data_id}")
    t0 = dt.datetime.utcnow()
    local_directory = WORK_PATH  /  data_id
    session = boto3.session.Session()
    client = session.client('s3')
    file_list = []
    for root, dirs, files in os.walk(local_directory):
        for filename in files:

            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, str(local_directory))
            s3_path = os.path.join(root_path, data_id, relative_path)

            file_list.append((local_path, bucket, s3_path))

    def upload(args):
        """Map function for pool, uploads to S3 Bucket if it doesn't exist already"""
        local_path, bucket, s3_path = args[0], args[1], args[2]

        if not force_upload and path_exists(s3_path, bucket):
            print("Path found on S3! Skipping %s to %s" % (s3_path, bucket))
        else:
            try:
                client.upload_file(local_path, bucket, s3_path,
                    ExtraArgs={
                        'ACL':'public-read',
                        'ContentType': mimetype(local_path)
                        })
                print("Uploading %s..." % s3_path)
            except Exception as e:
                print(f"exception raised uploading {local_path} => {bucket}/{s3_path}")
                raise e
    
    def path_exists(path, bucket_name):
        """Check to see if an object exists on S3"""
        try:
            response = client.list_objects_v2(Bucket=bucket_name, Prefix=path)
            if response:
                if response['KeyCount'] == 0:
                    return False
                else:    
                    for obj in response['Contents']:
                        if path == obj['Key']:
                            return True
        except ClientError as e:
                print(f"exception raised on {bucket_name}/{path}")
                raise e

        
    pool = ThreadPool(processes=S3_UPLOAD_WORKERS)
    pool.map(upload, file_list)

    pool.close()
    pool.join()
    print("Done! uploaded %s in %s secs" % (len(file_list), (dt.datetime.utcnow() - t0).total_seconds()))

def upload_index():
    print(f'uploading disagg index to S3 bucket {S3_INDEX_BUCKET} / {INDEX_KEY}')
    session = boto3.session.Session(profile_name=INDEX_PROFILE)
    client = session.client('s3')
    client.upload_file(str(INDEX_LOCALPATH), S3_INDEX_BUCKET, INDEX_KEY,
        ExtraArgs={
            'ACL':'public-read',
            'ContentType': 'application/json'
            })


def save_index(disaggs):
    print(f'saving indext to local {INDEX_LOCALPATH}')
    with INDEX_LOCALPATH.open(mode='w') as jf: 
        json.dump(disaggs, jf, indent=2)
        
def main(hazard_model_id, vs30s, location_names, imts, poes, upload=False):

    disagg_index = get_disagg_index() if upload else []

    locations = [loc.code for loc in get_locations(location_names)]
    disaggs = []
    for vs30, location, imt, poe in itertools.product(
        vs30s, locations, imts, poes
    ): 
        disagg_entry, report_folder = run_report(hazard_model_id, vs30, location, imt, poe)        
        if disagg_entry not in disagg_index:
            disaggs.append(disagg_entry)
            if upload:
                upload_to_bucket(str(Path(*report_folder.parts[-2:])), S3_REPORT_BUCKET, root_path=ROOT_PATH, force_upload=True)
        else:
            print(f'skipping upload of {location}-{vs30}-{imt}-{poe}')

    # append entries
    if upload:
        disaggs = disagg_index + disaggs
        save_index(disaggs)
        upload_index()


def run_report(hazard_model_id, vs30, location, imt, poe):

    
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

    return disagg_entry, report_folder



if __name__ == "__main__":

    # upload = True
    upload = True
    hazard_model_id = 'NSHM_v1.0.4'
    vs30s = [200]
    locations = ["NZ", "srg_164"]
    imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.5)", "SA(3.0)"]
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

    
