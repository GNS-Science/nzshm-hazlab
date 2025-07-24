"""This module provies the THSHazardLoader class."""

from typing import TYPE_CHECKING

import numpy as np
from toshi_hazard_store.query.datasets import get_hazard_curves

if TYPE_CHECKING:
    import numpy.typing as npt
    from nzshm_common import CodedLocation


class THSHazardLoader:
    """A class for loading hazard curves from toshi-hazard-store.

    Specify the location of the dataset with environment variable 'THS_DATASET_AGGR_URI'.
    """

    def __init__(self):
        """Initialize a THSHazardLoader object."""
        self._levels: None | 'npt.NDArray' = None

    def get_probabilities(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, agg: str
    ) -> 'npt.NDArray':
        """Get the probablity values for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: The vs30 of the site.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            The probability values.

        Raises:
            KeyError: If no records are found.
        """
        # try differenty query strategies starting with the most efficient partitioning
        for strategy in ['d2', 'd1', 'native']:
            try:
                # using next(), we should only get one result
                agg_hazard = next(
                    get_hazard_curves(
                        [location.downsample(0.001).code], [vs30], hazard_model_id, [imt], [agg], strategy
                    )
                )
                break
            except RuntimeWarning:
                continue
            except StopIteration:
                raise KeyError(f"agg dataset does not contain {hazard_model_id=}, {imt=}, {location=}, {vs30=}, {agg=}")

        if self._levels is None:
            self._levels = np.array([v.lvl for v in agg_hazard.values])
        return np.array([v.val for v in agg_hazard.values])

    def get_levels(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, agg: str
    ) -> 'npt.NDArray':
        """Get the intensity measure levels for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: The vs30 of the site.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            The intensity measure values.
        """
        if self._levels is None:
            _ = self.get_probabilities(hazard_model_id, imt, location, vs30, agg)
        assert self._levels is not None  # for type checking
        return self._levels
