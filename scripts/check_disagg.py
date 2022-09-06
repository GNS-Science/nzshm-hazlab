from dis import dis
import json
from pathlib import Path
import matplotlib.pyplot as plt
from zipfile import ZipFile
import io
from collections import namedtuple
import csv

from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL, WORK_PATH)
from runzi.automation.scaling.hazard_output_helper import HazardOutputHelper

def get_disagg_trt(csv_archive):
    hazard = {}
    with ZipFile(csv_archive) as zipf:
        with io.TextIOWrapper(zipf.open('Mag_Dist_TRT-0_1.csv'), encoding="utf-8") as mag_dist_TRT_file:
            disagg_reader = csv.reader(mag_dist_TRT_file)
            junk = next(disagg_reader)
            header = next(disagg_reader)
            DisaggData = namedtuple("DisaggData", header, rename=True)
            for row in disagg_reader:
                disagg_data = DisaggData(*row)
                trt = disagg_data.trt
                prob = disagg_data.rlz0
                if not hazard.get(trt):
                    hazard[trt] = float(prob)
                else:
                    hazard[trt] += float(prob)

    return hazard


headers={"x-api-key":API_KEY}
toshi_api = ToshiApi(API_URL, None, None, with_schema_validation=True, headers=headers)


site_names = ['Kerikeri','Franz Josef','Tauranga','Hamilton','Auckland','Wellington','Christchurch','Dunedin','Queenstown']
poe = 0.1
imt = 'SA(0.5)'
# imt = 'PGA'

disagg_result_file = Path('/home/chrisdc/NSHM/Disaggs/disagg_result.json')
with open(disagg_result_file,'r') as jsonfile:
    disaggs = json.load(jsonfile)

for site_name in site_names:
    for disagg in disaggs['hazard_solutions']:
        if (disagg['site_name'] == site_name) & (disagg['imt'] == imt) & (disagg['poe'] == poe):


            hazard_solution_id = disagg['hazard_solution_id']
            h = HazardOutputHelper(toshi_api)
            hazard_solutions = h.download_csv([hazard_solution_id],WORK_PATH)
            csv_archive = list(hazard_solutions.values())[0]['filepath']
            print(csv_archive)

            hazard = get_disagg_trt(csv_archive)
            print('='*50)
            print(site_name, poe, imt)
            print(disagg['location'])
            print(disagg['level'],disagg['target_level'],disagg['dist'])
            print(hazard)
            haz_sum = 0
            for k,v in hazard.items():
                haz_sum += v
            print(haz_sum)
            print('')

            break


