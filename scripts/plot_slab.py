import geopandas
from zipfile import ZipFile
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
# from solvis import *
import math
import numpy as np
from shapely.geometry import Polygon

xlim = [165,182]
ylim = [-48,-33]

def set_plot_formatting():    
    # set up plot formatting
    SMALL_SIZE = 12
    MEDIUM_SIZE = 16
    BIGGER_SIZE = 25

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


set_plot_formatting()


def get_slab(csv_path):
    dx = 0.1
    dy = 0.1
    dtol = 0.001

    grid = np.genfromtxt(csv_path,delimiter=',',skip_header=1)

    x = grid[:,0]
    y = grid[:,1]
    
    return x, y


coast_shape_fpath = '/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp'
nz = geopandas.read_file(coast_shape_fpath)

slab_path = '/home/chrisdc/NSHM/DEV/nz-oq-slab/components/spatial_distribution/files/processed-uniform/hik-slab-uniform_1depth.csv'
x_slab, y_slab = get_slab(slab_path)

ba_polygon = Polygon(   [
                        (177.2, -37.715),
                        (176.2, -38.72),
                        (175.375, -39.27),
                        (174.25, -40),
                        (173.1, -39.183),
                        (171.7, -34.76),
                        (173.54, -33.22),
                        (177.2, -37.715),
                        ]
)
x,y = ba_polygon.exterior.xy
\

fig, ax = plt.subplots(1,1)
fig.set_size_inches(8,10)
fig.set_facecolor('white')

ax.plot(x_slab,y_slab,'r.')
ax.plot(x,y,lw=3)
nz.boundary.plot(ax=ax,color='k')
ax.set_xlim(xlim)
ax.set_ylim(ylim)

fig.savefig('backarc_slab.png')
plt.close()

