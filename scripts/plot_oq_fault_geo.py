import matplotlib.pyplot as plt
import geopandas
from nzshm_common.location.location import LOCATIONS_BY_ID
from shapely.geometry import LineString


# hik_old_ruptures_xml_path = "/home/chrisdc/tmp/xml_test/comp_hik/old/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTE0MTk2-ruptures_sections.xml"
# ruptures_xml_path = "/home/chrisdc/Downloads/new_convert/NZSHM22_ScaledInversionSolution-QXV0b21hdGlvblRhc2s6MTA3NjY4_nrml/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTE0MTEx-ruptures_sections.xml"
# hik_ruptures_xml_path = "//home/chrisdc/tmp/oq_fault_geo/hik/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTE0MTk2-ruptures_sections.xml"
# puy_ruptures_xml_path = "/home/chrisdc/tmp/xml_test/puy/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTE4NTQz-ruptures_sections.xml"
cru_ruptures_xml_path = "/home/chrisdc/tmp/oq_fault_geo/cru/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNjk4-ruptures_sections.xml"
coast_file_path = '/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp'


def interface_geo(ruptures_xml_path): 
    points = []
    with open(ruptures_xml_path) as xmlfile:
        for xmlline in xmlfile:
            if "<gml:posList>" in xmlline:
                lon0, lat0, depth0, lon1, lat1, depth1 = [float(coord) for coord in xmlfile.readline().split()]
                lon0 = lon0 + 360 if lon0 < 0 else lon0
                lon1 = lon1 + 360 if lon1 < 0 else lon1
                line = LineString([[lon0, lat0, depth0], [lon1, lat1, depth1] ])
                points.append((lon0, lat0)) 
                points.append((lon1, lat1)) 
        
    x = [p[0] for p in points]
    y = [p[1] for p in points]

    return x, y

# x_hik_old, y_hik_old = interface_geo(hik_old_ruptures_xml_path)
# x_hik, y_hik = interface_geo(hik_ruptures_xml_path)
# x_puy, y_puy = interface_geo(puy_ruptures_xml_path)
x_cru, y_cru = interface_geo(cru_ruptures_xml_path)
fig, ax = plt.subplots(1,1)
# ax.plot(x_hik_old,y_hik_old,'k.')
# ax.plot(x_hik,y_hik,'g.')
# ax.plot(x_puy,y_puy,'r.')
ax.plot(x_cru,y_cru,'m.')
ax.grid()

nz = geopandas.read_file(coast_file_path)
nz.boundary.plot(ax=ax)
# x_cities = [loc['longitude'] for loc in LOCATIONS_BY_ID.values()]
# y_cities = [loc['latitude'] for loc in LOCATIONS_BY_ID.values()]
# ax.plot(x_cities, y_cities, 'bo')
plt.show()