from typing import TYPE_CHECKING
import numpy as np
import functools
from toshi_hazard_post.logic_tree import HazardLogicTree
import toshi_hazard_post.data as data
import toshi_hazard_post.aggregation_calc as aggregation
import toshi_hazard_post.calculators as calculators


if TYPE_CHECKING:
    import numpy.typing as npt
    from nzshm_common import CodedLocation
    import pyarrow.dataset as ds
    import pyarrow as pa
    from nzshm_model.logic_tree import GMCMLogicTree, SourceLogicTree



@functools.cache
def _get_batch_table_cached(
    dataset: 'ds.Dataset',
    compatibility_key: str,
    sources_digests: tuple[str],
    gmms_digests: tuple[str],
    nloc_0: str,
    vs30: int,
    imts: tuple[str],
) -> 'pa.Table':

    print("table not cached")
    return data.get_batch_table(dataset, compatibility_key, sources_digests, gmms_digests, nloc_0, vs30, imts)


class THPHazardLoader:
    """A class for loading hazard curves from toshi-hazard-store."""

    def __init__(self, compatibility_key: str, srm_logic_tree: 'SourceLogicTree', gmcm_logic_tree: 'GMCMLogicTree'):

        logic_tree = HazardLogicTree(srm_logic_tree, gmcm_logic_tree)
        self.branch_hash_table = logic_tree.branch_hash_table
        self.weights = logic_tree.weights
        self.compatibility_key = compatibility_key
        self.dataset = data.get_realizations_dataset()
        component_branches = logic_tree.component_branches
        self.gmms_digests = [branch.gmcm_hash_digest for branch in component_branches]
        self.sources_digests = [branch.source_hash_digest for branch in component_branches]


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

        agg_types = [agg]
        imts = [imt]
        nloc_0 = location.downsample(1.0).code    
        batch_datatable = _get_batch_table_cached(
                self.dataset, self.compatibility_key, tuple(self.sources_digests), tuple(self.gmms_digests), nloc_0, vs30, tuple(imts)
            )
        job_datatable = data.get_job_datatable(batch_datatable, location, imt, len(self.sources_digests))
        component_probs = job_datatable.to_pandas()
        component_rates = aggregation.convert_probs_to_rates(component_probs)
        component_rates = aggregation.create_component_dict(component_rates)
        composite_rates = aggregation.build_branch_rates(self.branch_hash_table, component_rates)
        hazard = aggregation.calculate_aggs(composite_rates, self.weights, agg_types)
        return calculators.rate_to_prob(hazard, 1.0)[0,:]

    # TODO: get actual levels once they are stored by THS
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