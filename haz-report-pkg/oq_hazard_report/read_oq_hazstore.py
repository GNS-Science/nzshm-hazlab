import numpy as np
import pandas as pd

from oq_hazard_report.read_oq_hdf5 import convert_imtls_to_disp, find_site_names
from toshi_hazard_store import query
from nzshm_common.location import location


def retrieve_data(hazard_id):
    '''
    Retrieves the data and metadata from toshi-hazard-store and producing legacy data structure (designed by Anne H.).
    '''

    data = {}
    data['metadata'] = {}

    for m in query.get_hazard_metadata([hazard_id]):
        rlzs_df = pd.read_json(m.rlz_lt)
        aggs = m.aggs
        imts = list(m.imts)
        imts.sort()

    data['metadata']['quantiles'] = [float(agg) for agg in aggs if (agg != 'mean')]
    data['metadata']['quantiles'].sort()
    data['metadata']['acc_imtls'] = dict.fromkeys(imts)

    sites = pd.DataFrame(list(m.locs))
    sites.columns = ['custom_site_id']

    sites = find_site_names(sites).sort_index()
    sites['sids'] = None
    for i,s in enumerate(sites.index):
        sites.loc[s,'sids'] = i
    data['metadata']['sites'] = sites.to_dict()
    
    data['metadata']['rlz_weights'] = rlzs_df['weight'].to_list()

    nsites = len(m.locs)
    nimts = len(m.imts)

    # TODO is there a better way to tget the number of levels?
    r = next(query.get_hazard_stats_curves(hazard_id))
    nimtls = len(r.values)

    nrlzs = len(rlzs_df.index)
    rlzs_array = np.empty((nsites,nimts,nimtls,nrlzs))
    rlzs_array[:] = np.nan
    stats_array = np.empty((nsites,nimts,nimtls,1+len(data['metadata']['quantiles'])))
    stats_array[:] = np.nan
    

    data['hcurves'] = {}
    res = query.get_hazard_stats_curves(hazard_id) # TODO one arg
    for r in res:
        imt = r.imt 
        site = r.loc
        idx_imt = list(data['metadata']['acc_imtls'].keys()).index(imt)
        idx_site = list(data['metadata']['sites']['custom_site_id'].values()).index(site)
        
        idx_quant = data['metadata']['quantiles'].index(float(r.agg))+1 if r.agg!='mean' else 0

        data['metadata']['acc_imtls'][imt] = [p.lvl for p in r.values]
        stats_array[idx_site, idx_imt,:,idx_quant] = [p.val for p in r.values]

    res = query.get_hazard_rlz_curves(hazard_id)
    for r in res:
        imt = r.imt
        site = r.loc
        idx_rlz = int(r.rlz)
        idx_imt = list(data['metadata']['acc_imtls'].keys()).index(imt)
        idx_site = list(data['metadata']['sites']['custom_site_id'].values()).index(site)
        
        rlzs_array[idx_site, idx_imt,:,idx_rlz] = [p.val for p in r.values]

    
    data['hcurves']['hcurves_stats'] = stats_array.tolist()
    data['hcurves']['hcurves_rlzs'] = rlzs_array.tolist()


    data['metadata']['disp_imtls'] = convert_imtls_to_disp(data['metadata']['acc_imtls'])
        
    return data
