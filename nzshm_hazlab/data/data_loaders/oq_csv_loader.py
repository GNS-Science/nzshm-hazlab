"""This module provides the OQCSVLoader class."""

from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
from nzshm_common import CodedLocation

from nzshm_hazlab.constants import RESOLUTION


def _get_df(hazard_id: str, imt: str, agg: str, output_dir: Path) -> pd.DataFrame:
    filename_prefix = "hazard" if agg == "mean" else "quantile"
    filepath = Path(output_dir) / f"{filename_prefix}_curve-{agg}-{imt}_{hazard_id}.csv"
    return pd.read_csv(filepath, header=1)


class OQCSVLoader:
    """A class for loading hazard curves from OpenQuake csv output."""

    def __init__(self, output_dir: Path | str):
        """Initializes a new OQCSVLoader object.

        Args:
            output_dir: The path to the folder where the output csv files are stored.
        """
        self._output_dir = Path(output_dir)
        self._levels: np.ndarray | None = None

    def get_probabilities(
        self, hazard_model_id: str | int, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> np.ndarray:
        """Get the probablity values for a hazard curve.

        Note that because the OpenQuake csv file does not store the site conditions, the vs30 argument
        is a dummy value. It is the responsibility of the user to check that the OpenQuake calculation
        was performed with the desired site conditions.

        Args:
            hazard_model_id: The calculation ID of the OpenQuake run.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: Not used.

        Returns:
            The probability values.

        Raises:
            KeyError: If no records or more than one record is found in the database.
        """
        hazard_model_id = str(hazard_model_id)

        def get_location(row):
            return CodedLocation(row['lat'], row['lon'], RESOLUTION)

        df = _get_df(hazard_model_id, imt, agg, self._output_dir)

        if self._levels is None:
            self._set_levels(df)

        poe_columns = [col_name for col_name in df.columns if 'poe-' in col_name]
        df['location'] = df.apply(lambda row: get_location(row), axis=1)
        loc_entry = df.loc[df['location'].eq(location)]
        if len(loc_entry) == 0:
            raise KeyError(f"no records found for location {location} in {self._output_dir}")
        if len(loc_entry) > 1:
            raise KeyError(f"more than one entry found for location {location} in {self._output_dir}")

        return loc_entry.iloc[0][poe_columns].to_numpy(dtype='float64')

    def _set_levels(self, df: pd.DataFrame) -> None:
        poe_columns = [col_name for col_name in df.columns if 'poe-' in col_name]
        self._levels = np.array([float(col[4:]) for col in poe_columns])

    def get_levels(self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int) -> np.ndarray:
        """Get the intensity measure levels for a hazard curve.

        Note that because the OpenQuake csv file does not store the site conditions, the vs30 argument
        is a dummy value. It is the responsibility of the user to check that the OpenQuake calculation
        was performed with the desired site conditions.

        Args:
            hazard_model_id: The calculation ID of the OpenQuake run.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: Not used.

        Returns:
            The intensity measure values.
        """
        hazard_model_id = str(hazard_model_id)

        if self._levels is None:
            df = _get_df(hazard_model_id, imt, agg, self._output_dir)
            self._set_levels(df)

        return cast(np.ndarray, self._levels)
