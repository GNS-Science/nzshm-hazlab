import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from nzshm_common.location.code_location import CodedLocation
from nzshm_common.location.location import location_by_id
from nzshm_hazlab.store.curves import get_hazard

INV_TIME = 1.0

def read_csv(csv_path, location):
    lat, lon = (location.lat, location.lon)
    with open(csv_path,'r') as csvfile:
        reader = csv.reader(csvfile)
        junk = next(reader)
        header = next(reader)
        levels_OQ = np.array([float(l[4:]) for l in header[4:]])
        for row in reader:
            longitude = float(row[1])
            latitude = float(row[2])
            if (longitude==lon) & (latitude==lat):
                hazard_OQ = np.array(list(map(float,row[4:]) ))

    return levels_OQ, hazard_OQ

def load_oq_hazard(oq_output_path, location):
    oq_hazard_mean_filepath = Path(oq_output_path, 'hazard_curve-mean-PGA_13.csv')
    oq_hazard_10_filepath = Path(oq_output_path, 'quantile_curve-0.1-PGA_13.csv')
    oq_hazard_90_filepath = Path(oq_output_path, 'quantile_curve-0.9-PGA_13.csv')
    levels_OQ, hazard_OQ_mean = read_csv(oq_hazard_mean_filepath, location)
    junk, hazard_OQ_10 = read_csv(oq_hazard_10_filepath, location)
    junk, hazard_OQ_90 = read_csv(oq_hazard_90_filepath, location)
    oq_hazard = {
        'levels': levels_OQ,
        'mean': hazard_OQ_mean,
        '0.1': hazard_OQ_10,
        '0.9': hazard_OQ_90,
    }
    return oq_hazard

def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

def prob_to_rate(prob):
    return -np.log(1 - prob) / INV_TIME

def prob_to_rate_err(prob, err):
    return prob_to_rate(prob) * (1 + err)
    # return prob

def rate_to_prob(rate):
    return 1.0 - np.exp(-INV_TIME * rate)

def rate_to_prob_err(rate, err):
    return rate_to_prob(rate) * (1 - err)

location_ids = ['AKL', 'WLG', 'CHC', 'DUD']
oq_output_path = Path("/home/chrisdc/NSHM/oqruns/Test_Against_OQ/output")
oq_hazard = {}
for c, location_id in enumerate(location_ids):
    i = c%2
    j = int(c/2)
    location = CodedLocation(*lat_lon(location_id), 0.001)
    oq_hazard[location_id] = load_oq_hazard(oq_output_path, location)

err = 1e-2
prob1 = oq_hazard['CHC']['mean']
prob2 = oq_hazard['DUD']['mean']
prob_sum = rate_to_prob(prob_to_rate(prob1) + prob_to_rate(prob2))
prob_sum_err = rate_to_prob_err(prob_to_rate_err(prob1, err) + prob_to_rate_err(prob2, err), err)

fig, ax = plt.subplots(1,2)
ax[0].plot(oq_hazard['CHC']['levels'], prob1, label='prob1')
ax[0].plot(oq_hazard['DUD']['levels'], prob2, label='prob2')
ax[0].plot(oq_hazard['DUD']['levels'], prob_sum, label='sum')
ax[0].plot(oq_hazard['DUD']['levels'], prob_sum_err, label='sum w err')
ax[0].set_xscale('log')
ax[0].set_yscale('log')
ax[0].grid(True)
ax[0].legend()

ax[1].plot(oq_hazard['DUD']['levels'], prob_sum_err/prob_sum, label='sum')
ax[1].set_xscale('log')
plt.show()


