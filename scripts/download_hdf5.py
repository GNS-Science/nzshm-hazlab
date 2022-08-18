import sys
import runzi.automation.scaling.hazard_output_helper
from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL, WORK_PATH)

# general_task_id = 'R2VuZXJhbFRhc2s6MTAyMzI3'
general_task_id = sys.argv[1]


headers={"x-api-key":API_KEY}
toshi_api = ToshiApi(API_URL, None, None, with_schema_validation=True, headers=headers)

h = runzi.automation.scaling.hazard_output_helper.HazardOutputHelper(toshi_api)
sub = h.get_hazard_ids_from_gt(general_task_id)
hazard_solutions = h.download_hdf(sub,str(WORK_PATH)) #WORK_PATH is just where you want the downloads to go on your computer