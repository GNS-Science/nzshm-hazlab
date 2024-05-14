from zipfile import ZipFile
import itertools
import io
from collections import namedtuple
import csv
import numpy as np
import numpy.typing as npt

AXIS_MAG = 0
AXIS_DIST = 1
AXIS_TRT = 2
AXIS_EPS = 3

AXIS_NUMS = dict(
    mag = AXIS_MAG,
    dist = AXIS_DIST,
    trt = AXIS_TRT,
    eps = AXIS_EPS
)

INV_TIME = 1.0

def prob_to_rate(prob: npt.ArrayLike) -> npt.ArrayLike:

    return -np.log(1.0 - prob) / INV_TIME

def rate_to_prob(rate: npt.ArrayLike) -> npt.ArrayLike:

    return 1.0 - np.exp(-INV_TIME * rate)

def calc_mode_disagg(disagg, bins, dimensions):

    disagg = prob_to_rate(disagg)
    
    sum_dims = tuple(AXIS_NUMS[d] for d in AXIS_NUMS.keys() if d not in dimensions)
    keep_dims = tuple(d for d in AXIS_NUMS.keys() if d in dimensions)

    disagg = np.sum(disagg, axis=sum_dims)
    disagg = disagg / np.sum(disagg)
    
    mode_ind = np.where(disagg == disagg.max())
    mode = {}
    for i, dim in enumerate(keep_dims):
        mode[dim] = float(bins[AXIS_NUMS[dim]][mode_ind[i][0]])

    contribution = disagg.max()

    return mode, contribution


def calc_mean_disagg(disagg, bins):

    disagg = prob_to_rate(disagg)
    dist_mean = np.sum(np.sum(disagg, axis = (AXIS_MAG, AXIS_TRT, AXIS_EPS) ) / np.sum(disagg) * bins[AXIS_DIST])
    mag_mean = np.sum(np.sum(disagg, axis = (AXIS_DIST, AXIS_TRT, AXIS_EPS) ) / np.sum(disagg) * bins[AXIS_MAG])
    eps_mean = np.sum(np.sum(disagg, axis = (AXIS_MAG, AXIS_DIST, AXIS_TRT) ) / np.sum(disagg) * bins[AXIS_EPS])

    return dict(dist = dist_mean, mag = mag_mean, eps = eps_mean)


def meshgrid_disaggs(mags,dists,rates_int,rates_slab,rates_cru):

    umags = list(set(mags))
    umags.sort()
    udists = list(set(dists))
    udists.sort()

    nmags = len(umags)
    ndists = len(udists)
    

    Mags = np.empty((ndists,nmags))
    Dists = np.empty((ndists,nmags))
    Rates_int = np.empty((ndists,nmags))
    Rates_slab = np.empty((ndists,nmags))
    Rates_cru = np.empty((ndists,nmags))
    Rates_tot = np.empty((ndists,nmags))

    for col,mag in enumerate(umags):
        for row,dist in enumerate(udists):

            Mags[row,col] = mag
            Dists[row,col] = dist
            ind = (mags==mag) & (dists==dist)
            Rates_int[row,col] = rates_int[ind]
            Rates_cru[row,col] = rates_cru[ind]
            Rates_slab[row,col] = rates_slab[ind]
            Rates_tot[row,col] = rates_int[ind] + rates_cru[ind] + rates_slab[ind]

    return Mags, Dists, Rates_int, Rates_slab, Rates_cru, Rates_tot


def meshgrid_disaggs_v2(mags,dists,rates):

    umags = list(set(mags))
    umags.sort()
    udists = list(set(dists))
    udists.sort()

    nmags = len(umags)
    ndists = len(udists)
    

    Mags = np.empty((ndists,nmags))
    Dists = np.empty((ndists,nmags))
    Rates = np.empty((ndists,nmags))

    for col,mag in enumerate(umags):
        for row,dist in enumerate(udists):

            Mags[row,col] = mag
            Dists[row,col] = dist
            ind = (mags==mag) & (dists==dist)
            Rates[row,col] = rates[ind]
            
    return Mags, Dists, Rates



def get_disagg_trt(csv_archive):
    hazard = {}
    with ZipFile(csv_archive) as zipf:
        with io.TextIOWrapper(zipf.open('Mag_Dist_TRT-0_1.csv'), encoding="utf-8") as mag_dist_TRT_file:
            disagg_reader = csv.reader(mag_dist_TRT_file)
            junk = next(disagg_reader)
            header = next(disagg_reader)
            DisaggData = namedtuple("DisaggData", header, rename=True)
            for row in disagg_reader:
                disagg_data = DisaggData(*row)
                trt = disagg_data.trt
                prob = disagg_data.rlz0
                if not hazard.get(trt):
                    hazard[trt] = float(prob)
                else:
                    hazard[trt] += float(prob)

    return hazard

def get_disagg_MDT(csv_archive):

    with ZipFile(csv_archive) as zipf:
        with io.TextIOWrapper(zipf.open('Mag_Dist_TRT-0_1.csv'), encoding="utf-8") as mag_dist_TRT_file:
            disagg_reader = csv.reader(mag_dist_TRT_file)
            junk = next(disagg_reader)
            header = next(disagg_reader)
            DisaggData = namedtuple("DisaggData", header, rename=True)
            mags = []
            dists = []
            rates_slab = []
            rates_cru = []
            rates_int = []

            for row in disagg_reader:
                disagg_data = DisaggData(*row)

                mag = float(disagg_data.mag)
                dist = float(disagg_data.dist)
                rate = float(disagg_data.rlz0)
                trt = disagg_data.trt


                if trt == 'Active Shallow Crust':
                    mags.append(mag)
                    dists.append(dist)
                    rates_cru.append(rate)
                    # rates_slab.append(0.0)
                    # rates_int.append(0.0)
                elif trt == 'Subduction Interface':
                    rates_int.append(rate)
                    # rates_slab.append(0.0)
                    # rates_cru.append(0.0)
                elif trt == 'Subduction Intraslab':
                    rates_slab.append(rate)
                    # rates_int.append(0.0)
                    # rates_cru.append(0.0)

    mags = np.array(mags)
    dists = np.array(dists)
    rates_int = np.array(rates_int)
    rates_slab = np.array(rates_slab)
    rates_cru = np.array(rates_cru)

    return mags,dists,rates_int,rates_slab,rates_cru


def disagg_to_csv(disagg, bins, header, csv_filepath):

    disagg = disagg.flatten()
    disagg_pc = prob_to_rate(disagg)
    disagg_pc = disagg_pc / np.sum(disagg_pc) * 100.0
    with open(csv_filepath, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([header])
        writer.writerow(['magnitude','distance (km)','TRT','epsilon (sigma)','annual probability of exceedance', '% contribution to hazard'])
        for i, (mag, dist, trt, eps) in enumerate(itertools.product(*bins)):
            row = (f'{mag:0.1f}', f'{dist:0.0f}', trt, f'{eps:0.3f}', f'{disagg[i]:0.3e}', f'{disagg_pc[i]:0.3e}')
            writer.writerow(row)

