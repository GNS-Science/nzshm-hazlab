from pathlib import Path
import pyarrow.compute as pc
import pyarrow.dataset as ds
from pyarrow import fs
from toshi_hazard_store.model.revision_4 import hazard_aggregate_curve, pyarrow_aggr_dataset, pyarrow_dataset
from typing import TYPE_CHECKING
from nzshm_hazlab.constants import RESOLUTION

if TYPE_CHECKING:
    from nzshm_common.location import CodedLocation
    import numpy as np


def _get_realizations_dataset(dataset_dir: Path | str) -> ds.Dataset:
    rlz_dir, filesystem = pyarrow_dataset.configure_output(str(dataset_dir))
    dataset = ds.dataset(rlz_dir, format='parquet', filesystem=filesystem, partitioning='hive')
    return dataset

class THPLoader:

    def __init__(self, dataset_dir: Path | str):
        self._dataset = _get_realizations_dataset(dataset_dir)

    def get_probabilities(self, hazard_id: str, imt: str, location: 'CodedLocation', aggregate: str, vs30: int) -> np.ndarray:

        loc_strs = [loc.downsample(RESOLUTION).code for loc in locs]
        naggs = len(aggs)
        nimts = len(imts)

        location = locs[0]
        imt = imts[0]
        nloc_001s = [loc.downsample(0.001).code for loc in locs]
        flt = (
            (pc.is_in(pc.field('agg') == pc.scalar(aggregate)))
            & (pc.is_in(pc.field('imt') == pc.scalar(imt)))
            & (pc.is_in(pc.field('nloc_001') == pc.scalar(nloc_001)))
            & (pc.field('vs30') == pc.scalar(vs30))
            & (pc.field('hazard_model_id') == pc.scalar(hazard_id))
        )
        columns = ['agg', 'values', 'vs30', 'imt', 'lat', 'lon']
        arrow_scanner = ds.Scanner.from_dataset(dataset, filter=flt, columns=columns)
        table = arrow_scanner.to_table()
        hazard_curves = table.to_pandas()
        hazard_curves[['lat', 'lon']] = hazard_curves[['lat', 'lon']].applymap(lambda x: '{0:.3f}'.format(x))
        hazard_curves['level'] = pd.NA
        hazard_curves['level'] = hazard_curves['level'].apply(lambda x: imtls)
        hazard_curves.rename({'values': 'apoe'}, axis='columns', inplace=True)


    def get_levels(self, hazard_id: str, imt: str, location: 'CodedLocation', aggregate: str, vs30: int) -> np.ndarray:
        ...
