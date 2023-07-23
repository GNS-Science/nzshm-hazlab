import tempfile

from zipfile import ZipFile
from pathlib import Path

import geopandas as gpd
import pygmt
import shapely
import math

def degToRad(a):
    return math.pi/180.0 * a

def radToDeg(a):
    return 180.0 / math.pi * a

def calcAzimuth(line):
    lon1,lat1,lon2,lat2 = [(math.pi/180.0)*x for x in line.bounds]
    dlon = lon2-lon1
    return math.atan2(math.sin(dlon)*math.cos(lat2), math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(dlon))

def getDownDipPoint(lat,lon,dip_dir,x):
    R = 6371.0
    Ad = x/R
    latdd = math.asin(math.sin(lat)*math.cos(Ad)+math.cos(lat)*math.sin(Ad)*math.cos(dip_dir))
    londd = lon + math.atan2(math.sin(dip_dir)*math.sin(Ad)*math.cos(lat),math.cos(Ad)-math.sin(lat)*math.sin(lat))
    return(latdd,londd)

def getFaultPatchPoly(line,height,dip):
    lon1,lat1,lon2,lat2 = [(math.pi/180.0)*x for x in line.bounds]
    dip_dir = calcAzimuth(line) + math.pi/2
    x = height / math.tan(dip*math.pi/180.0)
    lat1dd,lon1dd = getDownDipPoint(lat1,lon1,dip_dir,x)
    lat2dd,lon2dd = getDownDipPoint(lat2,lon2,dip_dir,x)
    return shapely.geometry.Polygon([ [radToDeg(lon1), radToDeg(lat1)],\
        [radToDeg(lon2), radToDeg(lat2)],\
        [radToDeg(lon2dd), radToDeg(lat2dd)],\
        [radToDeg(lon1dd), radToDeg(lat1dd)] ])


CPT_FILEPATH = Path('/tmp/tmp.cpt')

def clear_cpt():
    if CPT_FILEPATH.exists():
        CPT_FILEPATH.unlink()


# ███╗░░░███╗░█████╗░██╗███╗░░██╗
# ████╗░████║██╔══██╗██║████╗░██║
# ██╔████╔██║███████║██║██╔██╗██║
# ██║╚██╔╝██║██╔══██║██║██║╚████║
# ██║░╚═╝░██║██║░░██║██║██║░╚███║
# ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝╚═╝░░╚══╝

# inversion_solution_file = "/home/chrisdc/tmp/NZSHM22_InversionSolution-df550df0-9e46-4204-be83-ac535432cf53.zip" #HIK
inversion_solution_file = "/home/chrisdc/tmp/NZSHM22_InversionSolution-QXV0b21hdGlvblRhc2s6MTA3MDM2.zip" # PUY


with ZipFile(inversion_solution_file, 'r') as zip:
    fault_sections_file = zip.open('ruptures/fault_sections.geojson')
    fault_sections = gpd.read_file(fault_sections_file)

ncols = fault_sections.shape[0]
for (index, row) in fault_sections.iterrows():
    dip = row.DipDeg
    height = row.LowDepth - row.UpDepth
    line = row['geometry']
    fault_sections.loc[index,'geometry'] = getFaultPatchPoly(line,height,dip)

plot_width = 10
# region = "172/185/-43/-24" #HIK
region = "163/169/-50/-44" #PUY
projection = f'M{plot_width}c'
colormap = 'hot' #'inferno' # 'viridis', 'jet', 'plasma', 'imola', 'hawaii'
font_size = 10 #12 
font = f'{font_size}p'
legend_text = 'slip rate (mm/yr)'

fig = pygmt.Figure()
pygmt.makecpt(cmap = colormap, series=[0,50, 0.1], output=str(CPT_FILEPATH), reverse=True)
# fig.plot(data=fault_sections, fill="220/220/220", transparency=30, pen="black")

zfilepath = Path('/tmp/zfile')
fault_sections.to_csv(str(zfilepath), columns=['SlipRate'], index=False, header=False)
fig.plot(data=fault_sections, zvalue=str(zfilepath), fill="+z", cmap=CPT_FILEPATH, frame = "a", projection=projection, region=region)
zfilepath.unlink()

# fig.coast(shorelines = True, water="white", frame = "a", projection=projection, region=region)
fig.coast(shorelines = True, frame = "a")
fig.basemap(frame=["a"])

# font = f'{int(int(font[:-1])*0.8)}p'
# font_annot = font
# pygmt.config(FONT_LABEL=font, FONT_ANNOT_PRIMARY=font_annot)
fig.colorbar(frame=f'af+l"{legend_text}"', projection=projection, region=region, position="n0.5/0.07+w4.5c/6%+h+ml",cmap=CPT_FILEPATH)
clear_cpt()

fig.show()
