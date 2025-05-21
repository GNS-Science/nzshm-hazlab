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

oq_output_dir = Path(__file__).parent.parent / "fixtures/csv_loader"
hazard_model_oqcsv = "1"
csv_loader = OQCSVLoader(oq_output_dir)

vs30 = 750
location_id = "WLG"
location = CodedLocation(*_lat_lon(location_id), RESOLUTION)

def test_no_dir():
    with pytest.raises(FileNotFoundError):
        OQCSVLoader("/not/a/directory")

imt_agg_filepath_err = [
    ("PGA", "0.1", "probs_PGA_0.1.json", does_not_raise()),
    ("PGA", "mean", "probs_PGA_mean.json", does_not_raise()),
    ("SA(2.0)", "mean", "probs_2.0_mean.json", does_not_raise()),
    ("SA(7.0)", "mean", "probs_2.0_mean.json", pytest.raises(KeyError)),
]
@pytest.mark.parametrize("imt,agg,filepath,err",imt_agg_filepath_err)
def test_probabilities(imt, agg, filepath, err):
    ref = resources.files('tests.data.fixtures.csv_loader.expected') / filepath
    expected = json.load(ref.open())
    with err:
        probabilities = csv_loader.get_probabilities(hazard_model_oqcsv, imt, location, agg, vs30)
        np.testing.assert_allclose(probabilities, expected)

def test_levels():
    ref = resources.files('tests.data.fixtures.csv_loader.expected') / 'levels.json'
    expected = json.load(ref.open())
    agg = "mean"
    imt = "PGA"
    levels = csv_loader.get_levels(hazard_model_oqcsv, imt, location, agg, vs30)
    np.testing.assert_allclose(levels, expected)
