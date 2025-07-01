"""This module provies the DynamoHazardLoader and DynamoDisaggLoader classes."""

from typing import TYPE_CHECKING

import numpy as np
from toshi_hazard_store import query
from toshi_hazard_store.model import AggregationEnum

from nzshm_hazlab.base_functions import convert_poe

if TYPE_CHECKING:
    import numpy.typing as npt
    from nzshm_common import CodedLocation
    from toshi_hazard_store.model import ProbabilityEnum


class DynamoHazardLoader:
    """A class for loading hazard curves from toshi-hazard-store DynamoDB.

    The use of DynamoDB for storing hazard curves is depricated and will be removed with v2 of toshi-hazard-store.
    """

    def __init__(self):
        """Initialize a DynamoHazardLoader object."""
        self._levels: 'npt.NDArray' | None = None

    def get_probabilities(
        self, hazard_model_id: str, imt: str, location: 'CodedLocation', vs30: int, agg: str
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
        """
        res = next(query.get_hazard_curves([location.code], [vs30], [hazard_model_id], [imt], [agg]))
        if self._levels is None:
            self._levels = np.array([float(item.lvl) for item in res.values])
        return np.array([float(item.val) for item in res.values])

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
            res = next(query.get_hazard_curves([location.code], [vs30], [hazard_model_id], [imt], [agg]))
            self._levels = np.array([float(item.lvl) for item in res.values])
        return self._levels


class DynamoDisaggLoader:
    """A class for loading disaggregation matricies from toshi-hazard-store DynamoDB."""

    def get_disagg(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, poe: 'ProbabilityEnum', agg: str
    ) -> 'npt.NDArray':
        """Get the disaggregation values.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: The vs30 of the site.
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
        agg = AggregationEnum(agg.lower())
        location = location.downsample(0.001).code
        return next(
            query.get_disagg_aggregates(
                [hazard_model_id], [agg], [AggregationEnum.MEAN], [location], [vs30], [imt], [poe]
            )
        ).disaggs

    def get_bin_centers(
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
            Array of probability contributions from each disaggregation bin.
                Array has demensionallity matching the number of disaggregation dimensions with the length along
                each dimension matching the number of bins. The order of dimensions matches the order of the bins
                from the get_bin_centers method.

        Raises:
            KeyError: If no records or more than one record is found in the database.
        """
        agg = AggregationEnum(agg.lower())
        location = location.downsample(0.001).code
        bins = next(
            query.get_disagg_aggregates(
                [hazard_model_id], [agg], [AggregationEnum.MEAN], [location], [vs30], [imt], [poe]
            )
        ).bins
        dimensions = ["mag", "dist", "trt", "eps"]
        return {d: b for d, b in zip(dimensions, bins)}

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

        Raises:
            NotImplementedError: Dynamo database does not provide bin edges.
        """
        raise NotImplementedError("get_bin_edges is not implemented for the DynamoDisaggLoader class")


class DynamoGridLoader:
    """A class for loading hazard grid data from toshi-hazard-store DynamoDB."""

    def get_grid(
        self, hazard_model_id: str, imt: str, grid_name: str, vs30: int, poe: 'ProbabilityEnum', agg: str
    ) -> 'npt.NDArray':
        """Get the hazard grid IMTL values.

        Args:
            hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            grid_name: The site location for the hazard curve.
            vs30: The vs30 of the site.
            poe: The probability of exceedance.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            The intensity measure levels (IMTLs) at the poe of interest over the grid. The array is 1D and its entries
                are in the same order as the locations retrieved from nzshm_common.grids.get_location_grid.
        """
        poe_in_50 = round(convert_poe(poe.value, 1.0, 50.0), 4)
        return np.array(
            next(query.get_gridded_hazard([hazard_model_id], [grid_name], [vs30], [imt], [agg], [poe_in_50])).grid_poes
        )
