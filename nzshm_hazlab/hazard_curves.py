import pandas as pd
from typing import TYPE_CHECKING
import numpy as np


if TYPE_CHECKING:
    from nzshm_common.location import CodedLocation
    from .data_loaders.data_loader import DataLoader

_columns = ["imt", "location", "aggregate", "vs30", "probability"]

class HazardCurves:

    def __init__(self, loader: 'DataLoader'):
        self._loader = loader
        self._data = pd.DataFrame(columns=_columns)
        self._levels: None | np.ndarray = None

    def get_hcurve(self, imt: str, location: 'CodedLocation', aggregate: str, vs30: int) -> tuple[np.ndarray, np.ndarray]:
        idx = self._data.loc[
            self._data['imt'].eq(imt) \
            & self._data['location'].eq(location) \
            & self._data['aggregate'].eq(aggregate) \
            & self._data['vs30'].eq(vs30)
        ]

        if not idx:
            self._load_data(imt, location, aggregate, vs30)

        return self._levels, self._data[idx]['probability']

    def _load_data(self, imt: str, location: 'CodedLocation', aggregate: str, vs30: int) -> None:
        values = self._loader.get_probabilities(imt, location, aggregate, vs30)
        df = pd.df([[imt, location, aggregate, vs30, values]], columns=_columns)
        self._data = pd.concat([self._data, df])

        if not self._levels:
            self._levels = self._loader.get_levels(imt, location, aggregate, vs30)