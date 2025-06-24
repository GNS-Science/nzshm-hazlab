"""This module provies the THSHazardLoader class."""

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pyarrow.compute as pc
import pyarrow.dataset as ds
from toshi_hazard_store.model.pyarrow import pyarrow_dataset

if TYPE_CHECKING:
    import numpy.typing as npt  # pragma: no cover
    from nzshm_common import CodedLocation  # pragma: no cover


def _get_realizations_dataset(dataset_dir: str) -> ds.Dataset:
    rlz_dir, filesystem = pyarrow_dataset.configure_output(dataset_dir)
    dataset = ds.dataset(rlz_dir, format="parquet", filesystem=filesystem, partitioning="hive")
    return dataset


class THSHazardLoader:
    """A class for loading hazard curves from toshi-hazard-store."""

    def __init__(self, dataset_dir: Path | str):
        """Initialize a THSHazardLoader object.

        Args:
            dataset_dir: location of dataset (parquet) files. This can be a local filepath or S3 bucket URI.
        """
        if not (isinstance(dataset_dir, str) and dataset_dir[0:5] == "s3://"):
            dataset_dir = Path(dataset_dir).expanduser()
        self._dataset = _get_realizations_dataset(str(dataset_dir))
        self._levels: None | 'npt.NDArray' = None

    def get_probabilities(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> 'npt.NDArray':
        """Get the probablity values for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: The vs30 of the site.

        Returns:
            The probability values.

        Raises:
            KeyError: If no records are found.
        """
        nloc_001 = location.downsample(0.001).code
        nloc_0 = location.downsample(1.0).code
        flt = (
            (pc.field("aggr") == pc.scalar(agg))
            & (pc.field("imt") == pc.scalar(imt))
            & (pc.field("nloc_0") == pc.scalar(nloc_0))
            & (pc.field("nloc_001") == pc.scalar(nloc_001))
            & (pc.field("vs30") == pc.scalar(vs30))
            & (pc.field("hazard_model_id") == pc.scalar(hazard_model_id))
        )
        arrow_scanner = ds.Scanner.from_dataset(self._dataset, filter=flt)
        table = arrow_scanner.to_table()
        values = table.column("values").to_numpy()
        if len(values) != 1:
            raise KeyError("pyarrow filter on agg dataset did not result in a single entry")

        return values[0]

    # TODO: get actual levels once they are stored by THS
    def get_levels(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> 'npt.NDArray':
        """Get the intensity measure levels for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: The vs30 of the site.

        Returns:
            The intensity measure values.
        """
        return np.array(
            [
                0.0001,
                0.0002,
                0.0004,
                0.0006,
                0.0008,
                0.001,
                0.002,
                0.004,
                0.006,
                0.008,
                0.01,
                0.02,
                0.04,
                0.06,
                0.08,
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6,
                0.7,
                0.8,
                0.9,
                1.0,
                1.2,
                1.4,
                1.6,
                1.8,
                2.0,
                2.2,
                2.4,
                2.6,
                2.8,
                3.0,
                3.5,
                4.0,
                4.5,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
            ]
        )
