"""This module provides the OQCSVHazardLoader class."""

import csv
import json
import math
import re
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd
from nzshm_common import CodedLocation

from nzshm_hazlab.base_functions import convert_poe
from nzshm_hazlab.constants import RESOLUTION

if TYPE_CHECKING:
    import numpy.typing as npt
    from toshi_hazard_store.model import ProbabilityEnum


def _get_disagg_header_data(filepath):
    with filepath.open() as file:
        reader = csv.reader(file)
        header = next(reader)
    data_str = header[-1]
    js = "{" + re.sub(r'(\b\w+=)', r'"\1', data_str).replace("=", '":').replace("'", '"') + "}"
    return json.loads(js)


def _get_hazard_curve_df(hazard_id: str, imt: str, agg: str, output_dir: Path) -> pd.DataFrame:
    filename_prefix = "hazard" if agg == "mean" else "quantile"
    filepath = Path(output_dir) / f"{filename_prefix}_curve-{agg}-{imt}_{hazard_id}.csv"
    if not filepath.exists():
        raise KeyError(f"Hazard curve not found for {hazard_id}, {imt}, {agg}")
    return pd.read_csv(filepath, header=1)


def _disagg_filepath(hazard_id: str, location: CodedLocation, agg: str, output_dir: Path) -> Path:

    # start by looking for the file with the most disagg dimensions and work down to the least until a file is found
    file_prefixes = [
        'TRT_Mag_Dist_Eps',
        'TRT_Mag_Dist',
        # 'TRT_Lon_Lat',
        'TRT_Mag',
        'TRT',
        # 'Mag_Lon_Lat',
        # 'Lon_Lat',
        'Mag_Dist_Eps',
        'Mag_Dist',
        'Dist',
        'Mag',
    ]
    for prefix in file_prefixes:
        for filepath in output_dir.glob(f"{prefix}-{agg}-*_{hazard_id}.csv"):
            header_data = _get_disagg_header_data(filepath)
            file_location = CodedLocation(header_data['lat'], header_data['lon'], RESOLUTION)
            if file_location == location:
                return filepath
    raise KeyError(f"Disaggregation not found for {hazard_id}, {agg}")


def _get_disagg_df(hazard_id: str, location: CodedLocation, agg: str, output_dir: Path) -> pd.DataFrame:
    filepath = _disagg_filepath(hazard_id, location, agg, output_dir)
    df = pd.read_csv(filepath, header=1)
    header_data = _get_disagg_header_data(filepath)

    # convert poes from OQ to annual, if necessary
    if (inv_time := header_data['investigation_time']) != 1.0:
        df['poe'] = df.apply(lambda row: convert_poe(row['poe'], inv_time, 1.0), axis=1)

    return df


class OQCSVHazardLoader:
    """A class for loading hazard curves from OpenQuake csv output."""

    def __init__(self, output_dir: Path | str):
        """Initialize a new OQCSVHazardLoader object.

        Args:
            output_dir: The path to the folder where the output csv files are stored.
        """
        if not Path(output_dir).is_dir():
            raise FileNotFoundError(f"No such directory {output_dir}")
        self._output_dir = Path(output_dir)
        self._levels: 'npt.NDArray' | None = None

    def get_probabilities(
        self, hazard_model_id: str | int, imt: str, location: "CodedLocation", vs30: int, agg: str
    ) -> 'npt.NDArray':
        """Get the probablity values for a hazard curve.

        Note that because the OpenQuake csv file does not store the site conditions, the vs30 argument
        is a dummy value. It is the responsibility of the user to check that the OpenQuake calculation
        was performed with the desired site conditions.

        Args:
            hazard_model_id: The calculation ID of the OpenQuake run.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: Not used.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            The probability values.

        Raises:
            KeyError: If no records or more than one record is found in the database.
        """
        hazard_model_id = str(hazard_model_id)

        df = _get_hazard_curve_df(hazard_model_id, imt, agg, self._output_dir)

        if self._levels is None:
            self._set_levels(df)

        poe_columns = [col_name for col_name in df.columns if 'poe-' in col_name]
        # df['location'] = df.apply(lambda row: get_location(row), axis=1)
        df['location'] = df.apply(lambda row: CodedLocation(row['lat'], row['lon'], RESOLUTION), axis=1)
        loc_entry = df.loc[df['location'].eq(location)]
        if len(loc_entry) == 0:
            raise KeyError(f"no records found for location {location} in {self._output_dir}")
        if len(loc_entry) > 1:
            raise KeyError(f"more than one entry found for location {location} in {self._output_dir}")

        return loc_entry.iloc[0][poe_columns].to_numpy(dtype='float64')

    def _set_levels(self, df: pd.DataFrame) -> None:
        poe_columns = [col_name for col_name in df.columns if 'poe-' in col_name]
        self._levels = np.array([float(col[4:]) for col in poe_columns])

    def get_levels(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, agg: str
    ) -> 'npt.NDArray':
        """Get the intensity measure levels for a hazard curve.

        Note that because the OpenQuake csv file does not store the site conditions, the vs30 argument
        is a dummy value. It is the responsibility of the user to check that the OpenQuake calculation
        was performed with the desired site conditions.

        Args:
            hazard_model_id: The calculation ID of the OpenQuake run.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: Not used.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            The intensity measure values.
        """
        hazard_model_id = str(hazard_model_id)

        if self._levels is None:
            df = _get_hazard_curve_df(hazard_model_id, imt, agg, self._output_dir)
            self._set_levels(df)

        return cast(np.ndarray, self._levels)


class OQCSVDisaggLoader:
    """A class for loading disaggregations from OpenQuake csv output."""

    def __init__(self, output_dir: Path | str):
        """Initialize a new OQCSVDisaggLoader object.

        Args:
            output_dir: The path to the folder where the output csv files are stored.
        """
        if not Path(output_dir).is_dir():
            raise FileNotFoundError(f"No such directory {output_dir}")
        self._output_dir = Path(output_dir)

    def get_disagg(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, poe: 'ProbabilityEnum', agg: str
    ) -> 'npt.NDArray':
        """Get the disaggregation values.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: Not used.
            poe: The probability of exceedance.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            Array of probability contributions from each disaggregation bin.
                Array has demensionallity matching the number of disaggregation dimensions with the length along
                each dimension matching the number of bins. The order of dimensions matches the order of the bins
                from the get_bin_centers method. Indexing order is 'matrix' indexing.

        Raises:
            KeyError: If no records or more than one record is found in the database.
        """
        df = _get_disagg_df(hazard_model_id, location, agg, self._output_dir)
        bin_centers = self.get_bin_centers(hazard_model_id, imt, location, vs30, poe, agg)
        array_shape = [len(b) for b in bin_centers.values()]
        n_bins = math.prod(array_shape)

        # use approximate equality to compare floating point numbers
        poe_rows = np.isclose(df['poe'], poe.value)
        df = df.loc[df['imt'].eq(imt) & poe_rows]
        if len(df) == 0:
            raise KeyError(f"no records found for location {location} and poe {poe} in {self._output_dir}")
        if len(df) != n_bins:
            raise KeyError(f"more than one entry found for location {location} and {poe} in {self._output_dir}")

        # this is likely not the fastest way to create the reshaped disagg array, but it's easy and we don't care
        # about speed as this class will not be used often
        probs = np.empty(array_shape)
        for ri, row in df.iterrows():
            ind = []
            for name, values in bin_centers.items():
                ind.append(np.where(values == row[name])[0][0])
            probs[tuple(ind)] = row[agg]

        return probs

    def get_bin_centers(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, poe: 'ProbabilityEnum', agg: str
    ) -> dict[str, 'npt.NDArray']:
        """Get the disaggregation bin centers.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: Not used.
            poe: The probability of exceedance.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            Array of probability contributions from each disaggregation bin.
                Array has demensionallity matching the number of disaggregation dimensions with the length along
                each dimension matching the number of bins. The order of dimensions matches the order of the bins
                from the get_bin_centers method.

        Raises:
            KeyError: If no records or more than one record is found in the database.
        """
        disaggs = _get_disagg_df(hazard_model_id, location, agg, self._output_dir)
        all_disagg_columns = ['trt', 'mag', 'dist', 'eps']
        disagg_columns = [col for col in all_disagg_columns if col in disaggs.columns]
        return {col: np.sort(disaggs[col].unique()) for col in disagg_columns}

    @cache
    def get_bin_edges(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, poe: 'ProbabilityEnum', agg: str
    ) -> dict[str, 'npt.NDArray']:
        """Get the disaggregation bin centers.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: The vs30 of the site.
            poe: The probability of exceedance.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            The disaggregation bin centers with the keys being the disaggregation dimension names (e.g. "TRT", "dist")
                and the values being the bin centers.
        """
        filepath = _disagg_filepath(hazard_model_id, location, agg, self._output_dir)
        header_data = _get_disagg_header_data(filepath)
        return {k[:-10]: v for k, v in header_data.items() if "edges" in k}
