from nzshm_common.location.location import LOCATION_LISTS, location_by_id
from nzshm_common.location import CodedLocation
from toshi_hazard_store import query

resolution = 0.001 # resolution at which we store lat, lon in the model
# these are the lookups for the locations in the model, you could use your spreadsheet, but this is probably easier
location_keys = LOCATION_LISTS['HB']['locations'] 
# locations are coded as '~' seperated lat~lon strings
locations = [CodedLocation(location_by_id(k)['latitude'], location_by_id(k)['longitude'], resolution).code for k in location_keys]
imt = 'PGA'
vs30 = 0 # value of 0 indicates that the vs30s are site-specific
aggs = ['mean', '0.1', '0.9'] # statistical aggregations you want (mean, 10th percentile, 90th percentile)
hazard_id = 'NSHM_v1.0.4'

for res in query.get_hazard_curves(locations[0:10], [vs30], [hazard_id], [imt], aggs):
    lat = res.lat
    lon = res.lon
    imt = res.imt
    agg = res.agg
    site_vs30 = res.site_vs30 # this only exists for models whith site spcific vs30
    levels = [item.lvl for item in res.values] # the IMTL levels
    apoes = [item.val for item in res.values] # the annual probabilities of exceedance

    print(lat, lon, imt, agg, site_vs30)
    print(levels)
    print(apoes)    
