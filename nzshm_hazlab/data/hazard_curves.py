from typing import TYPE_CHECKING, cast
from nzshm_hazlab.base_functions import period_from_imt, compute_hazard_at_poe

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from nzshm_common import CodedLocation

    from .data_loaders.data_loader import DataLoader

_columns = ["hazard_model_id", "imt", "location", "agg", "vs30", "probability"]


class HazardCurves:

    def __init__(self, loader: "DataLoader"):
        self._loader = loader
        self._data = pd.DataFrame(columns=_columns)
        self._levels: None | np.ndarray = None

    def get_hazard_curve(
        self,
        hazard_model_id: str,
        imt: str,
        location: 'CodedLocation',
        agg: str,
        vs30: int,
    ) -> tuple[np.ndarray, np.ndarray]:

        def filter_data(hmi, imt, loc, agg, vs30):
            return self._data.loc[
                self._data["imt"].eq(imt)
                & self._data["location"].eq(loc)
                & self._data["agg"].eq(agg)
                & self._data["vs30"].eq(vs30)
                & self._data["hazard_model_id"].eq(hmi)
            ]

        data = filter_data(hazard_model_id, imt, location, agg, vs30)

        if data.empty:
            self._load_data(hazard_model_id, imt, location, agg, vs30)
            data = filter_data(hazard_model_id, imt, location, agg, vs30)

        return cast(np.ndarray, self._levels), data["probability"].values[0]

    def get_uhs(
        self, hazard_model_id: str, apoe: float, imts: list[str], location: 'CodedLocation', agg: str, vs30: int
    ) -> tuple[np.ndarray, np.ndarray]:

        periods = [period_from_imt(imt) for imt in imts] # x
        uhs = []
        for imt in imts:
            imtls, apoes = self.get_hazard_curve(hazard_model_id, imt, location, agg, vs30)
            uhs.append(compute_hazard_at_poe(apoe, apoes, imtls))

        return np.array(periods), np.array(uhs)


    def _load_data(
        self,
        hazard_model_id: str,
        imt: str,
        location: "CodedLocation",
        agg: str,
        vs30: int,
    ) -> None:
        values = self._loader.get_probabilities(hazard_model_id, imt, location, agg, vs30)
        df = pd.DataFrame([[hazard_model_id, imt, location, agg, vs30, values]], columns=_columns)
        self._data = pd.concat([self._data, df])

        if self._levels is None:
            self._levels = self._loader.get_levels(hazard_model_id, imt, location, agg, vs30)
