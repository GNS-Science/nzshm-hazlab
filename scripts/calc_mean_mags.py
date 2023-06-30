import argparse
import csv
import itertools
from pathlib import Path

import numpy as np

from nzshm_common.location.location import LOCATIONS_BY_ID
# from oq_hazard_report.disagg_plotting_functions import prob_to_rate, AXIS_DIST, AXIS_MAG, MAGS, DISTS

AXIS_MAG = 0
AXIS_DIST = 1
AXIS_TRT = 2
AXIS_EPS = 3

MAGS = np.arange(5.25,10,.5)
DISTS = np.arange(5,550,10)

INV_TIME = 1.0

def prob_to_rate(prob):

    return -np.log(1 - prob) / INV_TIME

def assemble_disaggs(disagg):

    nmags = len(MAGS)
    ndists = len(DISTS)

    disaggs = np.empty((len(MAGS),len(DISTS)))
    for i, (imag, idist) in enumerate(itertools.product(range(nmags), range(ndists))):
        disaggs[imag,idist] = disagg[i]

    return disaggs

def calc_mean_mag(disagg_filepath):

    # convert to rate
    disagg = np.load(disagg_filepath)
    disagg = assemble_disaggs(disagg)
    disagg = prob_to_rate(disagg)

    # sum along distance axis
    disagg = np.sum(disagg, axis = AXIS_DIST)

    # normalize rates to sum to 1
    disagg = disagg/np.sum(disagg)

    # calculate weighted mean 
    return np.sum(MAGS * disagg)


def get_location(disagg_filepath):

    j0,j1,j2,j3,j4,j5, latlon, vs30, imt, poe, j6 = disagg_filepath.stem.split('_')
    lat,lon = latlon.split('~')
    location_key = [key for key,loc in LOCATIONS_BY_ID.items() if (loc['latitude'] == float(lat)) & (loc['longitude'] == float(lon))]
    if not location_key:
        site_name = location_key.replace('~',',')
        location_key = latlon.replace('~','')
    else:
        location_key = location_key[0]
        site_name = LOCATIONS_BY_ID[location_key]['name']

    return site_name, vs30, imt, poe

def main(disaggs, report_filepath):

    with open(report_filepath,'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['location','IMT','vs30','poe (% in 50 years)','mean magnitude'])
        for disagg_filepath in disaggs:
            site_name, vs30, imt, poe = get_location(disagg_filepath)
            mean_mag = calc_mean_mag(disagg_filepath)
            writer.writerow([site_name, imt, vs30, poe, mean_mag])        


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="calculate mean magnitudes from mag-dist disaggregations")
    parser.add_argument("disagg_dir", help="the path to the directory containing the disagg .npy files")
    args = parser.parse_args()

    disagg_dir = Path(args.disagg_dir)
    report_filepath = Path(disagg_dir, 'mean_mags.csv')

    disaggs = disagg_dir.glob('*.npy')
    main(disaggs, report_filepath)
    