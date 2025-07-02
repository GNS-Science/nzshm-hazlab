"""This module provides the HazardGrids class.

Classes:
    HazardGrids: a class to retrieve hazard grids. Hazard grids are intensity measure levels (IMTLs) at a particular
        probability of exceedance for every point on a map grid. They are used to produce "hazard maps".
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    import numpy.typing as npt
    from toshi_hazard_store.model import ProbabilityEnum

    from .data_loaders.data_loaders import GridLoader


_columns = ["hazard_model_id", "imt", "grid_name", "vs30", "agg", "poe", "imtls"]


class HazardGrids:
    """A class to retrieve hazard grids.

    Hazard grids are intensity measure levels (IMTLs) at a particular probability of exceedance for every point
    on a map grid. They are used to produce "hazard maps".
    """

    def __init__(self, loader: 'GridLoader'):
        """Initialize a new HazardGrids object.

        Args:
            loader: The data loader to use to retrive hazard grids.
        """
        self._loader = loader
        self._data = pd.DataFrame(columns=_columns)

    def get_grid(
        self, hazard_model_id: str, imt: str, grid_name: str, vs30: int, poe: 'ProbabilityEnum', agg: str
    ) -> 'npt.NDArray':
        """Get a hazard grid.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            grid_name: A grid name from nzshm_common. Use nzshm_common.grids.get_location_grid_names() to find a
                list of valid grid names.
            vs30: The vs30 of the sites.
            poe: Probability of exceedance
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            The intensity measure levels (IMTLs) at the poe of interest over the grid. The array is 1D and its entries
                are in the same order as the locations retrieved from nzshm_common.grids.get_location_grid.
        """

        def filter_data(hmi, imt, grid, vs30, poe, agg):
            return self._data.loc[
                self._data["imt"].eq(imt)
                & self._data["grid_name"].eq(grid)
                & self._data["agg"].eq(agg)
                & self._data["vs30"].eq(vs30)
                & self._data["hazard_model_id"].eq(hmi)
                & self._data["poe"].eq(poe)
            ]

        data = filter_data(hazard_model_id, imt, grid_name, vs30, poe, agg)

        if data.empty:
            self._load_data(hazard_model_id, imt, grid_name, vs30, poe, agg)
            data = filter_data(hazard_model_id, imt, grid_name, vs30, poe, agg)

        return data["imtls"].values[0]

    def _load_data(
        self, hazard_model_id: str, imt: str, grid_name: str, vs30: int, poe: 'ProbabilityEnum', agg: str
    ) -> None:

        imtls = self._loader.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
        df = pd.DataFrame([[hazard_model_id, imt, grid_name, vs30, agg, poe, imtls]], columns=_columns)
        self._data = pd.concat([self._data, df])
