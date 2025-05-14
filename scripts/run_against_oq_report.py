import csv
import sys
import itertools
import nzshm_hazlab.disagg_plotting_functions as dpf

from pathlib import Path
from typing import List, Dict, Tuple, Iterable, NamedTuple, Optional

import markdown
import pandas as pd
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
import xarray as xr

from nzshm_common.location.code_location import CodedLocation
from nzshm_common.location.location import location_by_id, LOCATION_LISTS
from nzshm_common.grids import load_grid
from nzshm_hazlab.store.curves import get_hazard

from nzshm_hazlab.map_plotting_functions import get_poe_grid
from nzshm_hazlab.map_plotting_functions import plot_hazard_diff_map


PLOT_WIDTH = 12/2
PLOT_HEIGHT = 8.625/2
fonts_axis_label = 14 
fonts_title = 12

xlim = [1e-2,5]
# xlim = [1e-2,5]
xlim_res = [1e-4,5]
ylim = [1e-6,1e-2]
# ylim = [1e-6, 1e-2]
# ylim_res = [-1, 1]
ylim_res = [0.8, 1.1]

DEFAULT_RESOLUTION = 0.001

def get_locations(locations: Iterable[str], resolution: float = DEFAULT_RESOLUTION) -> List[CodedLocation]:
    """
    Get the coded locations from a list of identifiers.

    Identifiers can be any combination of:
        - a location string (latitude~longitude)
        - location list (key in nzhsm_common.location.location.LOCATION_LISTS)
        - location code (e.g. "WLG")
        - grid name in nzshm_common.grids.region_grid.RegionGrid
        - csv file with at least a column headed "lat" and a column headed "lon" (any other columns will be ignored)

    Parameters:
        locations: a list of location identifiers
        resolution: the resolution used by CodedLocation

    Returns:
        coded_locations: a list of coded locations
    """
    coded_locations: List[CodedLocation] = []
    for loc_id in locations:
        location_id = str(loc_id)
        if '~' in location_id:
            lat, lon = location_id.split('~')
            coded_locations.append(CodedLocation(float(lat), float(lon), resolution))
        elif location_by_id(location_id):
            coded_locations.append(CodedLocation(*_lat_lon(location_id), resolution))  # type: ignore
        elif LOCATION_LISTS.get(location_id):
            location_ids = LOCATION_LISTS[location_id]["locations"]
            coded_locations += [CodedLocation(*_lat_lon(_id), resolution) for _id in location_ids]  # type: ignore
        else:
            try:
                coded_locations += [CodedLocation(*loc, resolution) for loc in load_grid(location_id)]  # type: ignore
            except KeyError:
                msg = "location {} is not a valid location identifier".format(location_id)
                raise KeyError(msg)

    return coded_locations


class LatLon(NamedTuple):
    """
    A lightweight type for `(latitude, longitude)` float pairs.

    This is a named tuple with latitude and longitude fields.

    Examples:
        ```py
        >>> wlg = LatLon(-41.3, 174.78)
        >>> wlg
        LatLon(latitude=-41.3, longitude=174.78)
        >>> wlg.latitude
        -41.3
        >>> wlg[0]
        -41.3
        ```
    """

    latitude: float
    longitude: float


def _lat_lon(_id) -> Optional[LatLon]:
    loc = location_by_id(_id)
    if loc:
        return LatLon(loc['latitude'], loc['longitude'])
    return None


def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

def read_csv(csv_path, locations: List[CodedLocation]) -> Tuple[npt.NDArray, Dict[CodedLocation, npt.NDArray]]:
    res = locations[0].resolution
    hazard_OQ = dict()
    with open(csv_path,'r') as csvfile:
        reader = csv.reader(csvfile)
        junk = next(reader)
        header = next(reader)
        levels_OQ = np.array([float(l[4:]) for l in header[3:]])
        for row in reader:
            longitude = float(row[0])
            latitude = float(row[1])
            location = CodedLocation(lat=latitude, lon=longitude, resolution=res)
            if location in locations:
                hazard_OQ[location] = np.array(list(map(float,row[3:]) ))
    return levels_OQ, hazard_OQ

def load_oq_hazard(oq_output_path, locations: List[CodedLocation], imt, aggs):
    DTYPE = {'lat':'str', 'lon':'str', 'imt':'str', 'agg':'str', 'level':'str', 'apoe':'str'}
    index = range(len(locations) * 1 * len(aggs))
    hazard_curves = pd.DataFrame({c: pd.Series(dtype=t) for c, t in DTYPE.items()}, index=index)

    ind = 0
    for agg in aggs:
        oq_hazard_filepath = get_oq_filepath(oq_output_path, agg, imt)
        levels, hazard = read_csv(oq_hazard_filepath, locations)

        for location, values in hazard.items():
            lat, lon = location.downsample(0.001).code.split('~')
            hazard_curves.loc[ind,'lat'] = lat
            hazard_curves.loc[ind,'lon'] = lon
            hazard_curves.loc[ind,'imt'] = imt
            hazard_curves.loc[ind,'agg'] = agg
            hazard_curves.loc[ind,'level'] = levels
            hazard_curves.loc[ind,'apoe'] = values
            ind += 1

    return hazard_curves

def load_ths_hazard(model_id, locations: List[CodedLocation], vs30, imt, aggs):
    return get_hazard(model_id, vs30, locations, [imt], aggs)

def get_lat_lon(location: CodedLocation):
    return location.downsample(0.001).code.split('~')

def plot_hcurves(fig, ax, ths_hazard, oq_hazard, imt, aggs, location: CodedLocation, labels=None, legend=False):
    
    color_oq = 'tab:blue'
    color_ths = 'tab:orange'

    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')
    # ax.plot(oq_hazard['levels'], oq_hazard['mean'], lw=7, color=color_oq, label='OpenQuake')
    # breakpoint()
    lat, lon = get_lat_lon(location)
    ths_hazard = ths_hazard[(ths_hazard['lat'] == lat) & (ths_hazard['lon'] == lon) & (ths_hazard['imt'] == imt)]
    oq_hazard = oq_hazard[(oq_hazard['lat'] == lat) & (oq_hazard['lon'] == lon) & (oq_hazard['imt'] == imt)]
    for i, agg in enumerate(aggs):
        ths_hazard_tmp = ths_hazard[ths_hazard['agg'] == agg]
        oq_hazard_tmp = oq_hazard[oq_hazard['agg'] == agg]
        ths_levels = ths_hazard_tmp.iloc[0]['level']
        ths_values = ths_hazard_tmp.iloc[0]['apoe']
        oq_levels = oq_hazard_tmp.iloc[0]['level']
        oq_values = oq_hazard_tmp.iloc[0]['apoe']
        if i == 0:
            ax.plot(ths_levels, ths_values, lw=1, color=color_ths, label='THP')
            ax.plot(oq_levels, oq_values, lw=2, linestyle='--', color=color_oq, label='OQ')
        else:
            ax.plot(ths_levels, ths_values, lw=1, color=color_ths)
            ax.plot(oq_levels, oq_values, lw=2, linestyle='--', color=color_oq)

    inv_time = 50.0
    for poe in [0.02, 0.1]:
        rp = -inv_time/np.log(1-poe)
        text = f'{poe*100:.0f}% in {inv_time:.0f} years (1/{rp:.0f})'
        ax.plot(xlim,[1/rp]*2,ls='--',color='dimgray',zorder=-1)
        ax.annotate(text, [xlim[0],1/rp], ha='left',va='bottom', fontsize=8)
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

def plot_hcurves_2(fig, ax, ths_hazard, oq_hazard_10k, oq_hazard_100k, imt, aggs, location: CodedLocation):
    
    color_oq_10k = 'tab:blue'
    color_oq_100k = 'tab:green'
    color_ths = 'tab:orange'

    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')
    # ax.plot(oq_hazard['levels'], oq_hazard['mean'], lw=7, color=color_oq, label='OpenQuake')
    # breakpoint()
    lat, lon = get_lat_lon(location)
    ths_hazard = ths_hazard[(ths_hazard['lat'] == lat) & (ths_hazard['lon'] == lon) & (ths_hazard['imt'] == imt)]
    oq_hazard_10k = oq_hazard_10k[(oq_hazard_10k['lat'] == lat) & (oq_hazard_10k['lon'] == lon) & (oq_hazard_10k['imt'] == imt)]
    oq_hazard_100k = oq_hazard_100k[(oq_hazard_100k['lat'] == lat) & (oq_hazard_100k['lon'] == lon) & (oq_hazard_100k['imt'] == imt)]
    for i, agg in enumerate(aggs):
        ths_hazard_tmp = ths_hazard[ths_hazard['agg'] == agg]
        oq_hazard_tmp_10k = oq_hazard_10k[oq_hazard_10k['agg'] == agg]
        oq_hazard_tmp_100k = oq_hazard_100k[oq_hazard_100k['agg'] == agg]
        ths_levels = ths_hazard_tmp.iloc[0]['level']
        ths_values = ths_hazard_tmp.iloc[0]['apoe']
        oq_levels_10k = oq_hazard_tmp_10k.iloc[0]['level']
        oq_values_10k = oq_hazard_tmp_10k.iloc[0]['apoe']
        oq_levels_100k = oq_hazard_tmp_100k.iloc[0]['level']
        oq_values_100k = oq_hazard_tmp_100k.iloc[0]['apoe']
        if i == 0:
            ax.plot(ths_levels, ths_values, lw=1, color=color_ths, label='NZ NSHM 2022')
            ax.plot(oq_levels_10k, oq_values_10k, lw=2, linestyle='--', color=color_oq_10k, label='10k samples')
            ax.plot(oq_levels_100k, oq_values_100k, lw=2, linestyle='--', color=color_oq_100k, label='100k samples')
        else:
            ax.plot(ths_levels, ths_values, lw=1, color=color_ths)
            ax.plot(oq_levels_10k, oq_values_10k, lw=2, linestyle='--', color=color_oq_10k)
            ax.plot(oq_levels_100k, oq_values_100k, lw=2, linestyle='--', color=color_oq_100k)

    inv_time = 50.0
    for poe in [0.02, 0.1]:
        rp = -inv_time/np.log(1-poe)
        text = f'{poe*100:.0f}% in {inv_time:.0f} years (1/{rp:.0f})'
        ax.plot(xlim,[1/rp]*2,ls='--',color='dimgray',zorder=-1)
        ax.annotate(text, [xlim[0],1/rp], ha='left',va='bottom', fontsize=8)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.grid(color='lightgray')

    ax.legend(handlelength=5)

    ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
    ax.set_ylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)

    # ax.set_title(f'{location_name}', fontsize=fonts_title, loc='left')


def calculate_resduals(oq_hazard, ths_hazard, imt, agg, location: CodedLocation):
    lat, lon = get_lat_lon(location)
    ths_hazard = ths_hazard[(ths_hazard['lat'] == lat) & (ths_hazard['lon'] == lon) & (ths_hazard['imt'] == imt)]
    oq_hazard = oq_hazard[(oq_hazard['lat'] == lat) & (oq_hazard['lon'] == lon) & (oq_hazard['imt'] == imt)]
    ths_hazard_tmp = ths_hazard[oq_hazard['agg'] == agg]
    oq_hazard_tmp = oq_hazard[oq_hazard['agg'] == agg]
    ths_values = ths_hazard_tmp.iloc[0]['apoe']
    oq_values = oq_hazard_tmp.iloc[0]['apoe']
    levels = ths_hazard_tmp.iloc[0]['level']
    residuals = ths_values - oq_values
    residuals_rel = residuals/ths_values

    return levels, residuals, residuals_rel


def get_all_residuals(oq_hazard, ths_hazard, agg, location_ids):
   pass 
    # levels = []
    # residuals = []
    

def plot_residuals(fig, ax, oq_hazard, ths_hazard, imt, aggs, location):

    for agg in aggs:
        levels, residuals, residuals_rel = calculate_resduals(oq_hazard, ths_hazard, imt, agg, location)
        ax[0].plot(levels, residuals, linestyle='none', marker='o', markersize = 7, label=agg)
        ax[1].plot(levels, residuals_rel, linestyle='none', marker='o', markersize = 7, label=agg)
    
    ax[0].set_xscale('log')
    ax[1].set_xscale('log')
    ax[0].set_xlim(xlim)
    ax[1].set_xlim(xlim)
    ax[0].set_ylim([-0.0002, 0.0002])
    # ax[1].set_ylim([-0.1, 0.1])
    ax[1].set_ylim([-0.01, 0.01])
    ax[0].legend()
    ax[0].set_ylabel('apoe residual')
    ax[1].set_ylabel('apoe relative residual')


def make_seed2seed_curve_report(location_ids, nrlz, seeds, imts, aggs, oq_output_dir, report_filepath, style):

    report_dir = report_filepath.parent
    fig_dir = report_dir / "figs"
    fig_dir.mkdir(exist_ok=True)

    md_str = ''
    oq_output_path_0 = oq_output_dir / "seeds" / f"s{seeds[0]}" / f"rlz_{nrlz:_}" / "site37" / "vs30_750"

    for location_id in location_ids:
        loc = location_by_id(location_id)
        loc = {'name': location_id} if not loc else loc
        location = get_locations([location_id])[0]
        lat, lon = get_lat_lon(location)
        for agg in aggs:
            for imt in imts:
                ths_hazard = load_ths_hazard(model_id, [location], 750, imt, aggs)
                ths_hazard = (
                        ths_hazard[
                            (ths_hazard['lat'] == lat) &
                            (ths_hazard['lon'] == lon) &
                            (ths_hazard['imt'] == imt) &
                            (ths_hazard['agg'] == agg)
                        ]
                    )
                fig, ax = plt.subplots()
                print(f"working on {imt=}")
                print(f"working on {location_id=}")
                # oq_output_path = oq_output_dir / "seeds" / f"s{seeds[0]}" / f"rlz_{nrlz:_}" / "site37" / "vs30_750"
                # oq_hazard_0 = load_oq_hazard(oq_output_path, [location], imt, [agg])
                # hazard_0 = (
                #     oq_hazard_0[
                #         (oq_hazard_0['lat'] == lat) &
                #         (oq_hazard_0['lon'] == lon) &
                #         (oq_hazard_0['imt'] == imt) &
                #         (oq_hazard_0['agg'] == agg)
                #     ]
                # )

                for seed in seeds:
                    oq_output_path = oq_output_dir / "seeds" / f"s{seed}" / f"rlz_{nrlz:_}" / "site37" / "vs30_750"
                    oq_hazard = load_oq_hazard(oq_output_path, [location], imt, [agg])
                    hazard = (
                        oq_hazard[
                            (oq_hazard['lat'] == lat) &
                            (oq_hazard['lon'] == lon) &
                            (oq_hazard['imt'] == imt) &
                            (oq_hazard['agg'] == agg)
                        ]
                    )
                    x = hazard.iloc[0]['level']
                    if style == 'ratio':
                        y = ths_hazard.iloc[0]['apoe'] / hazard.iloc[0]['apoe']
                    elif style == 'diff':
                        y = abs(ths_hazard.iloc[0]['apoe'] - hazard.iloc[0]['apoe'])
                    elif style == 'stack':
                        y = hazard.iloc[0]['apoe']
                    ax.plot(x, y)
                if style == 'stack':
                    ax.plot(x, ths_hazard.iloc[0]['apoe'], color='k', linestyle='--')

                title = f"{location_id} {imt} {agg}"
                if style == 'ratio':
                    fig_name = f'hazardcurve_s2s_ratio_{location_id}_{imt}_{agg}.png'
                elif style == 'diff':
                    fig_name = f'hazardcurve_s2s_diff_{location_id}_{imt}_{agg}.png'
                elif style == 'stack':
                    fig_name = f'hazardcurve_s2s_stack_{location_id}_{imt}_{agg}.png'
                fig_filepath = fig_dir / fig_name


                ax.set_xlabel(f'Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
                ax.set_ylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)
                ax.set_xscale('log')
                ax.set_yscale('log')
                # ax.set_xlim(xlim)
                # ax.set_ylim(-0.1, 0.1)
                ax.set_title(title)
                ax.grid(color='lightgray')
                fig.savefig(fig_filepath)
                plt.close(fig)
                md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"

    md_str += '\n\n'
    write_report(md_str, report_filepath)


def make_seed_curve_report(location_ids, nrlz, seeds, imts, aggs, oq_output_dir, report_filepath):

    report_dir = report_filepath.parent
    fig_dir = report_dir / "figs"
    fig_dir.mkdir(exist_ok=True)

    md_str = ''
    oq_output_path_0 = oq_output_dir / "seeds" / f"s{seeds[0]}" / f"rlz_{nrlz:_}" / "site37" / "vs30_750"

    for imt in imts:
        print(f"working on {imt=}")
        for location_id in location_ids:
            print(f"working on {location_id=}")
            loc = location_by_id(location_id)
            loc = {'name': location_id} if not loc else loc
            location = get_locations([location_id])[0]
            oq_hazard_0 = load_oq_hazard(oq_output_path_0, [location], imt, aggs)
            for seed in seeds[1:]:
                print(f"working on {seed=}")
                md_str += f'# imt={imt}, location={location_id}, seed={seed}\n'
                oq_output_path = oq_output_dir / "seeds" / f"s{seed}" / f"rlz_{nrlz:_}" / "site37" / "vs30_750"
                oq_hazard = load_oq_hazard(oq_output_path, [location], imt, aggs)
                fig, ax = plt.subplots()
                plot_hcurves(
                    fig, ax,
                    ths_hazard=oq_hazard_0,
                    oq_hazard=oq_hazard,
                    imt=imt,
                    aggs=aggs,
                    location=location,
                )
                ax.set_xlabel(f'Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
                ax.set_ylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)
                title = f'{loc["name"]} {imt}'
                ax.set_title(title, fontsize=fonts_title, loc='left')
                fig_name = f'hazardcurve_{imt}_{location_id}_s{seed}.png'
                fig_filepath = fig_dir / fig_name
                fig.savefig(fig_filepath)
                plt.close(fig)
                md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"

                fig, ax = plt.subplots(1, 2)
                fig_name = f'residuals_{imt}_{location_id}_s{seed}.png'
                fig_filepath = fig_dir / fig_name
                plot_residuals(fig, ax, oq_hazard, oq_hazard_0, imt, aggs, location) 
                fig.savefig(fig_filepath)
                plt.close(fig)
                # plt.show()
                md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"

                md_str += '\n\n'

        md_str += '\n\n'

    write_report(md_str, report_filepath)



def make_hazard_curve_report(location_ids, model_id, vs30s, imts, aggs, oq_output_dir, report_filepath):

    report_dir = report_filepath.parent

    fig_dir = report_dir / "figs"
    if not fig_dir.exists():
        fig_dir.mkdir()

    md_str = ''

    for vs30 in vs30s:
        md_str += f'# vs30={vs30}\n'
        for imt in imts:
            for c, location_id in enumerate(location_ids):

                if (loc:=location_by_id(location_id)):
                    oq_output_path = oq_output_dir / f"site36_{vs30}"
                else:
                    oq_output_path = oq_output_dir / f"site_0.1_{vs30}"
                    # oq_output_path = oq_output_dir / f"site4_{vs30}"
                    loc = {'name': location_id}

                location = get_locations([location_id])[0]
                ths_hazard = load_ths_hazard(model_id, [location], vs30, imt, aggs)
                oq_hazard = load_oq_hazard(oq_output_path, [location], imt, aggs)

                fig, ax = plt.subplots()
                plot_hcurves(
                    fig, ax,
                    ths_hazard=ths_hazard,
                    oq_hazard=oq_hazard,
                    imt=imt,
                    aggs=aggs,
                    location=location,
                )
                ax.set_xlabel(f'Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
                ax.set_ylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)
                title = f'{loc["name"]} {vs30} {imt}'
                ax.set_title(title, fontsize=fonts_title, loc='left')
                fig_name = f'hazardcurve_{vs30}_{imt}_{location_id}.png'
                fig_filepath = fig_dir / fig_name
                fig.savefig(fig_filepath)
                md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"

                fig, ax = plt.subplots(1, 2)
                fig_name = f'residuals_{vs30}_{imt}_{location_id}.png'
                fig_filepath = fig_dir / fig_name
                plot_residuals(fig, ax, oq_hazard, ths_hazard, imt, aggs, location) 
                # fig.savefig(fig_filepath)
                plt.show()
                md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"

                md_str += '\n\n'
                plt.close()

        md_str += '\n\n'

    write_report(md_str, report_filepath)


def make_hazard_curve_report_2(location_ids, model_id, vs30s, imts, aggs, report_filepath):

    oq_output_dir_10k = Path("/home/chrisdc/mnt/glacier/oqruns/full-model/output/rlz_10_000")
    oq_output_dir_100k = Path("/home/chrisdc/mnt/glacier/oqruns/full-model/output/rlz_100_000")

    report_dir = report_filepath.parent


    fig_dir = report_dir / "figs"
    if not fig_dir.exists():
        fig_dir.mkdir()

    md_str = ''
    site_str = "site36"

    for vs30 in vs30s:
        md_str += f'# vs30={vs30}\n'
        for imt in imts:
            for c, location_id in enumerate(location_ids):

                if (loc:=location_by_id(location_id)):
                    oq_output_path_10k = oq_output_dir_10k / f"{site_str}_{vs30}"
                    oq_output_path_100k = oq_output_dir_100k / f"{site_str}_{vs30}"
                else:
                    # oq_output_path = oq_output_dir / f"site_0.1_{vs30}"
                    oq_output_path_10k = oq_output_dir_10k / f"{site_str}_{vs30}"
                    oq_output_path_100k = oq_output_dir_100k / f"{site_str}_{vs30}"
                    loc = {'name': location_id}

                location = get_locations([location_id])[0]
                ths_hazard = load_ths_hazard(model_id, [location], vs30, imt, aggs)
                oq_hazard_10k = load_oq_hazard(oq_output_path_10k, [location], imt, aggs)
                oq_hazard_100k = load_oq_hazard(oq_output_path_100k, [location], imt, aggs)

                fig, ax = plt.subplots()
                plot_hcurves_2(
                    fig, ax,
                    ths_hazard=ths_hazard,
                    oq_hazard_10k=oq_hazard_10k,
                    oq_hazard_100k=oq_hazard_100k,
                    imt=imt,
                    aggs=aggs,
                    location=location,
                )
                ax.set_xlabel(f'Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
                ax.set_ylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)
                title = f'{loc["name"]} {vs30} {imt}'
                ax.set_title(title, fontsize=fonts_title, loc='left')
                fig_name = f'hazardcurve_{vs30}_{imt}_{location_id}.png'
                fig_filepath = fig_dir / fig_name
                fig.savefig(fig_filepath)
                md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"

                fig, ax = plt.subplots(1, 2)
                fig_name = f'residuals_{vs30}_{imt}_{location_id}.png'
                fig_filepath = fig_dir / fig_name
                plot_residuals(fig, ax, oq_hazard_10k, ths_hazard, imt, aggs, location) 
                fig.savefig(fig_filepath)
                # plt.show()
                md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"

                md_str += '\n\n'
                plt.close()

        md_str += '\n\n'

    write_report(md_str, report_filepath)


def get_oq_filepath(oq_output_path, agg, imt):
    print(oq_output_path)
    oq_id = sorted(Path(oq_output_path).glob("*csv"))[0].name.split('_')[-1][0:-4]
    if agg == 'mean':
        return Path(oq_output_path, f'hazard_curve-{agg}-{imt}_{oq_id}.csv')

    return Path(oq_output_path, f'quantile_curve-{agg}-{imt}_{oq_id}.csv')

def get_poe_grid_oq(model_id, vs30, imt, agg, poe, nrlz):

    # get the map from THS
    print(f"{model_id=}, {vs30=}, {imt=}, {agg=}, {poe=}")

    # get the map from OQ in same format as above
    oq_output_path = oq_output_dir / f"site_0.1_{vs30}"
    oq_hazard_filepath = get_oq_filepath(oq_output_path, agg, imt)
    hazard_oq = get_oq_grid(oq_hazard_filepath, poe)
    hazard_oq['lon'] = np.round(hazard_oq['lon'], decimals=1)
    return hazard_oq

def trim_poes(min_poe, max_poe, ground_accels, annual_poes):
    """
    Returns a copy of annual_poes with values removed that are below min_poe or above max_poe.
    Returns a copy of ground_accels with elements removed at the same indexes that were removed from annual_poes.
    :param min_poe: the minimum poe
    :param max_poe: the maximum poe
    :param ground_accels: ground accels
    :param annual_poes: annual poes
    :return: a filter copy of ground_accels, and a filtered copy of annual_poes
    """
    acc_result = []
    poe_result = []
    for a, p in zip(ground_accels, annual_poes):
        if min_poe <= p <= max_poe:
            acc_result.append(a)
            poe_result.append(p)
    return np.array(acc_result), np.array(poe_result)


def get_oq_grid(oq_hazard_filepath, poe):

    investigation_time = 50.0

    hazard = pd.read_csv(oq_hazard_filepath, header=1)
    lcols = [c for c in hazard.columns if 'poe-' in c]
    level =  np.array([float(c.split('-')[1]) for c in lcols])
    hazard['level'] = np.nan
    for ind, row in hazard.iterrows():
        apoe = row[lcols].to_numpy()
        level_t, apoe_t = trim_poes(1e-10, 0.632, level, apoe)
        return_period = -investigation_time / np.log(1 - poe)

        xp = np.flip(np.log(apoe_t))  # type: ignore
        yp = np.flip(np.log(level_t))  # type: ignore

        if not np.all(np.diff(xp) >= 0):  # raise is x_accel_levels not increasing or at least not dropping,
            raise ValueError('Poe values not monotonous.')

        hazard.loc[ind, 'level']  = np.exp(np.interp(np.log(1 / return_period), xp, yp))

    hazard = hazard.drop(labels=lcols + ['depth'], axis=1)
    hazard = hazard.pivot(index="lat", columns="lon")
    hazard = hazard.droplevel(0, axis=1)
    return xr.DataArray(data=hazard)


def make_hazard_map_report(model_id, vs30s, imts, aggs, oq_output_dir, diff_type, report_filepath):

    report_dir = report_filepath.parent

    fig_dir = report_dir / "figs"
    if not fig_dir.exists():
        fig_dir.mkdir()

    if diff_type == 'ratio':
        md_str = '# Hazard Ratio Maps\n'
        climits = [0.985, 1.015]
    else:
        md_str = '# Hazard Difference Maps\n'
        climits = None

    dpi = None # 100
    region = "165/180/-48/-34"
    plot_width = 6
    font_size = 5 
    font = f'{font_size}p'
    font_annot = f'{int(0.8*font_size)}p'


    for vs30, imt, agg, poe in itertools.product(vs30s, imts, aggs, poes):
        md_str += f"###vs30: {vs30}, IMT: {imt}, Aggregate: {agg}, PoE: {poe:0.0%} in 50 years\n"
        if diff_type == 'sub':
            legend_text = f'{imt} ({poe*100:.0f}% PoE in 50 years) - difference in g'
        elif diff_type == 'ratio':
            legend_text = f'{imt} ({poe*100:.0f}% PoE in 50 years) - ratio'
        fig_name = f'map_{diff_type}_{vs30}_{imt}_{agg}_{poe}.png'
        fig_filepath = fig_dir / fig_name

        filepath = Path()
        hazard_oq = get_poe_grid_oq(model_id, vs30, imt, agg, poe, oq_output_dir)
        hazard_thp = get_poe_grid(model_id, vs30, imt, agg, poe)
        fig = plot_hazard_diff_map(hazard_oq, hazard_thp, diff_type, dpi, climits, font, font_annot, plot_width, legend_text, region)
        fig.savefig(str(fig_filepath))
        # fig.sw()

        md_str += f"![fig_name]({Path(*fig_filepath.parts[-2:])})"

        md_str += '\n\n'
        # return hazard_oq, hazard_thp

    write_report(md_str, report_filepath)

def write_report(md_str, report_filepath):

    HEAD_HTML = '''
    <!DOCTYPE html>
    <html>
    <article class="markdown-body">
    '''

    TAIL_HTML = '''
    </article>
    </html>
    '''

    print(f"writing {report_filepath}")
    with report_filepath.open('w') as report_file:
        report_file.write(md_str)

    html_filepath = report_filepath.with_suffix('.html')
    html = markdown.markdown(md_str)
    html = HEAD_HTML + html + TAIL_HTML
    with html_filepath.open('w') as html_file:
        html_file.write(html)

    

def make_disaggregation_report(disagg_file):
    values, bins = load_disaggs_oq(disagg_file)
    fig = plt.figure()
    widths = [2,2,2]
    heights = [1,2]
    gs = fig.add_gridspec(2, 3, width_ratios=widths, height_ratios=heights, hspace=0.08, wspace=0.07)
    ax = gs.subplots()
    fig.set_size_inches(12,5)    
    fig.set_facecolor('white')
    dpf.plot_mag_dist_trt_2d_v2(fig, ax, values, bins, None, None)
    plt.show()




def load_disaggs_oq(disagg_file):
    disagg = pd.read_csv(disagg_file, header=1)
    df = disagg.drop(['imt', 'iml', 'poe'], axis=1)
    values = df['mean'].to_numpy()
    trt = df['trt'].unique()
    mag = df['mag'].unique()
    dist = df['dist'].unique()
    eps = df['eps'].unique()
    shape = (len(eps), len(dist), len(mag), len(trt))
    values = values.reshape(shape, order='F')
    values = np.swapaxes(np.swapaxes(values, 0, 3), 0, 2)

    bins = np.array([ mag, dist, trt, eps ]) 

    return values, bins


    



# ███    ███  █████  ██ ███    ██ 
# ████  ████ ██   ██ ██ ████   ██ 
# ██ ████ ██ ███████ ██ ██ ██  ██ 
# ██  ██  ██ ██   ██ ██ ██  ██ ██ 
# ██      ██ ██   ██ ██ ██   ████ 
if __name__ == "__main__":
    make_hc_report = True
    make_hc2_report = False
    make_seed_report = False
    make_seed2seed_report = False
    make_map_report = False
    make_disagg_report = False
    # nrlz = 100_000
    # nrlz = 0
    # nrlz = int(sys.argv[1])False
    nrlz = 10_000
    # diff_type = sys.argv[2]
    # print(nrlz, diff_type)
    # model_id = 'NSHM_v1.0.4_OQv3.20.1'
    model_id = 'NSHM_v1.0.4'
    oq_output_dir = Path("/home/chrisdc/mnt/glacier/oqruns/full-model/output") / f"rlz_{nrlz:_}"
    report_dir = Path("/home/chrisdc/NSHM/oqruns/test_against_OQ_full") / f"rlz_{nrlz:_}"


    # | | | | __ _ ______ _ _ __ __| |  / ___|   _ _ ____   _____  ___ 
    # | |_| |/ _` |_  / _` | '__/ _` | | |  | | | | '__\ \ / / _ \/ __|
    # |  _  | (_| |/ / (_| | | | (_| | | |__| |_| | |   \ V /  __/\__ \
    # |_| |_|\__,_/___\__,_|_|  \__,_|  \____\__,_|_|    \_/ \___||___/

    if make_hc_report:
        # location_ids = ['AKL', 'WLG', 'KKE', 'WHO', 'DUD', 'CHC', "-38.700~178.100"]
        location_ids = ['AKL', 'WLG', 'KKE', 'WHO', 'DUD', 'CHC']
        # location_ids = ['-35.100~173.700']
        # location_ids = ["-38.700~178.100"]
        # location_ids = ["WLG", "-42.800~171.400"]
        # location_ids = ["CHC", "WLG", "-42.800~171.400"]
        # vs30s = [250, 400, 750]
        vs30s = [250]
        # imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.0)", "SA(2.0)", "SA(3.0)", "SA(5.0)", "SA(10.0)"]
        # imts = ["PGA", "SA(0.5)", "SA(1.0)", "SA(3.0)"]
        imts = ["PGA", "SA(0.5)", "SA(1.0)", "SA(3.0)"]
        aggs = ['mean', '0.01', '0.05', '0.1', '0.2', '0.5', '0.8', '0.9', '0.95', '0.99']


        if not report_dir.exists():
            report_dir.mkdir()
        report_filepath = report_dir / f"thp_oq_report_{nrlz:_}.md"
        make_hazard_curve_report(location_ids, model_id, vs30s, imts, aggs, oq_output_dir, report_filepath)

    if make_hc2_report:
        # location_ids = ['AKL', 'WLG', 'KKE', 'WHO', 'DUD', 'CHC', "-38.700~178.100"]
        location_ids = ['AKL', 'WLG', 'DUD', 'CHC']
        # location_ids = ['-35.100~173.700']
        # location_ids = ["-38.700~178.100"]
        # location_ids = ["WLG", "-42.800~171.400"]
        # location_ids = ["CHC", "WLG", "-42.800~171.400"]
        # vs30s = [250, 400, 750]
        vs30s = [750]
        # imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.0)", "SA(2.0)", "SA(3.0)", "SA(5.0)", "SA(10.0)"]
        # imts = ["PGA", "SA(0.5)", "SA(1.0)", "SA(3.0)"]
        imts = ["PGA", "SA(0.5)", "SA(1.0)", "SA(3.0)"]
        aggs = ['mean', '0.05', '0.95']


        if not report_dir.exists():
            report_dir.mkdir()
        report_filepath = report_dir / f"thp_oq_report_2.md"
        make_hazard_curve_report_2(location_ids, model_id, vs30s, imts, aggs, report_filepath)
    


    if make_seed_report:
        report_dir = Path("/home/chrisdc/NSHM/oqruns/test_against_OQ_full") / f"rlz_{nrlz:_}" / "seed_test"
        location_ids = ["AKL", "CHC", "WLG", "-42.800~171.400"]
        if not report_dir.exists():
            report_dir.mkdir()
        report_filepath = report_dir / f"seed_oq_report_{nrlz:_}.md"
        seeds = [1, 1000, 25, 45600, 666]
        oq_output_dir = Path("/home/chrisdc/mnt/glacier/oqruns/full-model/output")
        make_seed_curve_report(location_ids, nrlz, seeds, imts, aggs, oq_output_dir, report_filepath)

    if make_seed2seed_report:
        style = 'stack'
        report_dir = Path("/home/chrisdc/NSHM/oqruns/test_against_OQ_full") / f"rlz_{nrlz:_}" / "seed2seed_test"
        location_ids = ["AKL", "CHC", "WLG", "-42.800~171.400"]
        imts = ["PGA", "SA(0.5)", "SA(1.0)", "SA(3.0)"]
        aggs = ['mean', '0.05', '0.95']
        if not report_dir.exists():
            report_dir.mkdir()
        if style == 'ratio':
            report_filepath = report_dir / f"seed_oq_report_{nrlz:_}_ratio.md"
        elif style == 'diff':
            report_filepath = report_dir / f"seed_oq_report_{nrlz:_}_diff.md"
        elif style == 'stack':
            report_filepath = report_dir / f"seed_oq_report_{nrlz:_}_stack.md"
        seeds = [1, 1000, 25, 45600, 666]
        oq_output_dir = Path("/home/chrisdc/mnt/glacier/oqruns/full-model/output")
        make_seed2seed_curve_report(location_ids, nrlz, seeds, imts, aggs, oq_output_dir, report_filepath, style)


    #  __  __                 
    # |  \/  | __ _ _ __  ___ 
    # | |\/| |/ _` | '_ \/ __|
    # | |  | | (_| | |_) \__ \
    # |_|  |_|\__,_| .__/|___/
    #              |_|        
    if make_map_report:
        # diff_type = 'ratio' #'sub' 
        # diff_type = 'sub'
        for diff_type in ['sub', 'ratio']:
            report_filepath = report_dir / f"map_{diff_type}_{nrlz:_}.md"
            vs30s = [250, 400, 750]
            vs30s = [750]
            imts = ["PGA", "SA(0.5)", "SA(1.0)", "SA(3.0)"]
            # aggs = ['mean', '0.05', '0.1', '0.5', '0.9', '0.95']
            aggs = ['mean', '0.05', '0.95']
            # poes = [0.63, 0.39, 0.22, 0.18, 0.10, 0.05, 0.02]
            poes = [0.63, 0.18, 0.10, 0.02]
            # hazard_oq, hazard_thp = make_hazard_map_report(model_id, vs30s, imts, aggs, oq_output_dir, diff_type, report_filepath)
            make_hazard_map_report(model_id, vs30s, imts, aggs, oq_output_dir, diff_type, report_filepath)

    if make_disagg_report:
        disagg_file = oq_output_dir / 'disagg_WLG' / 'TRT_Mag_Dist_Eps-mean-0_26.csv'
        # values, bins = make_disaggregation_report(disagg_file)
        make_disaggregation_report(disagg_file)