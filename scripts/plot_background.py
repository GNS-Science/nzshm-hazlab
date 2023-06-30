import geopandas
from zipfile import ZipFile
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
# from solvis import *
import math
import numpy as np
import shapely.geometry

xlim = [163,180]
ylim = [-50,-32]

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


def get_background(csv_path):
    dx = 0.1
    dy = 0.1
    dtol = 0.001

    grid = np.genfromtxt(csv_path,delimiter=',',skip_header=1)
    
    x_min = min(grid[:,0])
    x_max = max(grid[:,0])

    y_min = min(grid[:,1])
    y_max = max(grid[:,1])

    x = np.arange(x_min,x_max+dx,dx)
    y = np.arange(y_min,y_max+dy,dy)
    X,Y = np.meshgrid(x,y)
    Z = np.empty(X.shape)
    Z[:] = np.nan

    
    for pt in grid:
        xind = (X >= (pt[0]-dtol)) & (X <= (pt[0]+dtol))
        yind = (Y >= (pt[1]-dtol)) & (Y <= (pt[1]+dtol))
        Z[xind & yind] = pt[2]

    return X,Y,Z


coast_shape_fpath = '/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp'
nz = geopandas.read_file(coast_shape_fpath)

grid_1346_path = '/home/chrisdc/NSHM/DEV/nz-oq-distrseis/components/spatial_distribution/files/Floor_AddoptiEEPAScomb_polygon-adjusted.csv'
# /home/chrisdc/NSHM/DATA/dist_seis/Gruenthalmod1346ConfDSMsss.csv'

X_1346,Y_1346,Z_1346 = get_background(grid_1346_path)


fig, ax = plt.subplots(1,2)
fig.set_size_inches(16,8)
fig.set_facecolor('white')

# cplot = ax[0].contourf(X_1346, Y_1346, Z_1346,locator=ticker.LogLocator(),levels=10)
cplot = ax[0].contourf(X_1346, Y_1346, Z_1346,levels=10)
ax[0].set_title('Gruenthalmod1346ConfDSMsss')
nz.boundary.plot(ax=ax[0],color='k')
ax[0].set_xlim(xlim)
ax[0].set_ylim(ylim)

fig.show()

#----------------------------------------------------------#


grid_hybrid_path = '/home/chrisdc/NSHM/DEV/nz-oq-distrseis/components/spatial_distribution/files/Floor_AddoptiEEPAScomb_polygon-adjusted.csv'
# '/home/chrisdc/NSHM/DATA/dist_seis/Floor_AddoptiEEPAScomb-CRU_pdf.csv'
X_hybrid,Y_hybrid,Z_hybrid = get_background(grid_hybrid_path)
# ax[1].contourf(X_hybrid, Y_hybrid, Z_hybrid,locator=ticker.LogLocator(),levels=10)
ax[1].contourf(X_hybrid, Y_hybrid, Z_hybrid,levels=10)
# ax[1].pcolormesh(X_hybrid, Y_hybrid, Z_hybrid)
cbar = plt.colorbar(cplot)
ax[1].set_title('Floor_AddoptiEEPAScomb-CRU')
nz.boundary.plot(ax=ax[1],color='k')
ax[1].set_xlim(xlim)
ax[1].set_ylim(ylim)


# fig.show()
plt.savefig('spatial_seis_pdf.png')

