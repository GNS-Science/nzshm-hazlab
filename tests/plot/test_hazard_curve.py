import matplotlib.pyplot as plt
import pytest
from matplotlib.testing.decorators import image_comparison
from nzshm_common import CodedLocation
from nzshm_common.location import get_locations

from nzshm_hazlab.data.data_loaders import THSHazardLoader
from nzshm_hazlab.data.hazard_curves import HazardCurves
from nzshm_hazlab.plot import plot_hazard_curve, plot_uhs
from nzshm_hazlab.plot.hazard_curve import _center_out

hazard_model = "TEST_RUNZI"
vs30 = 400
imt = "PGA"
wlg = get_locations(["WLG"])[0]
other_location = CodedLocation(lat=-41.75, lon=171.58, resolution=0.001)


@pytest.fixture(scope='module')
def hazard_curves():
    loader = THSHazardLoader()
    return HazardCurves(loader=loader)


length_expected = [
    (1, []),
    (2, [[0, 1]]),
    (3, [[0, 2]]),
    (4, [[1, 2], [0, 3]]),
    (5, [[1, 3], [0, 4]]),
    (6, [[2, 3], [1, 4], [0, 5]]),
    (7, [[2, 4], [1, 5], [0, 6]]),
]


@pytest.mark.parametrize("length,expected", length_expected)
def test_center_out(length, expected):
    returned = []
    for left, right in _center_out(length):
        returned.append([left, right])
    assert returned == expected


@image_comparison(baseline_images=['hazard_curve_mean'], extensions=['png'], style='mpl20')
def test_plot_hazard_curve_single(hazard_curves):
    aggs = ["mean"]
    fig, ax = plt.subplots(1, 1)
    plot_hazard_curve(ax, hazard_curves, hazard_model, wlg, imt, vs30, aggs)


@image_comparison(baseline_images=['hazard_curve_even'], extensions=['png'], style='mpl20')
def test_plot_hazard_curve_even(hazard_curves):
    aggs = ["0.1", "0.2", "0.8", "0.9"]
    fig, ax = plt.subplots(1, 1)
    plot_hazard_curve(ax, hazard_curves, hazard_model, wlg, imt, vs30, aggs)


@image_comparison(baseline_images=['hazard_curve_odd'], extensions=['png'], style='mpl20')
def test_plot_hazard_curve_odd(hazard_curves):
    aggs = ["0.1", "0.2", "mean", "0.8", "0.9"]
    fig, ax = plt.subplots(1, 1)
    plot_hazard_curve(ax, hazard_curves, hazard_model, wlg, imt, vs30, aggs)


imts = ["PGA", "SA(0.5)", "SA(1.5)", "SA(3.0)"]
poe = 0.1
inv_time = 50.0


@image_comparison(baseline_images=['uhs_curve_mean'], extensions=['png'], style='mpl20')
def test_plot_uhs_curve_single(hazard_curves):
    aggs = ["mean"]
    fig, ax = plt.subplots(1, 1)
    plot_uhs(ax, hazard_curves, hazard_model, wlg, imts, poe, inv_time, vs30, aggs)


@image_comparison(baseline_images=['uhs_curve_even'], extensions=['png'], style='mpl20')
def test_plot_uhs_curve_even(hazard_curves):
    aggs = ["0.1", "0.2", "0.8", "0.9"]
    fig, ax = plt.subplots(1, 1)
    plot_uhs(ax, hazard_curves, hazard_model, wlg, imts, poe, inv_time, vs30, aggs)


@image_comparison(baseline_images=['uhs_curve_odd'], extensions=['png'], style='mpl20')
def test_plot_uhs_curve_odd(hazard_curves):
    aggs = ["0.1", "0.2", "mean", "0.8", "0.9"]
    fig, ax = plt.subplots(1, 1)
    plot_uhs(ax, hazard_curves, hazard_model, wlg, imts, poe, inv_time, vs30, aggs)
