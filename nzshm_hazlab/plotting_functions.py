import numpy as np
import pandas as pd
from nzshm_hazlab.base_functions import period_from_imt, imt_from_period
from nzshm_hazlab.data_functions import ( 

    calculate_agg,
    compute_hazard_at_poe,
    rp_from_poe,
    poe_from_rp,
    rp_from_poe
)

from uuid import RESERVED_FUTURE
from matplotlib.collections import LineCollection

from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def plot_hazard_curve_fromdf(hazard_data, location, imt, ax, xlim, ylim,
                                central='mean', bandw=None, ref_lines=None, quants=None,
                                xscale='log',custom_label=None, color=None):
    
    lat, lon = location.split('~')

    hd_filt = hazard_data.loc[ (hazard_data['imt'] == imt) & (hazard_data['lat'] == lat) & (hazard_data['lon'] == lon)]

    levels = hd_filt.loc[ hazard_data['agg'] == central]['level'].to_numpy(dtype='float64')
    values = hd_filt.loc[ hazard_data['agg'] == central]['hazard'].to_numpy(dtype='float64')

    clr = color if color else 'k'

    lh, = ax.plot(levels,values,color=clr,lw=3,label=central)

    clr = color if color else 'b'
    if bandw: #{'u1':'0.8,'u2':'0.95', ...}
        
        bandw_data = {}
        for k,v in bandw.items():
            values = hd_filt.loc[ hazard_data['agg'] == v]['hazard'].to_numpy(dtype='float64')
            bandw_data[k] = values
        
        ax.fill_between(levels, bandw_data['upper1'], bandw_data['lower1'],alpha = 0.5, color=clr)
        ax.plot(levels, bandw_data['upper2'],color=clr,lw=1)
        ax.plot(levels, bandw_data['lower2'],color=clr,lw=1)
        # ax.plot(levels, bandw_data['upper2'],linestyle='--',color=clr,lw=1)
        # ax.plot(levels, bandw_data['lower2'],linestyle='--',color=clr,lw=1)
        # ax.plot(levels, bandw_data['upper1'],color=clr,lw=2)
        # ax.plot(levels, bandw_data['lower1'],color=clr,lw=2)
    if quants:
        for quant in quants:
            levels = hd_filt.loc[ hazard_data['agg'] == quant]['level'].to_numpy()
            values = hd_filt.loc[ hazard_data['agg'] == quant]['hazard'].to_numpy()
            ax.plot(levels,values,'b',alpha=.8,lw=1,label=quant)


    for ref_line in ref_lines:
        if ref_line['type'] == 'poe':
            poe = ref_line['poe']
            inv_time = ref_line['inv_time']
            rp = rp_from_poe(poe, inv_time)
        elif ref_line['type'] == 'rp':
            inv_time = ref_line['inv_time']
            rp = ref_line['rp']
            poe = poe_from_rp(poe, inv_time)

        text = f'{poe*100:.0f}% in {inv_time:.0f} years (1/{rp:.0f})'
        
        _ = ax.plot(xlim,[1/rp]*2,ls='--',color='dimgray',zorder=-1)
        # _ = ax.annotate(text, [xlim[1],1/rp], ha='right',va='bottom')
        _ = ax.annotate(text, [xlim[1],1/rp], ha='right',va='bottom')

    if not bandw:
        _ = ax.legend(handlelength=2)

    if xscale == 'log':
        _ = ax.set_xscale('log')
    _ = ax.set_yscale('log')
    _ = ax.set_ylim(ylim)
    _ = ax.set_xlim(xlim)
    _ = ax.set_xlabel('Shaking Intensity, %s [g]'%imt)
    _ = ax.set_ylabel('Annual Probability of Exceedance')
    _ = ax.grid(color='lightgray')  

    return lh

            


def plot_hazard_curve_wunc(hazard_data, location, imt, ax, xlim, ylim, bandw=False, inset=None):

    lvls = hazard_data.values(location=location,imt=imt,realization=0).lvls

    if bandw:
        quantiles = dict(
                        upper1 = 0.8,
                        lower1 = 0.2,
                        upper2 = 0.95,
                        lower2 = 0.05,
                        )
        values = {}
        for k,quant in quantiles.items():
            values[k] = calculate_agg(hazard_data,location,imt,quant)
        ax.fill_between(lvls, values['upper1'], values['lower1'],alpha = 0.5, color='b')
        ax.plot(lvls, values['upper2'],color='b',lw=1)
        ax.plot(lvls, values['lower2'],color='b',lw=1)
    else:
        da = 0.01
        aggs = np.arange(0,1.0+da,da)
        for i,agg in enumerate(aggs):
            # alpha = min(1.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0)+0.25)
            # alpha = min(1.0,-(2.0/len(aggs))**2 * (i-len(aggs)/2.0)**2  + 1.2)
            # alpha = max(0.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0)-0.1)
            # alpha = max(0.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0))
            # alpha = (len(aggs)/2.0 + np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0) - 1.0
            alpha = max(0.5,(len(aggs)/2.0 + np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0) - 1.0)
            print(alpha)
            vals = calculate_agg(hazard_data,location,imt,agg)
            # ax.plot(lvls,vals,color=str(alpha),alpha=0.6,lw=1)
            ax.plot(lvls,vals,color=str(alpha),lw=1)
                    
    vals = calculate_agg(hazard_data,location,imt,0.5)
    ax.plot(lvls,vals,'b',alpha=.8,lw=2)

    if inset:
        poe = inset['poe']
        inv_time = inset['inv_time']
        rp = -inv_time/np.log(1-poe)
        ax.plot(xlim,[1/rp]*2,ls='--',color='dimgray',zorder=-1)
        axins = inset_axes(ax, width="35%", height="25%")

        da = 0.02
        aggs = np.arange(0.01,0.99,da)
        haz_poe = [] #acceleration
        for i,agg in enumerate(aggs):
            vals = calculate_agg(hazard_data,location,imt,agg)
            haz_poe.append(compute_hazard_at_poe(lvls,vals,poe,inv_time))
        pdf = []
        for i in range(1,len(aggs)-1):
            pdf.append( (aggs[i+1] - aggs[i-1])/(2*(haz_poe[i+1]-haz_poe[i-1])) )
        axins.plot(haz_poe[1:-1],pdf,color='k',lw=1)

        
        da = 0.02
        aggs = np.arange(0.2-da,0.8+da,da)
        haz_poe = [] #acceleration
        for i,agg in enumerate(aggs):
            vals = calculate_agg(hazard_data,location,imt,agg)
            haz_poe.append(compute_hazard_at_poe(lvls,vals,poe,inv_time))
        pdf = []
        for i in range(1,len(aggs)-1):
            pdf.append( (aggs[i+1] - aggs[i-1])/(2*(haz_poe[i+1]-haz_poe[i-1])) )
        axins.fill_between(haz_poe[1:-1],pdf,alpha = 0.5, color='b',lw=1)

        xticks = axins.get_xticks()
        axins.set_xticks(xticks,labels=[])
        yticks = axins.get_yticks()
        axins.set_yticks(yticks,labels=[])
        # ylim = axins.get_ylim()
        # axins.set_ylim((min(pdf)-0.05,ylim[1]))
        # axins.set_ylabel('Probability of Shaking at PoE',fontsize=10)
        # axins.set_xlabel('Shaking Intensity [g]',fontsize=10)

    _ = ax.set_xscale('log')
    _ = ax.set_yscale('log')
    _ = ax.set_ylim(ylim)
    _ = ax.set_xlim(xlim)
    _ = ax.grid(color='lightgray')


def plot_spectrum_fromdf(hazard_data, location, poe, inv_time, ax, 
                            central='mean',bandw=False, color='b'):
    #TODO: this is slow!

    lat, lon = location.split('~')

    hd_filt = hazard_data.loc[ (hazard_data['lat'] == lat) & (hazard_data['lon'] == lon)]


    imts = set(hazard_data['imt'])
    periods = [period_from_imt(imt) for imt in imts]
    periods.sort()
    imts = [imt_from_period(period) for period in periods]

    # lvls = list(set(hazard_data['level']))
    # lvls.sort()


    if bandw:
        quantiles = dict(
                        upper1 = 0.8,
                        lower1 = 0.2,
                        upper2 = 0.975,
                        lower2 = 0.025,
                        )
        hazard = {}
        for k,quant in quantiles.items():
            haz = []
            for imt in imts:
                # vals = calculate_agg(hazard_data,location,imt,quant)
                vals = hd_filt.loc[(hd_filt['imt'] == imt) & (hd_filt['agg'] == str(quant)),'hazard']
                lvls = hd_filt.loc[(hd_filt['imt'] == imt) & (hd_filt['agg'] == str(quant)),'level']
                haz.append(compute_hazard_at_poe(lvls,vals,poe,inv_time))
            hazard[k] = haz
        ax.fill_between(periods,hazard['upper1'],hazard['lower1'],alpha = 0.5, color=color)
        ax.plot(periods, hazard['upper2'],color=color,lw=1)
        ax.plot(periods, hazard['lower2'],color=color,lw=1)
    else:
        da = 0.01
        aggs = np.arange(0,1.0+da,da)
        for i,agg in enumerate(aggs):
            # alpha = min(1.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0)+0.25)
            # alpha = min(1.0,-(2.0/len(aggs))**2 * (i-len(aggs)/2.0)**2  + 1.2)
            # alpha = max(0.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0)-0.1)
            alpha = max(0.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0))
            hazard = []
            for imt in imts:
                vals = calculate_agg(hazard_data,location,imt,agg)
                hazard.append(compute_hazard_at_poe(lvls,vals,poe,inv_time))
            ax.plot(periods,hazard,color=str(alpha),alpha=0.6,lw=1)


    hazard = []
    for imt in imts:
        values = hd_filt.loc[(hd_filt['imt'] == imt) & (hd_filt['agg'] == central),'hazard']
        levels = hd_filt.loc[(hd_filt['imt'] == imt) & (hd_filt['agg'] == central),'level']
        hazard.append(compute_hazard_at_poe(levels,values,poe,inv_time))

    lh = ax.plot(periods, hazard, color=color, alpha=0.8,lw=2)
    lh = lh[0]

    xlim = [0, max(periods)]
    ylim = ax.get_ylim()
    ylim = [0, ylim[1]]
    _ = ax.set_ylim(ylim)
    _ = ax.set_xlim(xlim)
    _ = ax.set_xlabel('Period [s]')
    _ = ax.set_ylabel('Shaking Intensity [g]')
    _ = ax.grid(color='lightgray')


    return lh


def plot_spectrum_wunc(hazard_data, location, poe, inv_time, ax, bandw=False):
    #TODO: this is slow!

    periods = [period_from_imt(imt) for imt in hazard_data.imts]
    periods.sort()
    imts = [imt_from_period(period) for period in periods]

    lvls = hazard_data.values(location=location,imt='PGA',realization=0).lvls

    if bandw:
        quantiles = dict(
                        upper1 = 0.8,
                        lower1 = 0.2,
                        upper2 = 0.95,
                        lower2 = 0.05,
                        )
        hazard = {}
        for k,quant in quantiles.items():
            haz = []
            for imt in imts:
                vals = calculate_agg(hazard_data,location,imt,quant)
                haz.append(compute_hazard_at_poe(lvls,vals,poe,inv_time))
            hazard[k] = haz
        ax.fill_between(periods,hazard['upper1'],hazard['lower1'],alpha = 0.5, color='b')
        ax.plot(periods, hazard['upper2'],color='b',lw=1)
        ax.plot(periods, hazard['lower2'],color='b',lw=1)
    else:
        da = 0.01
        aggs = np.arange(0,1.0+da,da)
        for i,agg in enumerate(aggs):
            # alpha = min(1.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0)+0.25)
            # alpha = min(1.0,-(2.0/len(aggs))**2 * (i-len(aggs)/2.0)**2  + 1.2)
            # alpha = max(0.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0)-0.1)
            alpha = max(0.0,(len(aggs)/2.0 - np.abs(len(aggs)/2.0 - i)) / (len(aggs)/2.0))
            hazard = []
            for imt in imts:
                vals = calculate_agg(hazard_data,location,imt,agg)
                hazard.append(compute_hazard_at_poe(lvls,vals,poe,inv_time))
            ax.plot(periods,hazard,color=str(alpha),alpha=0.6,lw=1)


    hazard = []
    for imt in imts:
        values = hazard_data.values(location=location,imt=imt,realization='0.5')
        hazard.append(compute_hazard_at_poe(values.lvls,values.vals,poe,inv_time))

    ax.plot(periods, hazard, 'b', alpha=0.8,lw=2)

    xlim = [0, max(periods)]
    ylim = ax.get_ylim()
    ylim = [0, ylim[1]]
    _ = ax.set_ylim(ylim)
    _ = ax.set_xlim(xlim)
    _ = ax.grid(color='lightgray')



def plot_hazard_curve(ax, site_list, imt, xlim, ylim, results,
                        ref_lines=None,
                        legend_type='site',
                        mean=False,
                        median=True,
                        quant=False,
                        show_rlz=True,
                        intensity_type='acc',
                        xscale='linear',custom_label=None, color=None):
    """
    plot hazard curves

    Parameters
    ----------
    ax:             matplotlib.axes
                    axis handle to plot to
    site_list:      list of str
                    sites to plot from the results dictionary
    imt:            list of str
                    intensity masure types to plot
    xlim:           list of float
                    x-limits for plot
    ylim:           list of float
                    y-limits for plot
    results:        dict
                    dictionary containing hazard data
    ref_lines:      dict, optional
                    draw lines at PoE or 1/(return period).
                    list of dicts. each dict contains a key called 'type' = ('poe' | 'rp')
                    if type=='poe', then other dict keys are 'poe' = poe and 'inv_time' = investigation time
                    if type=='rp', then other dict key is 'rp' = repeat period
    legend_type:    str, optional
                    specify how curves are colored and noted in legend 'site' or 'quant'
    mean:           bool, optional
                    turn on mean plotting
    median:         bool, optional
                    turn on median plotting
    quant:          bool, optional
                    turn on quantile plotting
    show_rlz:       bool, optional
                    show realizations
    intensity_type: str, optional
                    'acc' or 'disp'
    xscale:         str, optional
                    'linear' or 'log'
    """

    #TODO runs slowly; any performance imporvements to be had?
    
    imtls = results['metadata'][f'{intensity_type}_imtls']
    
    hcurves_stats = np.array(results['hcurves']['hcurves_stats'])
    sites = pd.DataFrame(results['metadata']['sites'])
    quantiles = results['metadata']['quantiles']

    if show_rlz:
        hcurves_rlzs = np.array(results['hcurves']['hcurves_rlzs']) 
    
    imt_idx = list(imtls.keys()).index(imt)  
    
    for i_site,site in enumerate(site_list):
        if not color:
            color = 'C%s'%i_site
                
        if legend_type == 'quant':
            color_m = 'r'
        else:
            color_m = color

        site_idx = sites.loc[site,'sids']
        
        if mean:
            if custom_label:
                label = custom_label
            else:
                if legend_type == 'site':
                    label = site
                elif legend_type == 'quant':
                    label = 'mean'

            ls = '-'
            lw = 5
            _ = ax.plot(imtls[imt],hcurves_stats[site_idx,imt_idx,:,0],color='k',lw=lw,ls=ls)
            ls = '-.'
            lw = 3
            _ = ax.plot(imtls[imt],hcurves_stats[site_idx,imt_idx,:,0],color=color_m,lw=lw,ls=ls,label=label)
        
        if median:
            if custom_label:
                label = custom_label
            else:
                if legend_type == 'site':
                    label = site
                elif legend_type == 'quant':
                    label = 'median (p50)'

            q_idx = quantiles.index(0.5)+1
            ls = '-'
            lw = 4
            # _ = ax.plot(imtls[imt],hcurves_stats[site_idx,imt_idx,:,q_idx],color='k',lw=lw,ls=ls)
            ls = '-'
            lw = 3
            _ = ax.plot(imtls[imt],hcurves_stats[site_idx,imt_idx,:,q_idx],color=color_m,lw=lw,ls=ls,label=label)

        if quant:
            if legend_type == 'quant':
                label = 'p10/p90'
            elif legend_type == 'site':
                label = ''

            ls = '--'
            lw = 1.5
            q_idx = quantiles.index(0.1)+1
            _ = ax.plot(imtls[imt],hcurves_stats[site_idx,imt_idx,:,q_idx],color=color_m,lw=lw,ls=ls,label=label)
            q_idx = quantiles.index(0.9)+1
            _ = ax.plot(imtls[imt],hcurves_stats[site_idx,imt_idx,:,q_idx],color=color_m,lw=lw,ls=ls)
            
        if show_rlz:
            lw = 1
            alpha = 0.25
            [_,_,n_imtls,n_rlz] = hcurves_rlzs.shape
            segs = np.zeros([n_rlz, n_imtls, 2])
            segs[:, :, 0] = imtls[imt]
            segs[:, :, 1] = np.transpose(np.squeeze(hcurves_rlzs[site_idx,imt_idx,:,:]))
            line_segments = LineCollection(segs, color=color, alpha=alpha, lw=lw)
            _ = ax.add_collection(line_segments)
            
    for ref_line in ref_lines:
        if ref_line['type'] == 'poe':
            poe = ref_line['poe']
            inv_time = ref_line['inv_time']
            rp = -inv_time/np.log(1-poe)
        elif ref_line['type'] == 'rp':
            inv_time = ref_line['inv_time']
            rp = ref_line['rp']
            poe = 1 - np.exp(-inv_time/rp)

        text = f'{poe*100:.0f}% in {inv_time:.0f} years (1/{rp:.0f})'
        
        _ = ax.plot(xlim,[1/rp]*2,ls='--',color='dimgray',zorder=-1)
        _ = ax.annotate(text, [xlim[1],1/rp], ha='right',va='bottom')

    if mean or median:
        _ = ax.legend(handlelength=2)
    
    _ = ax.set_yscale('log')
    if xscale == 'log':
        _ = ax.set_xscale('log')
    _ = ax.set_ylim(ylim)
    _ = ax.set_xlim(xlim)
    
    _ = ax.grid(color='lightgray')
    
    if intensity_type=='acc':
        _ = ax.set_xlabel('Shaking Intensity, %s [g]'%imt)
    elif intensity_type=='disp':
        _ = ax.set_xlabel('Displacement, %s [m]'%imt)
    _ = ax.set_ylabel('Annual Probability of Exceedance')


def plot_rfactor_curve(ax,site_list,imt,ref_rps,xlim,ylim,results,mean=False,median=True,show_rlz=True,intensity_type='acc'):
    
    rfactor_1170 = np.array([[20,  25,   50,   100, 250,  500, 1000, 2000, 2500],
                             [0.2, 0.25, 0.35, 0.5, 0.75, 1.0, 1.3,  1.7,  1.8]])
    r_rp = 500
    
    imtls = results['metadata'][f'{intensity_type}_imtls']
    hcurves_rlzs = np.array(results['hcurves']['hcurves_rlzs'])
    hcurves_stats = np.array(results['hcurves']['hcurves_stats'])
    sites = pd.DataFrame(results['metadata']['sites'])
    quantiles = results['metadata']['quantiles']
    
    hazard_rps = np.array(results['hazard_design']['hazard_rps'])
    im_hazard = np.array(results['hazard_design'][intensity_type]['im_hazard'])
    stats_im_hazard = np.array(results['hazard_design'][intensity_type]['stats_im_hazard'])
    
    imt_idx = list(imtls.keys()).index(imt)
    rp_idx = np.where(hazard_rps==r_rp)[0]
    
    for i_site,site in enumerate(site_list):
        color = 'C%s'%i_site
        site_idx = sites.loc[site,'sids']
        
        if mean:
            ls = '-'
            lw = '5'
            _ = ax.plot(imtls[imt]/stats_im_hazard[site_idx,imt_idx,rp_idx,0],hcurves_stats[site_idx,imt_idx,:,0],color='k',lw=lw,ls=ls)
            ls = '--'
            lw = 3
            _ = ax.plot(imtls[imt]/stats_im_hazard[site_idx,imt_idx,rp_idx,0],hcurves_stats[site_idx,imt_idx,:,0],color=color,lw=lw,ls=ls,label=site)
        
        if median:
            q_idx = quantiles.index(0.5)+1
            ls = '-'
            lw = 5
            _ = ax.plot(imtls[imt]/stats_im_hazard[site_idx,imt_idx,rp_idx,q_idx],hcurves_stats[site_idx,imt_idx,:,q_idx],color='k',lw=lw,ls=ls)
            ls = '-'
            lw = 3
            _ = ax.plot(imtls[imt]/stats_im_hazard[site_idx,imt_idx,rp_idx,q_idx],hcurves_stats[site_idx,imt_idx,:,q_idx],color=color,lw=lw,ls=ls,label=site)
            
        if show_rlz:
            lw = 1
            alpha = 0.25
            [_,_,n_imtls,n_rlz] = hcurves_rlzs.shape
            segs = np.zeros([n_rlz, n_imtls, 2])
            for i_rlz in range(n_rlz):
                segs[i_rlz, :, 0] = imtls[imt] / im_hazard[site_idx,imt_idx,rp_idx,i_rlz,0]
            segs[:, :, 1] = np.transpose(np.squeeze(hcurves_rlzs[site_idx,imt_idx,:,:]))
            line_segments = LineCollection(segs, color=color, alpha=alpha, lw=lw)
            _ = ax.add_collection(line_segments)
            
    for rp in ref_rps: 
        _ = ax.plot(xlim,[1/rp]*2,ls='--',color='dimgray',zorder=-1)
        _ = ax.annotate('1 / %s '%rp, [xlim[1],1/rp], ha='right',va='bottom')
        
    _ = ax.plot(rfactor_1170[1,:],1/rfactor_1170[0,:],color='k',lw=5,label='NZS1170.5')
    
    _ = ax.legend(handlelength=1)
    
    _ = ax.set_yscale('log')
    _ = ax.set_ylim(ylim)
    _ = ax.set_xlim(xlim)
    
    _ = ax.grid(color='lightgray')
    
    _ = ax.set_xlabel('R-factor, %s/%s$_{%s}$'%(imt,imt,r_rp))
    _ = ax.set_ylabel('Probability of Exceedance')


def plot_spectrum(ax,site,rp,results,inv_time,legend_type='site',color='C0',mean=False,median=True,quant=False,show_rlz=True,intensity_type='acc'):
    
    sites = pd.DataFrame(results['metadata']['sites'])
    imtls = results['metadata'][f'{intensity_type}_imtls']
    quantiles = results['metadata']['quantiles']
    
    hazard_rps = np.array(results['hazard_design']['hazard_rps'])
    im_hazard = np.array(results['hazard_design'][intensity_type]['im_hazard'])
    stats_im_hazard = np.array(results['hazard_design'][intensity_type]['stats_im_hazard'])
    
    site_idx = sites.loc[site,'sids']
    rp_idx = np.where(hazard_rps==rp)[0]

    poe = 1-np.exp(-inv_time/rp)
    tmp = f'{poe*100:.0f}_in_{inv_time:.0f}'

    if legend_type=='site':
        label = site
        color_m = color
    elif legend_type=='quant':
        color_m = 'r'
    
    periods = [period_from_imt(imt) for imt in imtls.keys()]
    
    if mean:
        if legend_type == 'quant':
            label = 'mean'

        ls = '-'
        lw = '5'
        _ = ax.plot(periods,np.squeeze(stats_im_hazard[site_idx,:,rp_idx,0]),color='k',lw=lw,ls=ls)
        ls = '-.'
        lw = 3
        _ = ax.plot(periods,np.squeeze(stats_im_hazard[site_idx,:,rp_idx,0]),color=color_m,lw=lw,ls=ls,label=label)

    if median:
        if legend_type == 'quant':
            label = 'median (p50)'

        q_idx = quantiles.index(0.5)+1
        ls = '-'
        lw = 5
        _ = ax.plot(periods,np.squeeze(stats_im_hazard[site_idx,:,rp_idx,q_idx]),color='k',lw=lw,ls=ls)
        ls = '-'
        lw = 3
        _ = ax.plot(periods,np.squeeze(stats_im_hazard[site_idx,:,rp_idx,q_idx]),color=color_m,lw=lw,ls=ls,label=label)

    if quant:
            if legend_type == 'quant':
                label10 = 'p10'
                label90 = 'p90'
            elif legend_type == 'site':
                label10 = ''
                label90 = ''

            ls = '--'
            lw = 2

            q_idx = quantiles.index(0.1)+1
            _ = ax.plot(periods,np.squeeze(stats_im_hazard[site_idx,:,rp_idx,q_idx]),color=color_m,lw=lw,ls=ls,label=label10)
            q_idx = quantiles.index(0.9)+1
            _ = ax.plot(periods,np.squeeze(stats_im_hazard[site_idx,:,rp_idx,q_idx]),color=color_m,lw=lw,ls=ls,label=label90)

    if show_rlz:
        lw = 1
        alpha = 0.25
        [_,n_imts,n_rps,n_rlz,_] = im_hazard.shape
        segs = np.zeros([n_rlz, n_imts, 2])
        segs[:, :, 0] = periods
        segs[:, :, 1] = np.transpose(np.squeeze(im_hazard[site_idx,:,rp_idx,:,0]))
        line_segments = LineCollection(segs, color=color, alpha=alpha, lw=lw)
        _ = ax.add_collection(line_segments)

    if mean or median:
        _ = ax.legend(handlelength=2)
    
    _ = ax.grid(color='lightgray')
        
    _ = ax.set_xlabel('Period [s]')
    if intensity_type=='acc':
        _ = ax.set_ylabel('Shaking Intensity [g]')
    elif intensity_type=='disp':
        _ = ax.set_ylabel('Displacement [m]')

    xlim = [0, max(periods)]
    ylim = ax.get_ylim()
    ylim = [0, ylim[1]]
    _ = ax.set_ylim(ylim)
    _ = ax.set_xlim(xlim)


def retrieve_design_intensities(results,intensity_type,design_type,imt,rp=500):
    '''
    return the design intensities based on the selected design parameters
    '''
    
    imtls = results['metadata'][f'{intensity_type}_imtls']
    imt_idx = list(imtls.keys()).index(imt)

    if design_type == 'hazard_design':
        im_idx = results[design_type]['hazard_rps'].index(rp)
        im_values_rlzs = np.squeeze(np.array(results[design_type][intensity_type]['im_hazard'])[:,imt_idx,im_idx,:,0])
        im_values_stats = np.squeeze(np.array(results[design_type][intensity_type]['stats_im_hazard'])[:,imt_idx,im_idx,:])
        
    return im_values_rlzs, im_values_stats


