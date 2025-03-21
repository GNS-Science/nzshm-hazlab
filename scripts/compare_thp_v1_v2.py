from nzshm_common.location import get_locations
from nzshm_hazlab.store.curves_v4 import get_hazard as get_hazard_v4, ArrowFS
from nzshm_hazlab.plotting_functions import extract_hazard_curve
from nzshm_hazlab.store.curves import get_hazard
import matplotlib.pyplot as plt
from pathlib import Path

from nzshm_hazlab.locations import get_locations, lat_lon

PLOT_WIDTH = 12 
PLOT_HEIGHT = 12

def set_fig_properties(fig, title):
    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')
    fig.suptitle(title)

def set_axis_properties(axis, title):
    axis.set_title(title, fontsize=10)
    axis.grid(color='lightgray')  

resolution = 0.001
xlim = [1e-2,1e1]
ylim = [1e-8,1]

fig_dir = Path("/home/chrisdc/NSHM/oqresults/THP_v1_v2")
model_id_v1 = "NSHM_v1.0.4"
model_id_v2 = "NSHM_v1.0.4"
locations = ["srg_120", "DUD", "CHC", "AKL"]
ths_dir = Path("/home/chrisdc/mnt/glacier_data/toshi_hazard_store")
ths_agg_db = "AGG_v0.5"
imts = ["PGA", "SA(1.0)", "SA(3.0)", "SA(10.0)"]
aggs = ["mean", "0.01", "0.05", "0.1", "0.5", "0.9", "0.95", "0.99"]
vs30 = 275



fs_specs = dict(
    arrow_fs=ArrowFS.LOCAL,
    arrow_dir=str(ths_dir / ths_agg_db)
)
coded_locations = get_locations(locations)

hazard_v1 = get_hazard(model_id_v1, vs30, coded_locations, imts, aggs)
hazard_v2 = get_hazard_v4(model_id_v2, vs30, coded_locations, imts, aggs, fs_specs)
for location, coded_location in zip(locations, coded_locations):
    lat, lon = coded_location.code.split("~")
    for imt in imts:
        title = f"{location} {imt}"
        fig_hcurve, ax_hcurve = plt.subplots(3,3)
        set_fig_properties(fig_hcurve, title)

        fig_diff, ax_diff = plt.subplots(3,3)
        set_fig_properties(fig_diff, title + " abs(difference)")

        fig_reldiff, ax_reldiff = plt.subplots(3,3)
        set_fig_properties(fig_reldiff, title + " abs(rel. difference)")

        for k, agg in enumerate(aggs):
            levels_v1, values_v1 = extract_hazard_curve(hazard_v1, coded_location, imt, agg)
            levels_v2, values_v2 = extract_hazard_curve(hazard_v2, coded_location, imt, agg)
            i = k // 3
            j = k % 3

            title = agg
            ax_hcurve[i, j].plot(levels_v1, values_v1)
            ax_hcurve[i, j].plot(levels_v2, values_v2)
            ax_hcurve[i, j].set_xscale('log')
            ax_hcurve[i, j].set_yscale('log')
            set_axis_properties(ax_hcurve[i, j], title)

            diff = abs(values_v1-values_v2)
            title = f"{agg}, max:  {max(diff):.2e}"
            ax_diff[i, j].plot(levels_v1, diff)
            ax_diff[i, j].set_xscale('log')
            ax_diff[i, j].set_yscale('log')
            set_axis_properties(ax_diff[i, j], title)

            rel_diff = diff / values_v1
            title = f"{agg}, max: {max(rel_diff):.2e}"
            ax_reldiff[i, j].plot(levels_v1, rel_diff)
            ax_reldiff[i, j].set_xscale('log')
            ax_reldiff[i, j].set_yscale('log')
            set_axis_properties(ax_reldiff[i, j], title)

        hcurve_filepath = fig_dir / f"hcurve_v1v2_{location}_{imt}.png"
        diff_filepath = fig_dir / f"diff_v1v2_{location}_{imt}.png"
        reldiff_filepath = fig_dir / f"reldiff_v1v2_{location}_{imt}.png"
        fig_hcurve.savefig(hcurve_filepath)
        fig_diff.savefig(diff_filepath)
        fig_reldiff.savefig(reldiff_filepath)
        plt.close(fig_hcurve)
        plt.close(fig_diff)
        plt.close(fig_reldiff)

