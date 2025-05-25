"""This module provides the Protocol DataLoader class."""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import numpy as np
    from nzshm_common import CodedLocation


class HazardLoader(Protocol):
    """The Protocol class for a DataLoader.

    To plot a standard hazard curve you would plot the array from get_levels on the x axis the array
    from get_probablities on the y axis.
    """

    def get_probabilities(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> np.ndarray:
        """Get the probablity values for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: The vs30 of the site.

        Returns:
            The probability values.
        """
        ...

    def get_levels(self, hazard_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int) -> np.ndarray:
        """Get the intensity measure levels for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: The vs30 of the site.

        Returns:
            The intensity measure values.
        """
        ...
