import csv
import geopandas
import matplotlib.pyplot as plt
from collections import namedtuple

coast_file_path = '/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp'


def get_mags(mag_filepath):
    lats, lons, mags = [], [], []
    with open(mag_filepath, 'r') as magfile:
        reader = csv.reader(magfile)
        Disagg = namedtuple("Disagg", next(reader), rename=True)
        for row in reader:
            disagg = Disagg(*row)
            if disagg._5 == '10':
                lats.append(float(disagg.latitude))
                lons.append(float(disagg.longitude))
                mags.append(float(disagg._8))

    return lats, lons, mags


lats_02, lons_02, mags_02 = get_mags('/home/chrisdc/NSHM/DEV/nzshm-hazlab/grid_02_mean_mag.csv')
lats_infill, lons_infill, mags_infill = get_mags('/home/chrisdc/NSHM/DEV/nzshm-hazlab/grid_01_infill_mean_mag.csv')
lats_01 = lats_02 + lats_infill
lons_01 = lons_02 + lons_infill
mags_01 = mags_02 + mags_infill

fig, ax = plt.subplots(1,2)
nz = geopandas.read_file(coast_file_path)
nz.boundary.plot(ax=ax[0], color='k')
# ax[0].scatter(lons_02, lats_02, c=mags_02, s=10, marker='o', cmap='inferno', vmin=5.6, vmax=8.3)
ax[0].scatter(lons_01, lats_01, c=mags_01, s=5, marker='s', cmap='inferno', vmin=5.6, vmax=8.3)
ax[0].set_title('0.1 deg grid')

nz.boundary.plot(ax=ax[1], color='k')
sc = ax[1].scatter(lons_02, lats_02, c=mags_02, s=10, marker='o', cmap='inferno', vmin=5.6, vmax=8.3)
ax[1].set_title('0.2 deg grid')
plt.colorbar(sc)