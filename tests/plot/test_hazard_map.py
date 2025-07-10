import pytest
from matplotlib.testing.decorators import image_comparison
from toshi_hazard_store.model import ProbabilityEnum

from nzshm_hazlab.plot import plot_hazard_diff_map, plot_hazard_map

vs30 = 400
hazard_model_id = "NSHM_v1.0.4"
agg = "mean"
grid_name = "NZ_0_1_NB_1_1"
poe = ProbabilityEnum._10_PCT_IN_50YRS
imt = "PGA"

hmids = [hazard_model_id, hazard_model_id]
imts = [imt, "SA(1.0)"]
vs30s = [vs30, 750]
poes = [poe, ProbabilityEnum._2_PCT_IN_50YRS]
aggs = [agg, agg]


@image_comparison(baseline_images=['hazard_map'], extensions=['png'], style='mpl20')
def test_plot_hazard_map(hazard_grids):
    hazard_model_id = "NSHM_v1.0.4"
    poe = ProbabilityEnum._10_PCT_IN_50YRS

    fig, ax = plot_hazard_map(hazard_grids, hazard_model_id, grid_name, imt, vs30, poe, agg, clim=[0, 1.5])


@image_comparison(baseline_images=['hazard_map_defaultc'], extensions=['png'], style='mpl20')
def test_plot_hazard_map_defaultc(hazard_grids):
    """Test default color limits."""
    hazard_model_id = "NSHM_v1.0.4"
    poe = ProbabilityEnum._10_PCT_IN_50YRS
    imt = "PGA"

    fig, ax = plot_hazard_map(hazard_grids, hazard_model_id, grid_name, imt, vs30, poe, agg)


@image_comparison(baseline_images=['hazard_diff_map_sub'], extensions=['png'], style='mpl20')
def test_plot_hazard_diff_map_sub(hazard_grids):
    hgs = [hazard_grids, hazard_grids]
    diff_type = 'sub'
    fig, ax = plot_hazard_diff_map(hgs, hmids, grid_name, imts, vs30s, poes, aggs, diff_type=diff_type)


@image_comparison(baseline_images=['hazard_diff_map_ratio'], extensions=['png'], style='mpl20')
def test_plot_hazard_diff_map_ratio(hazard_grids):
    hgs = [hazard_grids, hazard_grids]
    diff_type = 'ratio'
    fig, ax = plot_hazard_diff_map(hgs, hmids, grid_name, imts, vs30s, poes, aggs, diff_type=diff_type)


def test_plot_hazard_diff_map_err(hazard_grids):
    hgs = [hazard_grids, hazard_grids]
    diff_type = 'not an option'
    with pytest.raises(ValueError):
        fig, ax = plot_hazard_diff_map(hgs, hmids, grid_name, imts, vs30s, poes, aggs, diff_type=diff_type)

    diff_type = 'ratio'
    with pytest.raises(ValueError):
        fig, ax = plot_hazard_diff_map(
            [hazard_grids], [hazard_model_id], grid_name, [imt], [vs30], [poe], [agg], diff_type=diff_type
        )
