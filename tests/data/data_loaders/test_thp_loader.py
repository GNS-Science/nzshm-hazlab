from pathlib import Path

import pytest
from nzshm_common.location import CodedLocation, get_locations
from nzshm_model.logic_tree import GMCMLogicTree, SourceLogicTree

from nzshm_hazlab.data.data_loaders import THPHazardLoader
from tests.helpers import does_not_raise

vs30 = 400

wlg = get_locations(["WLG"])[0]
other_location = CodedLocation(lat=-41.75, lon=171.511, resolution=0.001)


@pytest.fixture(scope='function')
def loader():
    compatible_calc_id = "NZSHM22"
    srm_path = Path(__file__).parent.parent.parent / "fixtures/data/thp_loader/srm_logic_tree.json"
    gmcm_path = Path(__file__).parent.parent.parent / "fixtures/data/thp_loader/gmcm_logic_tree.json"
    srm_logic_tree = SourceLogicTree.from_json(srm_path)
    gmcm_logic_tree = GMCMLogicTree.from_json(gmcm_path)
    return THPHazardLoader(compatible_calc_id, srm_logic_tree, gmcm_logic_tree)


location_imt_agg_err = [
    (wlg, "PGA", "mean", does_not_raise()),
    (wlg, "PGA", "0.666", does_not_raise()),  # can calculate any valid fractile
    (wlg, "PGA", "std", does_not_raise()),
    (wlg, "SA(1.0)", "mean", does_not_raise()),
    (wlg, "SA(7.0)", "mean", pytest.raises(Exception)),
    (other_location, "PGA", "mean", pytest.raises(Exception)),
]


@pytest.mark.parametrize("location,imt,agg,err", location_imt_agg_err)
def test_probabilities(location, imt, agg, err, loader):
    with err:
        probs = loader.get_probabilities("dummy_hazard_model_id", imt, location, vs30, agg)
        assert (probs.size) > 0
