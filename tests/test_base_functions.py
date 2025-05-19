import nzshm_hazlab.base_functions as base_functions
import pytest


imt_period_type = [
    ("PGA", 0, "acc"),
    ("SA(0.1)", 0.1, "acc"),
    ("SA(1.0)", 1.0, "acc"),
    ("SA(1.5)", 1.5, "acc"),
    ("SA(3.1234)", 3.1234, "acc"),
    ("PGD", 0, "disp"),
    ("PGV", 0, "vel"),
    ("SV(10.4)", 10.4, "vel"),
]
imt_period = [ipt[0:2] for ipt in imt_period_type]
@pytest.mark.parametrize("imt,period", imt_period)
def test_period_from_imt(imt, period):
    assert base_functions.period_from_imt(imt) == period

@pytest.mark.parametrize("imt,period,type", imt_period_type)
def test_imt_from_period(imt, period,type):
    assert base_functions.imt_from_period(period, type) == imt