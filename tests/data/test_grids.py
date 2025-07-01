from pathlib import Path

import numpy as np
from toshi_hazard_store.model import ProbabilityEnum

from nzshm_hazlab.data import HazardGrids


class DummyGridLoader:
    """A dummy grid loader class."""

    def get_grid(self, hazard_model_id, imt, grid_name, vs30, poe, agg: str):
        """A method for the dummy loader."""
        filename = f"hazard_grid-{hazard_model_id}-{imt}-{grid_name}-{vs30}-{poe.name}-{agg}.npy"
        filepath = Path(__file__).parent.parent / f"fixtures/data/grids/{filename}"
        return np.load(filepath)


def test_get_grid():
    hazard_model_id = "NSHM_v1.0.4"
    grid_name = "NZ_0_1_NB_1_1"
    poe = ProbabilityEnum._2_PCT_IN_50YRS
    agg = "mean"
    imt = "SA(1.0)"
    vs30 = 750

    loader = DummyGridLoader()
    hazard_grids = HazardGrids(loader=loader)

    imtls = hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
    assert imtls.shape == (3741,)


def test_get_grid_cache(mocker):
    """Subsequent calls to get_grid should not call _load_data if the data have already been loaded."""
    hazard_model_id = "NSHM_v1.0.4"
    grid_name = "NZ_0_1_NB_1_1"
    poe = ProbabilityEnum._2_PCT_IN_50YRS
    agg = "mean"
    imt = "SA(1.0)"
    vs30 = 750

    loader = DummyGridLoader()
    hazard_grids = HazardGrids(loader=loader)
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
