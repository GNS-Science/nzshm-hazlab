import importlib.resources as resources
import json
from pathlib import Path

import numpy as np
import pytest
from nzshm_common import CodedLocation
from nzshm_common.location import get_locations

from nzshm_hazlab.data.data_loaders import THSHazardLoader
from tests.helpers import does_not_raise

hazard_model_oqcsv = "TEST_RUNZI"
vs30 = 400

wlg = get_locations(["WLG"])[0]
other_location = CodedLocation(lat=-41.75, lon=171.58, resolution=0.001)


@pytest.fixture(scope='function')
def loader():
    return THSHazardLoader()


location_imt_agg_err = [
    (wlg, "PGA", "0.01", does_not_raise()),
    (wlg, "PGA", "mean", does_not_raise()),
    (wlg, "SA(1.5)", "mean", does_not_raise()),
    (wlg, "SA(7.0)", "mean", pytest.raises(KeyError)),
    (other_location, "PGA", "mean", pytest.raises(KeyError)),
]


@pytest.mark.parametrize("location,imt,agg,err", location_imt_agg_err)
def test_probabilities(location, imt, agg, err, loader):
    with err:
        probabilities = loader.get_probabilities(hazard_model_oqcsv, imt, location, vs30, agg)
        dir = Path(__file__).parent.parent.parent / "fixtures/data/ths_loader/expected"
        filepath = dir / f"{location.lat}_{location.lon}_{imt}_{agg}.json"
        expected = json.load(filepath.open())
        np.testing.assert_allclose(probabilities, expected)


def test_levels(loader):
    ref = resources.files('tests.fixtures.data.ths_loader.expected') / 'levels.json'
    expected = json.load(ref.open())
    agg = "mean"
    imt = "PGA"
    levels = loader.get_levels(hazard_model_oqcsv, imt, wlg, vs30, agg)
    np.testing.assert_allclose(levels, expected)
