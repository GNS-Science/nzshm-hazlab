"""This module provides the HazardCurves class.

Classes:
    HazardCurves: a class to retrive hazard curves and calculate derivative products.
"""

from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd

from nzshm_hazlab.base_functions import calculate_hazard_at_poe, period_from_imt

if TYPE_CHECKING:
    import numpy.typing as npt
    from nzshm_common import CodedLocation

    from .data_loaders.data_loaders import HazardLoader

_columns = ["hazard_model_id", "imt", "location", "agg", "vs30", "probability"]


class HazardCurves:
    """A class for retrieving and storing hazard curves and calculating derived products."""

    def __init__(self, loader: "HazardLoader"):
        """Initialize a new HazardCurves object.

        Args:
            loader: The data loader to use to retrive hazard curves.
        """
        self._loader = loader
        self._data = pd.DataFrame(columns=_columns)
        self._levels: None | 'npt.NDArray' = None

    def get_hazard_curve(
        self,
        hazard_model_id: str,
        imt: str,
        location: 'CodedLocation',
        vs30: int,
        agg: str,
    ) -> tuple['npt.NDArray', 'npt.NDArray']:
        """Get a single hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: The vs30 of the site.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            A tuple (imtls, poes) where imtls is the shaking levels and poes is the probability of exceedance values.
        """

        def filter_data(hmi, imt, loc, vs30, agg):
            return self._data.loc[
                self._data["imt"].eq(imt)
                & self._data["location"].eq(loc)
                & self._data["agg"].eq(agg)
                & self._data["vs30"].eq(vs30)
                & self._data["hazard_model_id"].eq(hmi)
            ]

        data = filter_data(hazard_model_id, imt, location, vs30, agg)

        if data.empty:
            self._load_data(hazard_model_id, imt, location, vs30, agg)
            data = filter_data(hazard_model_id, imt, location, vs30, agg)
        return cast(np.ndarray, self._levels), data["probability"].values[0]

    def get_uhs(
        self, hazard_model_id: str, poe: float, imts: list[str], location: 'CodedLocation', vs30: int, agg: str
    ) -> tuple['npt.NDArray', 'npt.NDArray']:
        """Get the uniform hazard spectrum (UHS) for a site.

        The period for peak IMTs (e.g. "PGA", "PGV") is 0.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            poe: The probablity of exceedance at which to calculate the UHS.
            imts: The intesity measure types / periods at which to caluclate the UHS curve (e.g. ["PGA", "SA(1.0)"]).
            location: The site location for the UHS.
            vs30: The vs30 of the site.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            A tuple (periods, imtls) where periods is the shaking periods (from the imts) and imtls
            is the shaking levels.
        """
        periods = [period_from_imt(imt) for imt in imts]  # x
        uhs = []
        for imt in imts:
            imtls, poes = self.get_hazard_curve(hazard_model_id, imt, location, vs30, agg)
            uhs.append(calculate_hazard_at_poe(poe, imtls, poes))

        return np.array(periods), np.array(uhs)

    def _load_data(
        self,
        hazard_model_id: str,
        imt: str,
        location: "CodedLocation",
        vs30: int,
        agg: str,
    ) -> None:
        values = self._loader.get_probabilities(hazard_model_id, imt, location, vs30, agg)
        df = pd.DataFrame([[hazard_model_id, imt, location, agg, vs30, values]], columns=_columns)
        self._data = pd.concat([self._data, df])

        if self._levels is None:
            self._levels = self._loader.get_levels(hazard_model_id, imt, location, vs30, agg)
