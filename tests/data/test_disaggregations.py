from pathlib import Path

import pytest
from nzshm_common.location import get_locations
from toshi_hazard_store.model import ProbabilityEnum

from nzshm_hazlab.data import Disaggregations
from nzshm_hazlab.data.data_loaders import OQCSVDisaggLoader

testdata = [
    (["trt", "mag", "dist", "eps"], (3, 24, 17, 16)),
    (["mag", "dist", "eps"], (24, 17, 16)),
    (["trt", "dist", "eps"], (3, 17, 16)),
    (["mag", "dist"], (24, 17)),
    (["dist"], (17,)),
]


@pytest.mark.parametrize("dimensions,shape", testdata)
def test_get_disaggregations(dimensions, shape):
    oq_output_dir = Path(__file__).parent.parent / "fixtures/data/csv_loader"
    loader = OQCSVDisaggLoader(oq_output_dir)
    disaggs = Disaggregations(loader=loader)

    hazard_model = "31"
    imt = "PGA"
    location = get_locations(["WLG"])[0]
    agg = "mean"
    vs30 = "400"
    poe = ProbabilityEnum._10_PCT_IN_50YRS
    bin_centers, probabilities = disaggs.get_disaggregation(hazard_model, dimensions, imt, location, vs30, poe, agg)
    assert set(bin_centers.keys()) == set(dimensions)
    assert probabilities.shape == shape


def test_get_disaggs_missing():
    oq_output_dir = Path(__file__).parent.parent / "fixtures/data/csv_loader"
    loader = OQCSVDisaggLoader(oq_output_dir)
    disaggs = Disaggregations(loader=loader)

    hazard_model = "31"
    imt = "PGA"
    location = get_locations(["WLG"])[0]
    agg = "mean"
    vs30 = "400"
    dimensions = ["trt", "mag", "dist", "eps", "foobar"]
    poe = ProbabilityEnum._10_PCT_IN_50YRS
    with pytest.raises(KeyError):
        bin_centers, probabilities = disaggs.get_disaggregation(
            hazard_model, dimensions, imt, location, vs30, poe, agg
        )
