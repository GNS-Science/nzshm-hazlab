import numpy as np
import pytest

import nzshm_hazlab.base_functions as base_functions

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
def test_imt_from_period(imt, period, type):
    assert base_functions.imt_from_period(period, type) == imt


@pytest.mark.filterwarnings("ignore:divide by zero encountered in log")
def test_prob_to_rate():
    prob = np.array([0.0, 0.5, 1.0])
    rate = base_functions.prob_to_rate(prob, 1.0)
    rate_expected = np.array([0.0, -np.log(1.0 - 0.5), np.inf])
    np.testing.assert_allclose(rate, rate_expected)


def test_rate_to_prob():
    rate = np.array([0.0, 1.0])
    prob = base_functions.rate_to_prob(rate, 1.0)
    prob_expected = np.array([0.0, 1.0 - np.exp(-1.0)])
    np.testing.assert_allclose(prob, prob_expected)
