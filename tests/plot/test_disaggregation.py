from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.testing.decorators import image_comparison
from nzshm_common.location import get_locations
from toshi_hazard_store.model import ProbabilityEnum

from nzshm_hazlab.data import Disaggregations
from nzshm_hazlab.data.data_loaders import OQCSVDisaggLoader
from nzshm_hazlab.plot import plot_disagg_1d, plot_disagg_2d, plot_disagg_3d

hazard_model = "31"
imt = "PGA"
location = get_locations(["WLG"])[0]
agg = "mean"
vs30 = "400"
poe = ProbabilityEnum._10_PCT_IN_50YRS


@pytest.fixture(scope='module')
def disaggregations():
    oq_output_dir = Path(__file__).parent.parent / "fixtures/data/csv_loader"
    loader = OQCSVDisaggLoader(oq_output_dir)
    return Disaggregations(loader=loader)


@image_comparison(baseline_images=['disagg_1d_trt'], extensions=['png'], style='mpl20')
def test_plot_disagg_1d(disaggregations):
    _, ax = plt.subplots(1, 1)
    plot_disagg_1d(ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimension="trt")


@image_comparison(baseline_images=['disagg_1d_mag_reg'], extensions=['png'], style='mpl20')
def test_plot_disagg_1d_kwargs(disaggregations):
    _, ax = plt.subplots(1, 1)
    plot_disagg_1d(
        ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimension="mag", width=0.15, color='r'
    )


@image_comparison(baseline_images=['disagg_2d_mag_dist'], extensions=['png'], style='mpl20')
def test_plot_disagg_2d(disaggregations):
    _, ax = plt.subplots(1, 1)
    plot_disagg_2d(ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["mag", "dist"])


@image_comparison(baseline_images=['disagg_2d_dist_mag'], extensions=['png'], style='mpl20')
def test_plot_disagg_2d_swap(disaggregations):
    _, ax = plt.subplots(1, 1)
    plot_disagg_2d(ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["dist", "mag"])


@image_comparison(baseline_images=['disagg_2d_pct_lim'], extensions=['png'], style='mpl20')
def test_plot_disagg_2d_pct_lim(disaggregations):
    _, ax = plt.subplots(1, 1)
    plot_disagg_2d(
        ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["dist", "mag"], pct_lim=[0, 0.5]
    )


@image_comparison(baseline_images=['disagg_2d_plasma'], extensions=['png'], style='mpl20')
def test_plot_disagg_2d_colormap(disaggregations):
    _, ax = plt.subplots(1, 1)
    plot_disagg_2d(
        ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["dist", "mag"], cmap='plasma'
    )


@image_comparison(baseline_images=['disagg_2d_trt'], extensions=['png'], style='mpl20')
def test_plot_disagg_2d_trt(disaggregations):
    _, ax = plt.subplots(1, 3)
    plot_disagg_2d(
        list(ax),
        disaggregations,
        hazard_model,
        location,
        imt,
        vs30,
        poe,
        agg,
        dimensions=["mag", "dist"],
        split_by_trt=True,
    )


@pytest.mark.skip(reason="fails in GHA")
@image_comparison(baseline_images=['disagg_3d'], extensions=['png'], style='mpl20')
def test_plot_disagg_3d(disaggregations):
    fig = plt.figure()
    plot_disagg_3d(fig, disaggregations, hazard_model, location, imt, vs30, poe, agg, dist_lim=[0, 70])


@pytest.mark.parametrize(
    "dimensions, error_msg",
    (
        (["mag", "dist", "eps"], "must have length"),
        (["mag", "trt"], "Cannot specify trt"),
    ),
)
def test_plot_disagg_2d_dimension_error(disaggregations, dimensions, error_msg):
    _, ax = plt.subplots(1, 1)
    with pytest.raises(ValueError) as ve:
        plot_disagg_2d(ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=dimensions)
    assert error_msg in str(ve.value)


def test_plot_disagg_2d_shading_error(disaggregations):
    _, ax = plt.subplots(1, 3)
    with pytest.raises(KeyError) as ke:
        plot_disagg_2d(
            ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["mag", "dist"], shading='flat'
        )
    assert "specify shading" in str(ke.value)


def test_plot_disagg_2d_pct_lim_error(disaggregations):
    _, ax = plt.subplots(1, 3)
    pct_lim = [0]
    with pytest.raises(ValueError) as ve:
        plot_disagg_2d(
            ax,
            disaggregations,
            hazard_model,
            location,
            imt,
            vs30,
            poe,
            agg,
            dimensions=["mag", "dist"],
            pct_lim=pct_lim,
        )
    assert "pct_lim must have length of 2" in str(ve.value)


def test_plot_disagg_2d_trt_axes_error1(disaggregations):
    _, ax = plt.subplots(1, 1)
    with pytest.raises(TypeError) as te:
        plot_disagg_2d(
            ax,
            disaggregations,
            hazard_model,
            location,
            imt,
            vs30,
            poe,
            agg,
            dimensions=["mag", "dist"],
            split_by_trt=True,
        )
    assert "axes must be a sequence" in str(te.value)


def test_plot_disagg_2d_trt_axes_error2(disaggregations):
    _, ax = plt.subplots(1, 3)
    ax = ax[0:1]
    with pytest.raises(ValueError) as ve:
        plot_disagg_2d(
            list(ax),
            disaggregations,
            hazard_model,
            location,
            imt,
            vs30,
            poe,
            agg,
            dimensions=["mag", "dist"],
            split_by_trt=True,
        )
    assert "must have the same number" in str(ve.value)
