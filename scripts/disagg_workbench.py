import csv
from dis import dis
import io
import itertools
from collections import namedtuple
from zipfile import ZipFile

import numpy as np
import pandas as pd
from nzshm_common.location.code_location import CodedLocation

INV_TIME = 1.0

def disagg_df(rlz_names, dimensions='MDET'):

    dim_mapping = {'M':'mag', 'D':'dist', 'E':'eps', 'T':'trt'}
    d = {}
    d['M'] = np.arange(5.25, 10.0, 0.5)
    d['D'] = np.arange(5, 550, 10)
    d['E'] = np.arange(-3,4,2)
    d['T'] = ['Active Shallow Crust', 'Subduction Interface', 'Subduction Intraslab']

    total_len = 0
    iterate = []
    columns = []
    for dim in dimensions:
        total_len += len(d[dim])
        columns.append(dim_mapping[dim])
        iterate.append(d[dim])
    index = range(total_len)
    disaggs = pd.DataFrame(columns=columns, index=index)
    columns += rlz_names
    
    for i, (bins) in enumerate(itertools.product(*iterate)):
        for j,dim in enumerate(dimensions):
            if dim=='M':
                disaggs.loc[i,'mag'] = f'{bins[j]:0.3}'
            elif dim=='D':
                disaggs.loc[i, 'dist'] = f'{int(bins[j])}'
            elif dim=='E':
                disaggs.loc[i, 'eps'] = f'{int(bins[j])}'
            elif dim=='T':
                disaggs.loc[i, 'trt'] = bins[j]
        
        for rlz in rlz_names:
            disaggs.loc[i, rlz] = 0

    return disaggs

def get_location(header):
    """
    get the location from the disagg csv
    this is terrible and hacky and only temporory until disagg data is stored by THS
    """

    info = header[-1]
    start_lon = info.index('lon=') + 4
    tail = info[start_lon:]
    try:
        end_lon = tail.index(',')
        lon = tail[:end_lon]
    except:
        lon = tail[:]

    start_lat = info.index('lat=') + 4
    tail = info[start_lat:]
    try:
        end_lat = tail.index(',')
        lat = tail[:end_lat]
    except:
        lat = tail[:]

    location = CodedLocation(float(lat), float(lon), 0.001).code

    return location


def get_disagg(csv_archive, dimensions='MDET'):
    """
    get the disagg data from the csv archive
    this is terrible and hacky and only temporory until disagg data is stored by THS
    assuming only 1 location and 1 imt
    """

    disagg_flags = []
    ndim = len(dimensions)
    if 'M' in dimensions:
        disagg_flags.append('Mag')
    if 'D' in dimensions:
        disagg_flags.append('Dist')
    if 'T' in dimensions:
        disagg_flags.append('TRT')
    if 'E' in dimensions:
        disagg_flags.append('Eps')
    disagg_filename = '_'.join(disagg_flags) + '-0_1.csv'
    print(f'reading {disagg_filename}')

    with ZipFile(csv_archive) as zipf:
        with io.TextIOWrapper(zipf.open(disagg_filename), encoding="utf-8") as mag_dist_TRT_file:
            disagg_reader = csv.reader(mag_dist_TRT_file)
            header0 = next(disagg_reader)
            location = get_location(header0)

            header = next(disagg_reader)
            DisaggData = namedtuple("DisaggData", header, rename=True)
            rlz_names = header[(ndim+2):]
            disaggs = disagg_df(rlz_names,dimensions=dimensions)

            for row in disagg_reader:
                disagg_data = DisaggData(*row)
                ind = pd.Series(disaggs.index)
                ind[:] = True
                imt = disagg_data.imt
                if 'mag' in disagg_data._fields:
                    mag = f'{float(disagg_data.mag):0.3}'
                    ind = ind & (disaggs['mag'].isin([mag]))
                if 'dist' in disagg_data._fields:
                    dist = f'{int(float(disagg_data.dist))}'
                    ind = ind & (disaggs['dist'].isin([dist])) 
                if 'trt' in disagg_data._fields:
                    trt = disagg_data.trt
                    ind = ind & (disaggs['trt'].isin([trt]))
                if 'eps' in disagg_data._fields:
                    eps = f'{int(float(disagg_data.eps))}'
                    ind = ind & (disaggs['eps'].isin([eps]))
                if not any(ind):
                    raise Exception(f'no index found for {csv_archive} row: {row}')
                disaggs.loc[ind, rlz_names] = list(map(float, row[(ndim+2):]))

    return disaggs, rlz_names

def prob_to_rate(prob,rlz_names):

    rate = prob.copy()
    rate.loc[:,rlz_names] = -np.log(1 - prob.loc[:,rlz_names]) / INV_TIME
    return rate


def rate_to_prob(rate,rlz_names):

    prob = rate.copy()
    prob.loc[:,rlz_names] = 1.0 - np.exp(-INV_TIME * rate)
    return prob


#============================================================================================================================================

disagg_archive = '/home/chrisdc/Downloads/openquake_csv_archive-T3BlbnF1YWtlSGF6YXJkVGFzazoxMjgyNjY=.zip'
disagg_mdet, rlz_names = get_disagg(disagg_archive)
disagg_t, rlz_names = get_disagg(disagg_archive,dimensions='T')
disagg_md, rlz_names = get_disagg(disagg_archive,dimensions='MD')
disagg_mdt, rlz_names = get_disagg(disagg_archive,dimensions='MDT')

disagg_mdet_rate = prob_to_rate(disagg_mdet, rlz_names)
disagg_t_rate = prob_to_rate(disagg_t, rlz_names)
disagg_md_rate = prob_to_rate(disagg_md, rlz_names)
disagg_mdt_rate = prob_to_rate(disagg_mdt, rlz_names)

# raw sum
for trt in set(disagg_mdet['trt']):
    print(trt)
    print('TRT only')
    print(disagg_t.loc[disagg_t['trt'] == trt,rlz_names])
    print('sum of MDET')
    print(disagg_mdet.loc[disagg_mdet['trt'] == trt,rlz_names].sum())
    print('diff')
    print(disagg_t.loc[disagg_t['trt'] == trt,rlz_names] - disagg_mdet.loc[disagg_mdet['trt'] == trt,rlz_names].sum())
    
# convert to rate
for trt in set(disagg_mdet['trt']):
    print(trt)
    print('TRT only')
    print(disagg_t.loc[disagg_t['trt'] == trt,rlz_names])
    print('sum of MDET')
    foo = rate_to_prob(disagg_mdet_rate.loc[disagg_mdet_rate['trt'] == trt,rlz_names].sum(), rlz_names)
    print(foo)
    print('diff')
    print(disagg_t.loc[disagg_t['trt'] == trt,rlz_names] - foo.loc[:,rlz_names])

