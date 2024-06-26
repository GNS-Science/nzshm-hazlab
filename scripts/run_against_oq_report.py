import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from nzshm_common.location.code_location import CodedLocation
from nzshm_common.location.location import location_by_id
from nzshm_hazlab.store.curves import get_hazard

PLOT_WIDTH = 12/2
PLOT_HEIGHT = 8.625/2
fonts_axis_label = 14 
fonts_title = 12

xlim = [1e-4,5]
xlim_res = [1e-4,5]
ylim = [1e-6,1]
# ylim_res = [-1, 1]
ylim_res = [0.8, 1.1]

def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

def read_csv(csv_path, location):
    lat, lon = (location.lat, location.lon)
    with open(csv_path,'r') as csvfile:
        reader = csv.reader(csvfile)
        junk = next(reader)
        header = next(reader)
        levels_OQ = np.array([float(l[4:]) for l in header[3:]])
        for row in reader:
            longitude = float(row[0])
            latitude = float(row[1])
            if (longitude==lon) & (latitude==lat):
                hazard_OQ = np.array(list(map(float,row[3:]) ))
    return levels_OQ, hazard_OQ

def load_oq_hazard(oq_output_path, location, imt, aggs):
    oq_id = sorted(Path(oq_output_path).glob("*csv"))[0].name.split('_')[-1][0:-4]
    oq_hazard = {}

    for agg in aggs:
        if agg == 'mean':
            oq_hazard_filepath = Path(oq_output_path, f'hazard_curve-{agg}-{imt}_{oq_id}.csv')
        else:
            oq_hazard_filepath = Path(oq_output_path, f'quantile_curve-{agg}-{imt}_{oq_id}.csv')
        levels, hazard = read_csv(oq_hazard_filepath, location)
        if 'levels' not in oq_hazard:
            oq_hazard['levels'] = levels
        oq_hazard[agg] = hazard
    return oq_hazard

def load_ths_hazard(model_id, location, vs30, imt, aggs):
    hazard_THS = get_hazard(model_id, vs30, [location], [imt], aggs)
    ths_hazard = {}
    for agg in aggs:
        if 'levels' not in ths_hazard:
            levels_THS = hazard_THS[hazard_THS['agg'] == agg]['level'].iloc[0]
            ths_hazard['levels'] = levels_THS
        ths_hazard[agg] = hazard_THS[hazard_THS['agg'] == agg]['apoe'].iloc[0]

    return ths_hazard

def plot_hcurves(fig, ax, ths_hazard, oq_hazard, aggs, location_name, labels=None, legend=False):

    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')
    # ax.plot(oq_hazard['levels'], oq_hazard['mean'], lw=7, color=color_oq, label='OpenQuake')
    # breakpoint()
    for i, agg in enumerate(aggs):
        if i == 0:
            ax.plot(ths_hazard['levels'], ths_hazard[agg], lw=1, color=color_ths, label='THP')
            ax.plot(oq_hazard['levels'], oq_hazard[agg], lw=2, linestyle='--', color=color_oq, label='OQ')
        else:
            ax.plot(ths_hazard['levels'], ths_hazard[agg], lw=1, color=color_ths)
            ax.plot(oq_hazard['levels'], oq_hazard[agg], lw=2, linestyle='--', color=color_oq)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.grid(color='lightgray')

    if legend:
        ax.legend(handlelength=5)

    if labels:
        ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
        ax.set_ylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)

    # ax.set_title(f'{location_name}', fontsize=fonts_title, loc='left')


def calculate_resduals(oq_hazard, ths_hazard, agg):
    levels = np.array([])
    residuals = np.array([])
    for location_id in oq_hazard.keys():
        levels = np.hstack((levels, oq_hazard[location_id]['levels']))
        residuals = np.hstack(
            (
                residuals,
                # (oq_hazard[location_id][agg] - ths_hazard[location_id][agg])/oq_hazard[location_id][agg] * 100.0
                (oq_hazard[location_id][agg] / ths_hazard[location_id][agg])
            )
        )

    return {'levels': levels, 'residuals': residuals}

def get_all_residuals(oq_hazard, ths_hazard, agg, location_ids):
   pass 
    # levels = []
    # residuals = []
    

def plot_residuals(fig, ax, levels, residuals, title, label, labels):

    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')

    ax.plot(levels, residuals, linestyle='none', marker='o', markersize = 7, label=label)
    if labels:
        ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
        ax.set_ylabel('APOE ratio [traditional / new]', fontsize=fonts_axis_label)
    ax.grid(color='lightgray')
    ax.set_title(title, fontsize=fonts_title, loc='left')

    ax.set_xscale('log')
    ax.set_xlim(xlim_res)
    ax.set_ylim(ylim_res)


# ███    ███  █████  ██ ███    ██ 
# ████  ████ ██   ██ ██ ████   ██ 
# ██ ████ ██ ███████ ██ ██ ██  ██ 
# ██  ██  ██ ██   ██ ██ ██  ██ ██ 
# ██      ██ ██   ██ ██ ██   ████ 

location_ids = ['AKL', 'WLG', 'KKE', 'WHO', 'DUD', 'CHC']
model_id = 'NSHM_v1.0.4'
# vs30s = [250, 400, 750]
vs30s = [250]
imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.0)", "SA(2.0)", "SA(3.0)", "SA(5.0)", "SA(10.0)"]
aggs = ['mean', '0.01', '0.05', '0.1', '0.2', '0.5', '0.8', '0.9', '0.95', '0.99']
color_oq = 'tab:blue'
color_ths = 'tab:orange'

nrlz = 100000
oq_output_dir = Path("/home/chrisdc/mnt/glacier/oqruns/full-model/output") / f"rlz_{nrlz:_}"

report_dir = Path("/home/chrisdc/NSHM/oqruns/test_against_OQ_full") / f"rlz_{nrlz:_}"
fig_dir = report_dir / "figs"
if not report_dir.exists():
    report_dir.mkdir()
if not fig_dir.exists():
    fig_dir.mkdir()
report_filepath = report_dir / f"thp_oq_report_{nrlz:_}.md"

md_str = ''

for vs30 in vs30s:
    md_str += f'# vs30={vs30}\n'
    oq_output_path = oq_output_dir / f"site36_{vs30}"
    for imt in imts:
        for c, location_id in enumerate(location_ids):
            fig, ax = plt.subplots()
            location = CodedLocation(*lat_lon(location_id), 0.001)
            ths_hazard = load_ths_hazard(model_id, location, vs30, imt, aggs)
            oq_hazard = load_oq_hazard(oq_output_path, location, imt, aggs)
            location_name = location_by_id(location_id)['name']

            plot_hcurves(
                fig, ax,
                ths_hazard=ths_hazard,
                oq_hazard=oq_hazard,
                aggs=aggs,
                location_name=location_name,
            )
            ax.set_xlabel(f'Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
            ax.set_ylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)
            title = f'{location_name} {vs30} {imt}'
            ax.set_title(title, fontsize=fonts_title, loc='left')
            fig_name = f'hazardcurve_{vs30}_{imt}_{location_id}.png'
            fig_filepath = fig_dir / fig_name
            fig.savefig(fig_filepath)
            md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"
    md_str += '\n'

print(f"writing {report_filepath}")
with report_filepath.open('w') as report_file:
    report_file.write(md_str)

