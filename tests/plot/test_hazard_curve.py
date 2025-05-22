from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_hazlab.data.hazard_curves import HazardCurves
from nzshm_hazlab.plot import plot_hazard_curve, plot_uhs

import pytest
from nzshm_common import CodedLocation
from nzshm_common.location.location import _lat_lon

from nzshm_hazlab.constants import RESOLUTION
from nzshm_hazlab.data.data_loaders import THSLoader

hazard_model = "TEST_RUNZI"
vs30 = 400
imt = "PGA"
wlg = CodedLocation(*_lat_lon("WLG"), RESOLUTION)
other_location = CodedLocation(lat=-41.75, lon=171.58, resolution=0.001)


@pytest.fixture(scope='module')
def hazard_curves():
    dataset_dir = Path(__file__).parent.parent / "fixtures/data/ths_loader/dataset"
    loader = THSLoader(dataset_dir=dataset_dir)
    return HazardCurves(loader=loader)

figures_dir = Path(__file__).parent.parent / "fixtures/plot/hazard_curve"

@image_comparison(baseline_images=[str(figures_dir / 'hazard_curve_mean')], extensions=['png'], style='mpl20')
def test_plot_hazard_curve_single(hazard_curves):
    aggs = ["mean"]
    fig, ax = plt.subplots(1, 1)
    plot_hazard_curve(ax, hazard_curves, hazard_model, wlg, imt, vs30, aggs)
    
@image_comparison(baseline_images=[str(figures_dir / 'hazard_curve_even')], extensions=['png'], style='mpl20')
def test_plot_hazard_curve_even(hazard_curves):
    aggs = ["0.1", "0.2", "0.8", "0.9"]
    fig, ax = plt.subplots(1, 1)
    plot_hazard_curve(ax, hazard_curves, hazard_model, wlg, imt, vs30, aggs)

@image_comparison(baseline_images=[str(figures_dir / 'hazard_curve_odd')], extensions=['png'], style='mpl20')
def test_plot_hazard_curve_odd(hazard_curves):
    aggs = ["0.1", "0.2", "mean", "0.8", "0.9"]
    fig, ax = plt.subplots(1, 1)
    plot_hazard_curve(ax, hazard_curves, hazard_model, wlg, imt, vs30, aggs)


imts = ["PGA", "SA(0.5)", "SA(1.5)", "SA(3.0)"]
poe = 0.1
inv_time = 50.0
@image_comparison(baseline_images=[str(figures_dir / 'uhs_curve_mean')], extensions=['png'], style='mpl20')
def test_plot_uhs_curve_single(hazard_curves):
    aggs = ["mean"]
    fig, ax = plt.subplots(1, 1)
    plot_uhs(ax, hazard_curves, hazard_model, wlg, imts, poe, inv_time, vs30, aggs)
    
@image_comparison(baseline_images=[str(figures_dir / 'uhs_curve_even')], extensions=['png'], style='mpl20')
def test_plot_uhs_curve_even(hazard_curves):
    aggs = ["0.1", "0.2", "0.8", "0.9"]
    fig, ax = plt.subplots(1, 1)
    plot_uhs(ax, hazard_curves, hazard_model, wlg, imts, poe, inv_time, vs30, aggs)

@image_comparison(baseline_images=[str(figures_dir / 'uhs_curve_odd')], extensions=['png'], style='mpl20')
def test_plot_uhs_curve_odd(hazard_curves):
    aggs = ["0.1", "0.2", "mean", "0.8", "0.9"]
    fig, ax = plt.subplots(1, 1)
    plot_uhs(ax, hazard_curves, hazard_model, wlg, imts, poe, inv_time, vs30, aggs)