"""This module provies the DynamoLoader class."""

from typing import TYPE_CHECKING

import numpy as np
from toshi_hazard_store import query

if TYPE_CHECKING:
    from nzshm_common import CodedLocation  # prgama: no cover


class DynamoLoader:
    """A class for loading hazard curves from toshi-hazard-store DynamoDB.

    The use of DynamoDB for storing hazard curves is depricated and will be removed with v2 of toshi-hazard-store.
    """

    def __init__(self):
        """Initialize a DynamoLoader object."""
        self._levels: np.ndarray | None = None

    def get_probabilities(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> np.ndarray:
        """Get the probablity values for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: The vs30 of the site.

        Returns:
            The probability values.
        """
        res = next(query.get_hazard_curves([location.code], [vs30], [hazard_model_id], [imt], [agg]))
        if self._levels is None:
            self._levels = np.array([float(item.lvl) for item in res.values])
        return np.array([float(item.val) for item in res.values])

    def get_levels(self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int) -> np.ndarray:
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
        if self._levels is None:
            res = next(query.get_hazard_curves([location.code], [vs30], [hazard_model_id], [imt], [agg]))
            self._levels = np.array([float(item.lvl) for item in res.values])
        return self._levels
