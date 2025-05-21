from pathlib import Path
import json
import numpy as np
import importlib.resources as resources

import pytest
from nzshm_common import CodedLocation
from nzshm_common.location.location import _lat_lon

from tests.helpers import does_not_raise

from nzshm_hazlab.constants import RESOLUTION
from nzshm_hazlab.data.data_loaders import OQCSVLoader
from nzshm_hazlab.data.hazard_curves import HazardCurves

hazard_model_oqcsv = "1"
vs30 = 750
wlg = CodedLocation(*_lat_lon("WLG"), RESOLUTION)
other_location = CodedLocation(lat=-41.75, lon=171.58, resolution=0.001)

@pytest.fixture(scope='function')
def csv_loader():
    oq_output_dir = Path(__file__).parent.parent / "fixtures/csv_loader"
    return OQCSVLoader(oq_output_dir)


def test_no_dir():
    with pytest.raises(FileNotFoundError):
        OQCSVLoader("/not/a/directory")

location_imt_agg_filepath_err = [
    (wlg, "PGA", "0.1", "probs_PGA_0.1.json", does_not_raise()),
    (wlg, "PGA", "mean", "probs_PGA_mean.json", does_not_raise()),
    (wlg, "SA(2.0)", "mean", "probs_2.0_mean.json", does_not_raise()),
    (wlg, "SA(7.0)", "mean", "probs_2.0_mean.json", pytest.raises(KeyError)),
    (other_location, "PGA", "mean", "probs_PGA_0.1.json", pytest.raises(KeyError)),
]
@pytest.mark.parametrize("location,imt,agg,filepath,err",location_imt_agg_filepath_err)
def test_probabilities(location, imt, agg, filepath, err, csv_loader):
    ref = resources.files('tests.data.fixtures.csv_loader.expected') / filepath
    expected = json.load(ref.open())
    with err:
        probabilities = csv_loader.get_probabilities(hazard_model_oqcsv, imt, location, agg, vs30)
        np.testing.assert_allclose(probabilities, expected)

def test_levels(csv_loader):
    ref = resources.files('tests.data.fixtures.csv_loader.expected') / 'levels.json'
    expected = json.load(ref.open())
    agg = "mean"
    imt = "PGA"
    levels = csv_loader.get_levels(hazard_model_oqcsv, imt, wlg, agg, vs30)
    np.testing.assert_allclose(levels, expected)
