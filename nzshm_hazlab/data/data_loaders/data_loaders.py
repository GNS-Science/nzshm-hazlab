"""This module provides the Protocol DataLoader class."""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import numpy.typing as npt
    from nzshm_common import CodedLocation
    from toshi_hazard_store.model import ProbabilityEnum


class HazardLoader(Protocol):
    """The Protocol class for a DataLoader.

    To plot a standard hazard curve you would plot the array from get_levels on the x axis the array
    from get_probablities on the y axis.
    """

    def get_probabilities(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int
    ) -> npt.NDArray:
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

    def get_levels(self, hazard_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int) -> npt.NDArray:
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


class DisaggLoader(Protocol):
    """The protocol class for a disaggregation data loader."""

    def get_disagg(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int, poe: 'ProbabilityEnum'
    ) -> npt.NDArray:
        """Get the disaggregation values.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: The vs30 of the site.
            poe: The probability of exceedance.

        Returns:
            Array of probability contributions from each disaggregation bin.
                Array has demensionallity matching the number of disaggregation dimensions with the length along
                each dimension matching the number of bins. The order of dimensions matches the order of the bins
                from the get_bin_centers method. Indexing order is 'matrix' indexing.

        Raises:
            KeyError: If no records or more than one record is found in the database.
        """
        ...

    def get_bin_centers(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int, poe: 'ProbabilityEnum'
    ) -> dict[str, npt.NDArray]:
        """Get the disaggregation bin centers.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: The vs30 of the site.
            poe: The probability of exceedance.

        Returns:
            Array of probability contributions from each disaggregation bin.
                Array has demensionallity matching the number of disaggregation dimensions with the length along
                each dimension matching the number of bins. The order of dimensions matches the order of the bins
                from the get_bin_centers method.

        Raises:
            KeyError: If no records or more than one record is found in the database.
        """
        ...

    def get_bin_edges(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", agg: str, vs30: int, poe: 'ProbabilityEnum'
    ) -> dict[str, npt.NDArray]:
        """Get the disaggregation bin centers.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
            vs30: The vs30 of the site.
            poe: The probability of exceedance.

        Returns:
            The disaggregation bin centers with the keys being the disaggregation dimension names (e.g. "TRT", "dist")
                and the values being the bin centers.
        """
        ...
