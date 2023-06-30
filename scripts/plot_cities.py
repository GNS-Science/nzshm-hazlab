import geopandas
import matplotlib.pyplot as plt

from nzshm_common.location.location import LOCATION_LISTS, location_by_id

fig, ax = plt.subplots(1,1)
coast_file_path = '/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp'
nz = geopandas.read_file(coast_file_path)
nz.boundary.plot(ax=ax, color='k')


x_NZ = [location_by_id(lid)['longitude'] for lid in  LOCATION_LISTS['NZ']['locations']]
y_NZ = [location_by_id(lid)['latitude'] for lid in  LOCATION_LISTS['NZ']['locations']]
x_SRWG = [location_by_id(lid)['longitude'] for lid in  LOCATION_LISTS['SRWG214']['locations']]
y_SRWG = [location_by_id(lid)['latitude'] for lid in  LOCATION_LISTS['SRWG214']['locations']]

ax.plot(x_SRWG, y_SRWG, 'bo')
ax.plot(x_NZ, y_NZ, 'rs', markersize=5)

plt.show()