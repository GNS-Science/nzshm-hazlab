import pandas as pd
from nzshm_hazlab.store.levels import get_hazard_at_poe
hazard1 = get_hazard_at_poe('NSHM_v1.0.4',150,'PGA','mean',0.1)


hazard_web = pd.read_csv('/home/chrisdc/Downloads/hazard-maps.csv',header=2)

lat_lons = [str(row[1]['lat']) + '~' + str(row[1]['lon']) for row in hazard_web.iterrows()]
lat_lons_unique = set()
lat_lons_dup = []
for lat_lon in lat_lons:
    if lat_lon in lat_lons_unique:
        lat_lons_dup.append(lat_lon)
    else:
        lat_lons_unique.add(lat_lon)

dups = {}
for row in hazard_web.iterrows():
    lat_lon =  str(row[1]['lat']) + '~' + str(row[1]['lon'])
    if lat_lon in lat_lons_dup:
        if lat_lon in dups:
            dups[lat_lon]['second'] = row[1]['shaking intensity(g)']
        else:
            dups[lat_lon] = {}
            dups[lat_lon]['first'] = row[1]['shaking intensity(g)']

for lat_lon, acc in dups.items():
    lat, lon = lat_lon.split('~')
    print(f'lon: {lon}, lat: {lat}, acc: {acc["first"]}')



lat_lons1 = [str(row[1]['lat']) + '~' + str(row[1]['lon']) for row in hazard1.iterrows()]
lat_lons_missing = []
for lat_lon in lat_lons1:
    if lat_lon not in lat_lons:
        lat_lons_missing.append(lat_lon)
        lat, lon = lat_lon.split('~')
        print(f'lon: {lon}, lat: {lat}')



import geopandas
import matplotlib.pyplot as plt

from nzshm_common.location.location import LOCATION_LISTS, location_by_id

fig, ax = plt.subplots(1,1)
coast_file_path = '/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp'
nz = geopandas.read_file(coast_file_path)
nz.boundary.plot(ax=ax, color='k')

x = [float(ll.split('~')[1]) for ll in lat_lons_missing]
y = [float(ll.split('~')[0]) for ll in lat_lons_missing]
ax.plot(x, y, 'bo')

plt.show()