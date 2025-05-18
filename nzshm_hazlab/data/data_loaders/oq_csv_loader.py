from pathlib import Path
from typing import cast
import pandas as pd

from nzshm_common import CodedLocation

from nzshm_hazlab.constants import RESOLUTION
import numpy as np


def _get_df(hazard_id: str, imt: str, agg: str, output_dir: Path) -> pd.DataFrame:
    filename_prefix = "hazard" if agg == "mean" else "quantile"
    filepath = Path(output_dir) / f"{filename_prefix}_curve-{agg}-{imt}_{hazard_id}.csv"
    return pd.read_csv(filepath, header=1)

class OQCSVLoader:

    def __init__(self, output_dir: Path | str):
        self._output_dir = Path(output_dir)
        self._levels: np.ndarray | None = None


    def get_probabilities(
        self, hazard_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> np.ndarray:

        def get_location(row):
            return CodedLocation(row['lat'], row['lon'], RESOLUTION)

        df = _get_df(hazard_id, imt, agg, self._output_dir)

        if self._levels is None:
            self._set_levels(df)

        poe_columns = [col_name for col_name in df.columns if 'poe-' in col_name]
        df['location'] = df.apply(lambda row: get_location(row), axis=1)
        loc_entry = df.loc[df['location'].eq(location)]
        if len(loc_entry) == 0:
            raise Exception(f"no records found for location {location} in {self._output_dir}")
        if len(loc_entry) > 1:
            raise Exception(f"more than one entry found for location {location} in {self._output_dir}")

        return loc_entry.iloc[0][poe_columns].to_numpy(dtype='float64')


    def _set_levels(self, df: pd.DataFrame) -> None:
        poe_columns = [col_name for col_name in df.columns if 'poe-' in col_name]
        self._levels = np.array([float(col[4:]) for col in poe_columns])


    def get_levels(
        self, hazard_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> np.ndarray:

        if self._levels is None:
            df = _get_df(hazard_id, imt, agg, self._output_dir)
            self._set_levels(df)
        
        return cast(np.ndarray, self._levels)
