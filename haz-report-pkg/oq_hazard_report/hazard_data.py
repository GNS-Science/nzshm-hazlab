from collections import UserDict, namedtuple
from functools import lru_cache

from toshi_hazard_store import query

def retrieve_data_mock(key): #mock function
    return key + 'Data'

def get_hazard_metadata_mock(): #mock function
    MetaData = namedtuple("MetaData","imts aggs gsim_lt haz_sol_id hazsol_vs30_rk locs rlz_lt src_lt vs30")
    meta_data = MetaData("imts","aggs", "gsim_lt", "haz_sol_id", "hazsol_vs30_rk", "locs", "rlz_lt", "src_lt", "vs30")
    return meta_data


def encode_key(imt=None,location=None,realization=None):
    return ':'.join(map(str,(imt,location,realization)))

def decode_key(key):
    Key = namedtuple("Key","imt location realization")
    key_tuple = Key(*key.split(':'))
    return key_tuple


class LazyData(UserDict):

    def __init__(self,hazard_id):
        self._hazard_id = hazard_id 
        super().__init__()

    def __getitem__(self, key):
        if not self.data.get(key):
            self.data[key] = self.retrieve_data(key)
        return self.data[key]

    def __setitem__(self, key: _KT, item: _VT) -> None:
        raise Exception("LazyData: cannot set items")

    def retrieve_data(self,key):
        print('retrieve_data')
        k = decode_key(key)
        q = query.get_hazard_stats_curves(self._hazard_id,[k.imt],[k.location],[k.realization]) #TODO switch bt stats and rlz
        r = next(q)
        return r

            
class HazardData:

    def __init__(self,hazard_id):
        self._hazard_id = hazard_id
        self._data = LazyData(self._hazard_id) 
    
    @property
    @lru_cache(maxsize=None)
    def hazard_meta(self):
        print('get_hazard_metadata')
        return self.get_hazard_metadata()

    @property
    @lru_cache(maxsize=None)
    def imts(self):
        print('imts')
        return self.hazard_meta.imts

    @property
    @lru_cache(maxsize=None)
    def vs30(self):
        return self.hazard_meta.vs30

    @property
    @lru_cache(maxsize=None)
    def aggs(self):
        return self.hazard_meta.aggs

    @property
    @lru_cache(maxsize=None)
    def gsim_lt(self):
        return self.hazard_meta.gsim_lt

    @property
    @lru_cache(maxsize=None)
    def haz_sol_id(self):
        return self.hazard_meta.haz_sol_id

    @property
    @lru_cache(maxsize=None)
    def hazsol_vs30_rk(self):
        return self.hazard_meta.hazsol_vs30_rk

    @property
    @lru_cache(maxsize=None)
    def locs(self):
        return self.hazard_meta.locs

    @property
    @lru_cache(maxsize=None)
    def rlz_lt(self):
        return self.hazard_meta.rlz_lt

    @property
    @lru_cache(maxsize=None)
    def src_lt(self):
        return self.hazard_meta.src_lt
    
    
    def values(self, location=None, imt=None, realization=None):
        key = encode_key(location=location,imt=imt,realization=realization)
        lvls = [p.lvl for p in self._data[key].values]
        vals = [p.val for p in self._data[key].values]
        Values = namedtuple("Values","lvls vals")
        return Values(lvls=lvls,vals=vals)


    def get_hazard_metadata(self):
        q = query.get_hazard_metadata([self._hazard_id])
        return next(q)




