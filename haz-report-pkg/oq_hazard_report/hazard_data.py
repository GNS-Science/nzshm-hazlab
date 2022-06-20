import ast
from collections import UserDict, namedtuple
from functools import lru_cache

from toshi_hazard_store import query


def encode_key(imt,location,realization):
    realization = f'{int(realization):05d}' if str(realization).isdigit() else realization        
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

    def __setitem__(self, key, item) -> None:
        raise Exception("LazyData: cannot set items")

    def _load_all_rlz(self,location):
        q = query.get_hazard_rlz_curves_v2(self._hazard_id,[],[location],[])
        breakpoint()
        for re in q:
            rlz = re.rlz
            for r in re.values:
                imt = r.imt
                key = encode_key(imt,location,rlz)
                self.data[key] = r


    def retrieve_data(self,key):
        print('retrieve_data')
        k = decode_key(key)
        if k.realization.isdigit():
            self._load_all_rlz(k.location)
            q = query.get_hazard_rlz_curves_v2(self._hazard_id,[k.imt],[k.location],[k.realization])
        else:
            q = query.get_hazard_stats_curves_v2(self._hazard_id,[k.imt],[k.location],[k.realization]) 
        r = next(q)
        return r

            
class HazardData:

    def __init__(self,hazard_id):
        self._hazard_id = hazard_id
        self._data = LazyData(self._hazard_id) 
    
    @property
    @lru_cache(maxsize=None)
    def _hazard_meta(self):
        print('get_hazard_metadata')
        return self.get_hazard_metadata()

    @property
    @lru_cache(maxsize=None)
    def imts(self):
        print('imts')
        return self._hazard_meta.imts

    @property
    @lru_cache(maxsize=None)
    def vs30(self):
        return self._hazard_meta.vs30

    @property
    @lru_cache(maxsize=None)
    def aggs(self):
        return self._hazard_meta.aggs

    @property
    @lru_cache(maxsize=None)
    def gsim_lt(self):
        return ast.literal_eval(self._hazard_meta.gsim_lt)

    @property
    @lru_cache(maxsize=None)
    def haz_sol_id(self):
        return self._hazard_meta.haz_sol_id

    @property
    @lru_cache(maxsize=None)
    def hazsol_vs30_rk(self):
        return self._hazard_meta.hazsol_vs30_rk

    @property
    @lru_cache(maxsize=None)
    def locs(self):
        return self._hazard_meta.locs

    @property
    @lru_cache(maxsize=None)
    def rlz_lt(self):
        return ast.literal_eval(self._hazard_meta.rlz_lt)

    @property
    @lru_cache(maxsize=None)
    def src_lt(self):
        return ast.literal_eval(self._hazard_meta.src_lt)

    @property
    @lru_cache(maxsize=None)
    def nrlzs(self):
        return len(self.rlz_lt['weight'])

    
    
    
    def values(self, location, imt, realization):

        #TODO check location and imt agianst avaialable list
        # if str(realization).isdigit():
        #     nrlz = len(self.rlz_lt['weight'])
        #     for rlz in range(nrlz):
        #         key = encode_key(location=location,imt=imt,realization=rlz)
        #         _ = self._data[key].values[0]
                
        key = encode_key(location=location,imt=imt,realization=realization)
        lvls = self._data[key].values[0].lvls
        vals = self._data[key].values[0].vals
        Values = namedtuple("Values","lvls vals")
        return Values(lvls=lvls,vals=vals)


    def get_hazard_metadata(self):
        q = query.get_hazard_metadata([self._hazard_id])
        return next(q)




