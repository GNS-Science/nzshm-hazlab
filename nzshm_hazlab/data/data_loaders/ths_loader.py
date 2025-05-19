from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pyarrow.compute as pc
import pyarrow.dataset as ds
from toshi_hazard_store.model.revision_4 import pyarrow_dataset

if TYPE_CHECKING:
    from nzshm_common import CodedLocation

def _get_realizations_dataset(dataset_dir: Path) -> ds.Dataset:
    rlz_dir, filesystem = pyarrow_dataset.configure_output(str(dataset_dir))
    dataset = ds.dataset(rlz_dir, format="parquet", filesystem=filesystem, partitioning="hive")
    return dataset


class THSLoader:

    def __init__(self, dataset_dir: Path | str):
        self._dataset = _get_realizations_dataset(Path(dataset_dir).expanduser())
        self._levels: None | np.ndarray = None

    def get_probabilities(
        self, hazard_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> 'np.ndarray':

        nloc_001 = location.downsample(0.001).code
        flt = (
            (pc.field("agg") == pc.scalar(agg))
            & (pc.field("imt") == pc.scalar(imt))
            & (pc.field("nloc_001") == pc.scalar(nloc_001))
            & (pc.field("vs30") == pc.scalar(vs30))
            & (pc.field("hazard_model_id") == pc.scalar(hazard_id))
        )
        arrow_scanner = ds.Scanner.from_dataset(self._dataset, filter=flt)
        table = arrow_scanner.to_table()
        values = table.column("values").to_numpy()
        if len(values) != 1:
            raise Exception("pyarrow filter on agg dataset did not result in a single entry")

        return values[0]

    # TODO: get actual levels once they are stored by THS
    def get_levels(self, hazard_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int) -> 'np.ndarray':
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
