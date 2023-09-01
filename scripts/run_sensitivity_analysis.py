import itertools

from typing import List, Tuple, Dict
from math import copysign

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import toshi_hazard_store
from nzshm_common.location.location import location_by_id, LOCATION_LISTS
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid

from nzshm_hazlab.store.curves import get_hazard
from nzshm_hazlab.disagg_data_functions import prob_to_rate
from nzshm_hazlab.locations import get_locations

PLOT_WIDTH = 12
PLOT_HEIGHT = 6
LABEL_FONTSIZE = 9
TAG_FONTSIZE = 8
XLABEL_FONTSIZE = 12


def get_rate_at_imtl(hazard_data, locations, imt, imtl) -> pd.DataFrame:
    location_strs = [loc.code for loc in locations]
    col_name = f'{imt}_{imtl}'
    hazard_at_imtl = pd.DataFrame(index=location_strs, columns=[col_name])
    for loc in location_strs:
        lat, lon = loc.split('~')
        col = (
            (hazard_data['lat'] == lat) &
            (hazard_data['lon'] == lon) &
            (hazard_data['imt'] == imt) &
            (hazard_data['agg'] == 'mean')
        )
        levels = hazard_data.loc[col, 'level'].iloc[0]
        values = hazard_data.loc[col, 'apoe'].iloc[0]
        hazard_at_imtl.loc[loc, col_name] = prob_to_rate(values[np.where(levels == imtl)][0])

    return hazard_at_imtl

def load_data(hazard_model_groups, vs30, locations, imt) -> Dict[str,pd.DataFrame]:

    hazard_data = {}
    hazard_ids = [group['member_ids'] for group in hazard_model_groups]
    for hazard_id in itertools.chain(*hazard_ids):
        if (not hazard_id) or (hazard_id in hazard_data):
            continue
        print(f"loading HAZARD ID: {hazard_id}")
        hazard_data[hazard_id] = get_hazard(hazard_id, vs30, locations, [imt], ['mean'])
        if hazard_data[hazard_id].isnull().any().any():
            msg = f"hazard id {hazard_id} has a null value"
            raise Exception(msg)

        # hazard_data[hazard_id] = load_hazard_model(hazard_id, vs30, locations, imt, imtl)
    
    return hazard_data

def calculate_hazard_sens(hazard_data, hazard_data_full, hazard_model_groups, locations, imt, imtl, metric):
    hazard_sens = []
    for group in hazard_model_groups:
        hazard_sens.append(calculate_1_hazard_sens(hazard_data, hazard_data_full, group, locations, imt, imtl, metric))
    
    return hazard_sens

def calculate_1_hazard_sens(hazard_data, hazard_data_full, group, locations, imt, imtl, metric):
    # (A-B, C-B) where each entry in the tuple is a scaler
    member_ids = group['member_ids']
    hazard_a = get_rate_at_imtl(hazard_data[member_ids[0]], locations, imt, imtl)
    hazard_c = get_rate_at_imtl(hazard_data[member_ids[2]], locations, imt, imtl)
    if member_ids[1]:
        hazard_b = get_rate_at_imtl(hazard_data[member_ids[1]], locations, imt, imtl)
    else:
        hazard_b = (hazard_a + hazard_c)/2.0
    if metric.lower() == "ratio": 
        a_b = hazard_a / hazard_b
        c_b = hazard_c / hazard_b
    elif metric.lower() == "diff":
        a_b = hazard_a - hazard_b
        c_b = hazard_c - hazard_b
    elif metric.lower() == "rel_diff":
        a_b = (hazard_a - hazard_b) / hazard_b
        c_b = (hazard_c - hazard_b) / hazard_b
    elif metric.lower() == "rel_diff_full":
        hazard_full = get_rate_at_imtl(hazard_data_full, locations, imt, imtl)
        a_b = (hazard_a - hazard_b) / hazard_full # hazard_b
        c_b = (hazard_c - hazard_b) / hazard_full # hazard_b
    else:
        msg = f"metric {metric} is not supported. Must be 'ratio', 'diff', 'rel_diff', or 'rel_diff_full'"
        raise ValueError(msg)
    
    return a_b.mean().iloc[0], c_b.mean().iloc[0]



def plot_hazard_sens(hazard_sens, hazard_model_groups, ax, imt, imtl, metric, xlabels, ylabels, sup_title):

    y_pos = list(range(len(hazard_sens)))
    hi, low = [], []
    for group in hazard_sens:
        low.append(group[0])
        hi.append(group[1])

    ax.barh(y_pos, low, color='tab:red')
    ax.barh(y_pos, hi, color='tab:blue')

    if ylabels:
        labels = [group['name'] for group in hazard_model_groups]
    else:
        labels = ['']* len(hazard_model_groups)
    ax.set_yticks(y_pos, labels=labels, fontsize=LABEL_FONTSIZE)
    ax.invert_yaxis()
    if True:
        # x_low = min(low)
        # x_hi = max(hi)
        for i, group in enumerate(hazard_model_groups):
            # x_low = max(abs(low[i]), 0.1) * copysign(1.0, low[i])
            # x_hi = max(abs(hi[i]), 0.1) * copysign(1.0, hi[i])
            x_low = 0.01 * copysign(1.0, low[i])
            x_hi = 0.01 * copysign(1.0, hi[i])
            align_low = 'right' if x_low <=0 else 'left'
            align_hi = 'left' if x_hi >=0 else 'right'
            ax.text(x_low, i, group['member_names'][0], horizontalalignment=align_low, fontsize=TAG_FONTSIZE, fontweight='bold')
            ax.text(x_hi, i, group['member_names'][2], horizontalalignment=align_hi, fontsize=TAG_FONTSIZE, fontweight='bold')
    if metric == 'diff':
        label_str = f'Mean Hazard Rate Difference'
    elif metric == 'ratio':
        label_str = f'Mean Hazard Rate Ratio'
    elif metric == 'rel_diff':
        label_str = f'Mean Hazard Rate Relative Difference'
    elif metric == 'rel_diff_full':
        label_str = f'Mean Hazard Rate Relative Difference'
    if xlabels:
        ax.set_xlabel(label_str, fontsize=XLABEL_FONTSIZE)
    title = f"{imt} = {imtl}g"
    ax.set_title(title, fontsize=10)
    plt.suptitle(sup_title, fontsize=12)

if __name__ == "__main__":

    reload_data = True

    vs30 = 400
    # location_names = ["NZ", "NZ_0_1_NB_1_1_intersect_NZ_0_2_NB_1_1"]
    location_names = ["NZ_0_1_NB_1_1_intersect_NZ_0_2_NB_1_1"]
    location_names = ["WHO"]
    title = 'Franz Josef Hazard Sensitivity'
    imt = "PGA"
    imtls = [0.1, 0.5, 1.0]
    hazard_id_fullmodel = "NSHM_v1.0.4"
    hazard_model_groups = [ 
        dict(
            name='Crustal N-Scaling',
            member_names=['0.66','1.0','1.41'],
            member_ids = ["NSHM_v1.0.4_ST_cruNlo_iso", "NSHM_v1.0.4_ST_crubmid_iso", "NSHM_v1.0.4_ST_cruNhi_iso"],
        ),
        dict(
            name='H-K N-Scaling',
            member_names = ['0.42','1.0','1.58'],
            member_ids = ["NSHM_v1.0.4_ST_HikNlo_iso", "NSHM_v1.0.4_ST_HikNmed_iso", "NSHM_v1.0.4_ST_HikNhi_iso"],
        ),
        dict(
            name='H-K b value',
            member_names = ['1.241','1.097','0.95'],
            member_ids = ["NSHM_v1.0.4_ST_Hikbhi_iso", "NSHM_v1.0.4_ST_Hikbmid_iso", "NSHM_v1.0.4_ST_Hikblo_iso"],
        ),
        dict(
            name='Cru b value',
            member_names = ['1.089','0.959','0.823'],
            member_ids=["NSHM_v1.0.4_ST_crubhi_iso", "NSHM_v1.0.4_ST_crubmid_iso", "NSHM_v1.0.4_ST_crublo_iso"],
        ),
        dict(
            name='Cru Time Dependence',
            member_names = ['TI','','TD'],
            member_ids=["NSHM_v1.0.4_ST_crubmid_iso", None, "NSHM_v1.0.4_ST_TD_iso"],
        ),
        dict(
            name='Cru Def Model',
            member_names = ['geologic','','geodetic'],
            member_ids=["NSHM_v1.0.4_ST_crubmid_iso", None, "NSHM_v1.0.4_ST_geodetic_iso"],
        ),

    ]
    metric = "rel_diff_full" # "diff"

    locations = get_locations(location_names)
    if reload_data:
        hazard_data = load_data(hazard_model_groups, vs30, locations, imt)
        hazard_data_full = get_hazard(hazard_id_fullmodel, vs30, locations, [imt], ['mean'])
    
    fig, ax = plt.subplots(1,3)
    fig.set_size_inches(PLOT_WIDTH, PLOT_HEIGHT)
    for i, imtl in enumerate(imtls):
        ylabels = True if i==0 else False
        xlabels = True if i==1 else False
        hazard_sens = calculate_hazard_sens(hazard_data, hazard_data_full, hazard_model_groups, locations, imt, imtl, metric)
        plot_hazard_sens(hazard_sens, hazard_model_groups, ax[i], imt, imtl, metric, xlabels, ylabels, title)

    plt.show()