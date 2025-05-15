from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from nzshm_common import CodedLocation


class DataLoader(Protocol):

    def get_probabilities(self, hazard_id: str, imt: str, location: 'CodedLocation', agg: str, vs30: int) -> np.ndarray:
        ...

    def get_levels(self, hazard_id: str, imt: str, location: 'CodedLocation', agg: str, vs30: int) -> np.ndarray:
        ...
