"""This module provides the THPHazardLoader class for producing hazard curves from dynamically created hazard models."""

import functools
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import numpy as np
import toshi_hazard_post.aggregation_calc as aggregation
import toshi_hazard_post.calculators as calculators
import toshi_hazard_post.data as data
from toshi_hazard_post.logic_tree import HazardLogicTree

if TYPE_CHECKING:
    import numpy.typing as npt
    import pyarrow as pa
    import pyarrow.dataset as ds
    from nzshm_common import CodedLocation
    from nzshm_model.logic_tree import GMCMLogicTree, SourceLogicTree


@functools.cache
def _get_batch_table_cached(
    dataset: 'ds.Dataset',
    compatible_calc_id: str,
    sources_digests: tuple[str],
    gmms_digests: tuple[str],
    nloc_0: str,
    vs30: int,
    imts: tuple[str],
) -> 'pa.Table':

    return data.get_batch_table(dataset, compatible_calc_id, sources_digests, gmms_digests, vs30, nloc_0, imts)


class THPHazardLoader:
    """A class for creating hazard curves from user-defined hazard models.

    This class allows a user to calculate hazard curves from a hazard model comprised of user-defined source
    and ground motion logic trees. The logic trees are comprised of branches for which realizations have
    been pre-computed and stored in a Arrow dataset by toshi-hazard-store. See the nzshm-model documentation
    for how to build the logic tree objects needed to define the hazard model.

    The location of the realizations database is set with the environment variable THP_RLZ_DIR, in a .env file
    or by passing the location on initilaization. The location can be a local file path or an s3 bucket URI.

    Examples:
        ```py
        from nzshm_hazlab.data.data_loaders import THPHazardLoader
        from nzshm_hazlab.data import HazardCurves
        from nzshm_model.logic_tree import SourceLogicTree, GMCMLogicTree

        hazard_model_ths = "NSHM_v1.0.4"
        slt = SourceLogicTree.from_json("srm_logic_tree.json")
        gmcm = GMCMLogicTree.from_json("gmcm_logic_tree.json")
        thp_loader = THPHazardLoader("NZSHM22", slt, gmcm)
        ```
    """

    def __init__(
        self,
        compatible_calc_id: str,
        srm_logic_tree: 'SourceLogicTree',
        gmcm_logic_tree: 'GMCMLogicTree',
        rlz_dir: Optional[str | Path] = None,
    ):
        """Initialize a new THPHazardLoader object.

        Args:
            compatible_calc_id: The ID of a compatible calculation for PSHA engines interoperability. See the
                toshi-hazard-store documentation for details.
            srm_logic_tree: The seismicity rate model (aka source model) logic tree.
            gmcm_logic_tree: The ground motion model logic tree.
            rlz_dir: Location of realization dataset. If not passed, function will use env var.
        """
        self.compatible_calc_id = compatible_calc_id

        logic_tree = HazardLogicTree(srm_logic_tree, gmcm_logic_tree)

        component_branches = logic_tree.component_branches
        self.gmms_digests = [branch.gmcm_hash_digest for branch in component_branches]
        self.sources_digests = [branch.source_hash_digest for branch in component_branches]

        self.branch_hash_table = logic_tree.branch_hash_table
        self.weights = logic_tree.weights

        self.dataset = data.get_realizations_dataset(rlz_dir=rlz_dir)

    def get_probabilities(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, agg: str
    ) -> 'npt.NDArray':
        """Get the probablity values for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model. This is not used for the THP loader and can
                take on any value.
            imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
            location: The site location for the hazard curve.
            vs30: The vs30 of the site.
            agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.

        Returns:
            The probability values.
        """
        agg_types = [agg]
        imts = [imt]
        nloc_0 = location.downsample(1.0).code
        batch_datatable = _get_batch_table_cached(
            self.dataset,
            self.compatible_calc_id,
            tuple(self.sources_digests),
            tuple(self.gmms_digests),
            nloc_0,
            vs30,
            tuple(imts),
        )
        job_datatable = data.get_job_datatable(batch_datatable, location, imt, len(self.sources_digests))
        component_probs = job_datatable.to_pandas()
        component_rates = aggregation.convert_probs_to_rates(component_probs)
        component_rates = aggregation.create_component_dict(component_rates)
        composite_rates = aggregation.build_branch_rates(self.branch_hash_table, component_rates)
        hazard = aggregation.calculate_aggs(composite_rates, self.weights, agg_types)
        return calculators.rate_to_prob(hazard, 1.0)[0, :]

    # TODO: get actual levels once they are stored by THS
    def get_levels(
        self, hazard_model_id: str, imt: str, location: "CodedLocation", vs30: int, agg: str
    ) -> 'npt.NDArray':
        """Get the intensity measure levels for a hazard curve.

        Args:
            hazard_model_id: The identifier of the hazard model. This is not used for the THP loader and can
                take on any value.
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
