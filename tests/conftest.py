from pathlib import Path

import numpy as np
import pytest

from nzshm_hazlab.data import HazardGrids


class DummyGridLoader:
    """A dummy grid loader class."""

    def __init__(self, directory: Path | str):
        """Initialize a dummy grid loader."""
        self._directory = Path(directory)

    def get_grid(self, hazard_model_id, imt, grid_name, vs30, poe, agg):
        """A method for the dummy grid loader."""
        filename = f"hazard_grid-{hazard_model_id}-{imt}-{grid_name}-{vs30}-{poe.name}-{agg}.npy"
        filepath = self._directory / filename
        return np.load(filepath)


# scope is function because we attach a mocker.spy to the object which only seems to work for function scope
@pytest.fixture(scope='function')
def hazard_grids() -> HazardGrids:
    loader = DummyGridLoader(Path(__file__).parent / "fixtures/data/grids/")
    return HazardGrids(loader=loader)
