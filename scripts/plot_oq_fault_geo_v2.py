import xml.etree.ElementTree as ET
import importlib.util
import sys
from itertools import chain

import numpy as np
import matplotlib.pyplot as plt
import geopandas
from nzshm_common.location.location import location_by_id, LOCATION_LISTS
from shapely.geometry import LineString, Polygon, Point


# hik_ruptures_xml_path = "/home/chrisdc/mnt/glacier/NZSHM-WORKING/PROD/hik_filtered/4912/HIK_4912-ruptures_sections.xml"
# puy_ruptures_xml_path = "/home/chrisdc/mnt/glacier/NZSHM-WORKING/TEST/Puy/PUY_test-ruptures_sections.xml"
# cru_ruptures_xml_path = "/home/chrisdc/tmp/convert/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNjk4-ruptures_sections.xml"
cru_ruptures_xml_path_old = "/home/chrisdc/tmp/old_geo/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzI4-ruptures_sections.xml"
hik_ruptures_xml_path = "/home/chrisdc/tmp/check_SLTv9/hik/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTE0MTk0-ruptures_sections.xml"
puy_ruptures_xml_path = "/home/chrisdc/tmp/check_SLTv9/puy/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTI5MTM4Mg__-ruptures_sections.xml"
cru_ruptures_xml_path = "/home/chrisdc/tmp/check_SLTv9/cru/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwODYz-ruptures_sections.xml"
coast_file_path = '/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp'

xlim = [165,180]
ylim = [-47, -36]
PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625

spec = importlib.util.spec_from_file_location("module.name", "/home/chrisdc/NSHM/DEV/nzshm-hazlab/scratch/cr_colormap.py")
cr_colormap = importlib.util.module_from_spec(spec)
sys.modules["module.name"] = cr_colormap
spec.loader.exec_module(cr_colormap)

def make_polygon(top, bottom):
    bottom.reverse()
    return Polygon(chain(top,bottom))

def make_trace(top):
    return LineString(top)

def get_poly_depth(poly):
    depth = 0
    nsides = len(poly.boundary.coords)-1
    for i in range(nsides):
        depth += poly.boundary.coords[i][-1]
    return depth/nsides

def assert_depth_is(traces, adepth):

    for row in traces.iterrows():
        coords = row[1]['geometry'].coords
        for line in coords:
            assert line[-1] == adepth

def get_fault_geo(ruptures_xml_path):
    
    faults = geopandas.GeoDataFrame(columns = ['name', 'depth', 'geometry'])
    traces = geopandas.GeoDataFrame(columns = ['name', 'depth', 'geometry'])
    tree = ET.parse(ruptures_xml_path)
    root = tree.getroot()
    i = 0
    for child in root[0]:
        top = []
        bottom = []
        id = child.attrib['id']
        for profile in child[0]:
            lon0, lat0, depth0, lon1, lat1, depth1 = list( map(float, profile[0][0].text.strip().split()) )
            if lon0< 0:
                lon0 += 360
            if lon1 < 0:
                lon1 += 360
            # lines.append(LineString([[lon0, lat0, depth0], [lon1, lat1, depth1]]))
            top.append(Point((lon0, lat0, depth0)))
            bottom.append(Point((lon1, lat1, depth1)))
        polygon = make_polygon(top, bottom)
        trace = make_trace(top)
        depth = get_poly_depth(polygon)
        faults.loc[i] = {'name':id, 'depth':depth, 'geometry':polygon}
        traces.loc[i] = {'name':id, 'depth':depth, 'geometry':trace}
        i += 1

    return faults, traces

plot_old = True
save_geojson = False
ruptures_xml_path = cru_ruptures_xml_path
ruptures_xml_path_old = cru_ruptures_xml_path_old
# ruptures_xml_path = hik_ruptures_xml_path
# ruptures_xml_path = puy_ruptures_xml_path


faults, traces = get_fault_geo(ruptures_xml_path)
# assert_depth_is(traces, 0.0)

fig, ax = plt.subplots(1,1)
fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
faults.plot(ax=ax, facecolor='none', edgecolor='tab:blue')
# faults.plot(ax=ax, column='depth', edgecolor='none', legend=True, cmap='rainbow_r')
# traces.plot(ax=ax, column='depth', legend=True, cmap='rainbow_r')
traces.plot(ax=ax, edgecolor='tab:red')

nz = geopandas.read_file(coast_file_path)
nz.boundary.plot(ax=ax, color='k')

# cities = [location_by_id(lid) for lid in LOCATION_LISTS['SRWG214']['locations']]
# citiesNZ = [location_by_id(lid) for lid in LOCATION_LISTS['NZ']['locations']]

# ax.plot([city['longitude'] for city in cities], [city['latitude'] for city in cities], 'k.')
# ax.plot([city['longitude'] for city in citiesNZ], [city['latitude'] for city in citiesNZ], 'r.')
# for city in cities:
#     ax.text(city['longitude'], city['latitude'], city['name'])
# for city in citiesNZ:
#     ax.text(city['longitude'], city['latitude'], city['name'] + '_NSHM', color='r')

ax.axis('equal')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title('NSHM v1.0.4 Fault Geometry')

if plot_old:
    faults_old, traces_old = get_fault_geo(ruptures_xml_path_old)
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    faults_old.plot(ax=ax, facecolor='none', edgecolor='tab:blue')
    traces_old.plot(ax=ax, edgecolor='tab:red')

    nz = geopandas.read_file(coast_file_path)
    nz.boundary.plot(ax=ax, color='k')
    ax.axis('equal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_title('NSHM v1.0.0 Fault Geometry')
    # ax.plot([city['longitude'] for city in cities], [city['latitude'] for city in cities], 'k.')
    # for city in cities:
    #     ax.text(city['longitude'], city['latitude'], city['name'])

plt.show()

if save_geojson:
    traces['stroke'] = "#b62a0c"
    faults['fill'] = "#f0d9d4"
    traces.to_file("crustal_traces.geojson", driver='GeoJSON')
    faults.to_file("crustal_faults.geojson", driver='GeoJSON')
