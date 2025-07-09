from pathlib import Path
import pytest

import numpy as np
from toshi_hazard_store.model import ProbabilityEnum

from nzshm_hazlab.data import HazardGrids


class DummyGridLoader:
    """A dummy grid loader class."""

    def __init__(self, directory: Path | str):
        self._directory = Path(directory)

    def get_grid(self, hazard_model_id, imt, grid_name, vs30, poe, agg: str):
        """A method for the dummy loader."""
        filename = f"hazard_grid-{hazard_model_id}-{imt}-{grid_name}-{vs30}-{poe.name}-{agg}.npy"
        filepath = self._directory / filename
        return np.load(filepath)

# scope is function because we attach a mocker.spy to the object which only seems to work for function scope
@pytest.fixture(scope='function')
def hazard_grids() -> HazardGrids:
    loader = DummyGridLoader(Path(__file__).parent.parent / "fixtures/data/grids/")
    return HazardGrids(loader=loader)



def test_get_grid(hazard_grids):
    hazard_model_id = "NSHM_v1.0.4"
    grid_name = "NZ_0_1_NB_1_1"
    poe = ProbabilityEnum._2_PCT_IN_50YRS
    agg = "mean"
    imt = "SA(1.0)"
    vs30 = 750


    imtls = hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
    assert imtls.shape == (3741,)


def test_get_grid_cache(mocker, hazard_grids):
    """Subsequent calls to get_grid should not call _load_data if the data have already been loaded."""
    hazard_model_id = "NSHM_v1.0.4"
    grid_name = "NZ_0_1_NB_1_1"
    poe = ProbabilityEnum._2_PCT_IN_50YRS
    agg = "mean"
    imt = "SA(1.0)"
    vs30 = 750

    spy = mocker.spy(hazard_grids, '_load_data')

    hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
    assert spy.call_count == 1
    hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
    assert spy.call_count == 1

    poe = ProbabilityEnum._10_PCT_IN_50YRS
    imt = "PGA"
    vs30 = 400
    hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
    assert spy.call_count == 2


def test_2_grids(hazard_grids):
    """Test that we can get two different grids and the second doesn't overwrite the first."""
    hazard_model_id = "NSHM_v1.0.4"
    grid_name = "NZ_0_1_NB_1_1"
    agg = "mean"
    imt1 = "SA(1.0)"
    poe1 = ProbabilityEnum._2_PCT_IN_50YRS
    vs301 = 750
    poe2 = ProbabilityEnum._10_PCT_IN_50YRS
    imt2 = "PGA"
    vs302 = 400

    grid1 = hazard_grids.get_grid(hazard_model_id, imt1, grid_name, vs301, poe1, agg)
    grid2 = hazard_grids.get_grid(hazard_model_id, imt2, grid_name, vs302, poe2, agg)
    grid1_repeat = hazard_grids.get_grid(hazard_model_id, imt1, grid_name, vs301, poe1, agg)

    assert all(grid1 == grid1_repeat)
    assert any(grid2 != grid1)
