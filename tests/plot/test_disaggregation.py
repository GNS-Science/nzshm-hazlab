import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
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

if sys.platform.startswith("win"):
    pytest.skip("tests fail on Windows", allow_module_level=True)


@pytest.fixture(scope='module')
def disaggregations():
    oq_output_dir = Path(__file__).parent.parent / "fixtures/data/csv_loader"
    loader = OQCSVDisaggLoader(oq_output_dir)
    return Disaggregations(loader=loader)


@pytest.mark.mpl_image_compare
def test_plot_disagg_1d(disaggregations):
    fig, ax = plt.subplots(1, 1)
    plot_disagg_1d(ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimension="trt")
    return fig


@pytest.mark.mpl_image_compare
def test_plot_disagg_1d_kwargs(disaggregations):
    fig, ax = plt.subplots(1, 1)
    plot_disagg_1d(
        ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimension="mag", width=0.15, color='r'
    )
    return fig


@pytest.mark.mpl_image_compare
def test_plot_disagg_2d(disaggregations):
    fig, ax = plt.subplots(1, 1)
    plot_disagg_2d(ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["mag", "dist"])
    return fig


@pytest.mark.mpl_image_compare
def test_plot_disagg_2d_swap(disaggregations):
    fig, ax = plt.subplots(1, 1)
    plot_disagg_2d(ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["dist", "mag"])
    return fig


@pytest.mark.mpl_image_compare
def test_plot_disagg_2d_pct_lim(disaggregations):
    fig, ax = plt.subplots(1, 1)
    plot_disagg_2d(
        ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["dist", "mag"], pct_lim=[0, 0.5]
    )
    return fig


@pytest.mark.mpl_image_compare
def test_plot_disagg_2d_colormap(disaggregations):
    fig, ax = plt.subplots(1, 1)
    plot_disagg_2d(
        ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["dist", "mag"], cmap='plasma'
    )
    return fig


@pytest.mark.mpl_image_compare
def test_plot_disagg_2d_trt(disaggregations):
    fig, ax = plt.subplots(1, 3)
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
    return fig


@pytest.mark.mpl_image_compare
def test_plot_disagg_3d(disaggregations):
    fig = plt.figure()
    plot_disagg_3d(fig, disaggregations, hazard_model, location, imt, vs30, poe, agg, dist_lim=[0, 70])
    return fig


# def test_plot_disagg_3d_noimage(disaggregations):
#     """Since we skip the image comparison test (test_plot_disagg_3d),
#     run this test just ensure no exceptions raised."""
#     fig = plt.figure()
#     plot_disagg_3d(fig, disaggregations, hazard_model, location, imt, vs30, poe, agg, dist_lim=[0, 70])


@pytest.mark.parametrize(
    "dimensions, error_msg",
    (
        (["mag", "dist", "eps"], "must have length"),
        (["mag", "trt"], "Cannot specify trt"),
    ),
)
def test_plot_disagg_2d_dimension_error(disaggregations, dimensions, error_msg):
    fig, ax = plt.subplots(1, 1)
    with pytest.raises(ValueError) as ve:
        plot_disagg_2d(ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=dimensions)
    assert error_msg in str(ve.value)


def test_plot_disagg_2d_shading_error(disaggregations):
    fig, ax = plt.subplots(1, 3)
    with pytest.raises(KeyError) as ke:
        plot_disagg_2d(
            ax, disaggregations, hazard_model, location, imt, vs30, poe, agg, dimensions=["mag", "dist"], shading='flat'
        )
    assert "specify shading" in str(ke.value)


def test_plot_disagg_2d_pct_lim_error(disaggregations):
    fig, ax = plt.subplots(1, 3)
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
    fig, ax = plt.subplots(1, 1)
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
    fig, ax = plt.subplots(1, 3)
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
