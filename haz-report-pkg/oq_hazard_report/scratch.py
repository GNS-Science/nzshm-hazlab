
 elif type(ast.ast.literal_eval(k.realization)) is list:
            rlzs = [f'{r:05d}' for r in ast.literal_eval(k.realization)]
            q = query.get_hazard_rlz_curves_v2(self._hazard_id,[k.imt],[k.location],[rlzs])