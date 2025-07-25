import importlib.resources as resources
import json
from pathlib import Path

import numpy as np
import pytest
from nzshm_common import CodedLocation
from nzshm_common.location import get_locations
from toshi_hazard_store.model import ProbabilityEnum

from nzshm_hazlab.data.data_loaders import OQCSVDisaggLoader, OQCSVHazardLoader
from tests.helpers import does_not_raise

hazard_model_oqcsv = "1"
vs30 = 750
wlg = get_locations(["WLG"])[0]
other_location = CodedLocation(lat=-41.75, lon=171.58, resolution=0.001)


@pytest.fixture(scope='function')
def csv_hazard_loader():
    oq_output_dir = Path(__file__).parent.parent.parent / "fixtures/data/csv_loader"
    return OQCSVHazardLoader(oq_output_dir)


@pytest.fixture(scope='function')
def csv_disagg_loader() -> OQCSVDisaggLoader:
    oq_output_dir = Path(__file__).parent.parent.parent / "fixtures/data/csv_loader"
    return OQCSVDisaggLoader(oq_output_dir)


def test_no_dir():
    with pytest.raises(FileNotFoundError):
        OQCSVHazardLoader("/not/a/directory")


location_imt_agg_filepath_err = [
    (wlg, "PGA", "0.1", "probs_PGA_0.1.json", does_not_raise()),
    (wlg, "PGA", "mean", "probs_PGA_mean.json", does_not_raise()),
    (wlg, "SA(2.0)", "mean", "probs_2.0_mean.json", does_not_raise()),
    (wlg, "SA(7.0)", "mean", "probs_2.0_mean.json", pytest.raises(KeyError)),
    (other_location, "PGA", "mean", "probs_PGA_0.1.json", pytest.raises(KeyError)),
]


@pytest.mark.parametrize("location,imt,agg,filepath,err", location_imt_agg_filepath_err)
def test_probabilities(location, imt, agg, filepath, err, csv_hazard_loader):
    ref = resources.files('tests.fixtures.data.csv_loader.expected') / filepath
    expected = json.load(ref.open())
    with err:
        probabilities = csv_hazard_loader.get_probabilities(hazard_model_oqcsv, imt, location, vs30, agg)
        np.testing.assert_allclose(probabilities, expected)


def test_levels(csv_hazard_loader):
    ref = resources.files('tests.fixtures.data.csv_loader.expected') / 'levels.json'
    expected = json.load(ref.open())
    agg = "mean"
    imt = "PGA"
    levels = csv_hazard_loader.get_levels(hazard_model_oqcsv, imt, wlg, vs30, agg)
    np.testing.assert_allclose(levels, expected)


def test_disagg(csv_disagg_loader):
    hazard_model = "31"
    imt = "PGA"
    location = wlg
    agg = "mean"
    vs30 = "400"
    poe = ProbabilityEnum._10_PCT_IN_50YRS
    disagg = csv_disagg_loader.get_disagg(hazard_model, imt, location, vs30, poe, agg)
    assert disagg.shape == (3, 24, 17, 16)


def test_disagg_convert_investigation_time_to_1yr(csv_disagg_loader):
    hazard_model = "32"
    imt = "PGA"
    location = wlg
    agg = "mean"
    vs30 = "400"
    poe = ProbabilityEnum._10_PCT_IN_50YRS
    disagg = csv_disagg_loader.get_disagg(hazard_model, imt, location, vs30, poe, agg)
    assert disagg.shape == (3, 24, 17, 16)


def test_bin_centers(csv_disagg_loader):
    hazard_model = "31"
    imt = "PGA"
    location = wlg
    agg = "mean"
    vs30 = "400"
    dimensions = {'trt': 3, 'mag': 24, 'dist': 17, 'eps': 16}
    poe = ProbabilityEnum._10_PCT_IN_50YRS
    bin_centers = csv_disagg_loader.get_bin_centers(hazard_model, imt, location, vs30, poe, agg)
    assert len(bin_centers) == len(dimensions)
    for dim, length in dimensions.items():
        assert len(bin_centers[dim]) == length


def test_disagg_missing_poe(csv_disagg_loader):
    hazard_model = "31"
    imt = "PGA"
    location = wlg
    agg = "mean"
    vs30 = "400"
    poe = ProbabilityEnum._2_PCT_IN_50YRS
    with pytest.raises(KeyError, match='no records found for'):
        csv_disagg_loader.get_disagg(hazard_model, imt, location, vs30, poe, agg)


@pytest.mark.parametrize("hazard_model,agg", [("31", "0.001"), ("30", "mean")])
def test_disagg_missing(hazard_model, agg, csv_disagg_loader):
    imt = "PGA"
    location = wlg
    vs30 = "400"
    poe = ProbabilityEnum._10_PCT_IN_50YRS
    with pytest.raises(KeyError, match='Disaggregation not found for'):
        csv_disagg_loader.get_disagg(hazard_model, imt, location, vs30, poe, agg)


def test_get_disagg_bin_edges(csv_disagg_loader):
    hazard_model = "31"
    imt = "PGA"
    location = wlg
    agg = "mean"
    vs30 = "400"
    dimensions = {'mag': 24 + 1, 'dist': 17 + 1, 'eps': 16 + 1}
    poe = ProbabilityEnum._10_PCT_IN_50YRS
    bin_edges = csv_disagg_loader.get_bin_edges(hazard_model, imt, location, vs30, poe, agg)
    for dim, length in dimensions.items():
        assert len(bin_edges[dim]) == length
