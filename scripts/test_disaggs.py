from pathlib import Path

from nzshm_common.location.location import location_by_id, LOCATION_LISTS
from nzshm_common.location.code_location import CodedLocation
from toshi_hazard_store import model, query
from nzshm_hazlab.hazard_report.disagg_report_builder import DisaggReportBuilder

from runzi.automation.scaling.local_config import (WORK_PATH, API_KEY, API_URL, S3_REPORT_BUCKET)


def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

locations_coded = [CodedLocation(*lat_lon(id), 0.001).code for id in LOCATION_LISTS['SRWG214']['locations']]
locations_name = [location_by_id(id)['name'] for id in LOCATION_LISTS['SRWG214']['locations']]


HAZARD_MODEL_ID = "TEST_AWS"
locaiton_ids = ["srg_29", "srg_135"]
vs30s = [275]
imts = [model.IntensityMeasureTypeEnum.SA_5_0.value]
hazard_aggs = [model.AggregationEnum.MEAN.value]
disagg_aggs = [model.AggregationEnum.MEAN.value]
locs = [CodedLocation(*lat_lon(id), 0.001) for id in locaiton_ids]
probability = model.ProbabilityEnum._2_PCT_IN_50YRS

qlocs = [loc.downsample(0.001).code for loc in locs]

for qloc in qlocs:
    res = query.get_one_disagg_aggregation(
        HAZARD_MODEL_ID,
        model.AggregationEnum.MEAN,
        model.AggregationEnum.MEAN,
        qloc,
        vs30s[0],
        imts[0],
        probability
    )
    print(res)

    report_folder = Path(WORK_PATH, 'reports', HAZARD_MODEL_ID, f'{res.nloc_001}-{res.vs30}-{res.imt}-{res.probability.name}'.lower())
    location_name = locations_name[locations_coded.index(res.nloc_001)]
    name = f'{location_name}, {res.imt}, {res.vs30}m/s, {res.probability.name}'
    drb = DisaggReportBuilder(name, res.shaking_level, res.disaggs, res.bins, report_folder)
    drb.run()
