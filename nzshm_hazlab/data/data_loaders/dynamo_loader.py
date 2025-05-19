from typing import TYPE_CHECKING

import numpy as np
from toshi_hazard_store import query

if TYPE_CHECKING:
    from nzshm_common import CodedLocation


class DynamoLoader:

    def __init__(self):
        self._levels: np.ndarray | None = None

    def get_probabilities(self, hazard_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int) -> np.ndarray:
        res = next(query.get_hazard_curves([location.code], [vs30], [hazard_id], [imt], [agg]))
        if self._levels is None:
            self._levels = np.array([float(item.lvl) for item in res.values])
        return np.array([float(item.val) for item in res.values])

    def get_levels(self, hazard_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int) -> np.ndarray:
        if self._levels is None:
            res = next(query.get_hazard_curves([location.code], [vs30], [hazard_id], [imt], [agg]))
            self._levels = np.array([float(item.lvl) for item in res.values])
        return self._levels
