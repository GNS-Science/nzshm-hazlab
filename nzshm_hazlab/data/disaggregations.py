"""This module provides the Disaggregations class.

Classes:
    Disaggregations: a class to retrive disaggregation matrices.
"""

from typing import TYPE_CHECKING, Iterable

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
    """A class for retrieving and storing disaggregation matrices."""

    def __init__(self, loader: 'DisaggLoader'):
        """Initialize a new Disaggregations object.

        Args:
            loader: The data loader to use to retrive disaggregations.
        """
        self._loader = loader
        self._data = pd.DataFrame(columns=_columns)
        self._bin_centers: dict[str, 'npt.NDArray'] = {}

    def get_disaggregation(
        self,
        hazard_model_id: str,
        dimensions: Iterable[str],
        imt: str,
        location: 'CodedLocation',
        vs30: int,
        poe: 'ProbabilityEnum',
        agg: str,
    ) -> tuple[dict[str, 'npt.NDArray'], 'npt.NDArray']:
        """Get a disaggregation matrix.

        Available disaggregation dimensions are dictated by what was
        calculated during processing. Possible dimensions are "trt" (tectonic region type),
        "mag" (earthquake magnitude), "dist" (distance to source), "eps" (GMM epsilon).

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            dimensions: The disaggregation dimensions desired, e.g. ["trt", "mag"]
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: The vs30 of the site.
            poe: Probability of exceedance of the disaggregation (point on the hazard curve at which the
                disaggregation was calculated)
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            A tuple of (bin_centers, disaggregation probability matrix). The order of the dimensions in bin_centers
                is the same as the dimensions of the disaggregation probability matrix.
        """

        def filter_data(hmi, imt, loc, vs30, poe, agg):
            return self._data.loc[
                self._data["imt"].eq(imt)
                & self._data["location"].eq(loc)
                & self._data["agg"].eq(agg)
                & self._data["vs30"].eq(vs30)
                & self._data["hazard_model_id"].eq(hmi)
                & self._data["poe"].eq(poe)
            ]

        data = filter_data(hazard_model_id, imt, location, vs30, poe, agg)

        if data.empty:
            self._load_data(hazard_model_id, imt, location, vs30, poe, agg)
            data = filter_data(hazard_model_id, imt, location, vs30, poe, agg)

        if missing := set(dimensions) - set(self._dimensions):
            raise KeyError(f"disaggregation dimensions {missing} do not exist")

        probabilities = data["probability"].values[0]
        # sum out the dimensions not requested
        rates = prob_to_rate(probabilities, 1.0)
        dims_remove = set(self._dimensions) - set(dimensions)
        bin_centers = {dim: bins for dim, bins in self._bin_centers.items() if dim in dimensions}
        axes = tuple(self._dimensions.index(dim) for dim in dims_remove)
        rates = np.sum(rates, axis=axes)
        probabilities = rate_to_prob(rates, 1.0)
        return bin_centers, probabilities

    def _load_data(
        self,
        hazard_model_id: str,
        imt: str,
        location: "CodedLocation",
        vs30: int,
        poe: 'ProbabilityEnum',
        agg: str,
    ) -> None:
        values = self._loader.get_disagg(hazard_model_id, imt, location, vs30, poe, agg)
        df = pd.DataFrame([[hazard_model_id, imt, location, agg, vs30, poe, values]], columns=_columns)
        self._data = pd.concat([self._data, df])

        if not self._bin_centers:
            self._bin_centers = self._loader.get_bin_centers(hazard_model_id, imt, location, vs30, poe, agg)
            self._dimensions: list[str] = list(self._bin_centers.keys())
