from pathlib import Path

import pytest
from nzshm_common import CodedLocation
from nzshm_common.location.location import _lat_lon

from nzshm_hazlab.constants import RESOLUTION
from nzshm_hazlab.data.data_loaders import OQCSVLoader
from nzshm_hazlab.data.hazard_curves import HazardCurves

oq_output_dir = Path(__file__).parent / "fixtures"
hazard_model_oqcsv = "1"
csv_loader = OQCSVLoader(oq_output_dir)

hazard_curves_OQ = HazardCurves(loader=csv_loader)

vs30 = 750
location_id = "WLG"
location = CodedLocation(*_lat_lon(location_id), RESOLUTION)

imts = ["PGA", "SA(1.0)"]
aggs = ["0.1", "mean"]


@pytest.mark.parametrize("imt", imts)
@pytest.mark.parametrize("agg", aggs)
def test_csv_loader(imt, agg):
    assert hazard_curves_OQ.get_hcurve(hazard_model_oqcsv, imt, location, agg, vs30)
