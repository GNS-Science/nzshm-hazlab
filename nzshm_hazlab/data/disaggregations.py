from typing import TYPE_CHECKING, Iterable, cast
import numpy as np

import pandas as pd

from nzshm_hazlab.base_functions import prob_to_rate, rate_to_prob

if TYPE_CHECKING:
    import numpy.typing as npt
    from nzshm_common.location import CodedLocation
    from toshi_hazard_store.model import ProbabilityEnum

    from .data_loaders.data_loaders import DisaggLoader

_columns = ["hazard_model_id", "imt", "location", "agg", "vs30", "poe", "probability"]


class Disaggregations:

    def __init__(self, loader: 'DisaggLoader'):
        """Initialize a new HazardCurves object.

        Args:
            loader: The data loader to use to retrive hazard curves.
        """
        self._loader = loader
        self._data = pd.DataFrame(columns=_columns)
        self._bin_centers: None | dict[str, 'npt.NDArray'] = None

    def get_disaggregations(
        self,
        hazard_model_id: str,
        dimensions: Iterable[str],
        imt: str,
        location: 'CodedLocation',
        agg: str,
        vs30: int,
        poe: 'ProbabilityEnum',
    ) -> tuple[dict[str, 'npt.NDArray'], 'npt.NDArray']:

        def filter_data(hmi, imt, loc, agg, vs30, poe):
            return self._data.loc[
                self._data["imt"].eq(imt)
                & self._data["location"].eq(loc)
                & self._data["agg"].eq(agg)
                & self._data["vs30"].eq(vs30)
                & self._data["hazard_model_id"].eq(hmi)
                & self._data["poe"].eq(poe)
            ]

        data = filter_data(hazard_model_id, imt, location, agg, vs30, poe)

        if data.empty:
            self._load_data(hazard_model_id, imt, location, agg, vs30, poe)
            data = filter_data(hazard_model_id, imt, location, agg, vs30, poe)

        if (missing := set(dimensions) - set(self._dimensions)):
            raise KeyError(f"disaggregation dimensions {missing} do not exist")

        probabilities = data["probability"].values[0]
        # sum out the dimensions not requested
        rates = prob_to_rate(probabilities, 1.0)
        dims_remove = set(self._dimensions) - set(dimensions)
        bin_centers = {dim:bins for dim,bins in self._bin_centers.items() if dim in dimensions}
        for dim in dims_remove:
            axis = self._dimensions.index(dim)
            rates = np.sum(rates, axis=axis)
        probabilities = rate_to_prob(rates, 1.0)
        return bin_centers, probabilities

    def _load_data(
        self,
        hazard_model_id: str,
        imt: str,
        location: "CodedLocation",
        agg: str,
        vs30: int,
        poe: 'ProbabilityEnum',
    ) -> None:
        values = self._loader.get_disagg(hazard_model_id, imt, location, agg, vs30, poe)
        df = pd.DataFrame([[hazard_model_id, imt, location, agg, vs30, poe, values]], columns=_columns)
        self._data = pd.concat([self._data, df])

        if self._bin_centers is None:
            self._bin_centers = self._loader.get_bin_centers(hazard_model_id, imt, location, agg, vs30, poe)
            self._dimensions = list(self._bin_centers.keys())
