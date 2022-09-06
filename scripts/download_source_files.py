import json
from itertools import chain

from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL)
from runzi.automation.scaling.file_utils import download_files, get_output_file_ids, get_output_file_id

headers={"x-api-key":API_KEY}
toshi_api = ToshiApi(API_URL, None, None, with_schema_validation=True, headers=headers)

work_path = '/tmp/WORKING/PROD'

with open('/home/chrisdc/NSHM/oqresults/TAG_final/data/realization_data/source_leaves.json','r') as source_file:
    source_leaves = json.load(source_file)

ids = [s[3] for s in source_leaves if s[3]] + [s[4] for s in source_leaves if s[4]]

file_generators = []
for id in ids:
        file_generators.append(get_output_file_id(toshi_api, id))

source_files = download_files(toshi_api, chain(*file_generators), work_path, overwrite=False)

for id, file_info in source_files.items():
    print(id,file_info['filepath'])

