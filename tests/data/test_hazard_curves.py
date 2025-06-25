from pathlib import Path

import pytest
from nzshm_common import CodedLocation
from nzshm_common.location.location import _lat_lon

from nzshm_hazlab.base_functions import convert_poe
from nzshm_hazlab.constants import RESOLUTION
from nzshm_hazlab.data.data_loaders import OQCSVHazardLoader
from nzshm_hazlab.data.hazard_curves import HazardCurves

vs30 = 750
location_id = "WLG"
location = CodedLocation(*_lat_lon(location_id), RESOLUTION)
hazard_model_oqcsv = "1"


@pytest.fixture(scope='module')
def hazard_curves():
    oq_output_dir = Path(__file__).parent.parent / "fixtures/data/csv_loader"
    csv_loader = OQCSVHazardLoader(oq_output_dir)
    return HazardCurves(loader=csv_loader)


def test_uhs(hazard_curves):

    imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.0)", "SA(2.0)", "SA(3.0)", "SA(5.0)", "SA(10.0)"]
    agg = "mean"
    investigation_time = 50.0
    poe = 0.1
    apoe = convert_poe(poe, investigation_time, 1.0)
    assert hazard_curves.get_uhs(hazard_model_oqcsv, apoe, imts, location, agg, vs30)


@pytest.mark.parametrize("agg", ["mean", "0.1"])
def test_hazard_curve(agg, hazard_curves):
    imt = "PGA"
    assert hazard_curves.get_hazard_curve(hazard_model_oqcsv, imt, location, agg, vs30)
