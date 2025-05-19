import math
import re
from enum import Enum

import numpy as np


class GMType(Enum):
    ACC = "A"
    DISP = "D"
    VEL = "V"


def period_from_imt(imt: str) -> float:
    if imt[0:2] == "PG":
        period = 0.0
    else:
        period = float(re.split('\\(|\\)', imt)[1])
    return period


def imt_from_period(period: float, type: str) -> str:
    prefix = GMType[type.upper()].value
    if period == 0:
        return f"PG{prefix}"
    imt = f"{period:.10g}"
    if "." not in imt and "e" not in imt:
        imt += ".0"
    return f"S{prefix}({imt})"


def rp_from_poe(poe: float, inv_time: float) -> float:
    return -inv_time / math.log(1 - poe)


def poe_from_rp(rp: float, inv_time: float) -> float:
    return 1 - math.exp(-inv_time / rp)


def convert_poe(poe_in: float, inv_time_in: float, inv_time_out: float) -> float:
    return poe_from_rp(rp_from_poe(poe_in, inv_time_in), inv_time_out)


def compute_hazard_at_poe(poe: float, poes: np.ndarray, imtls: np.ndarray) -> float:
    return math.exp(np.interp(np.log(poe), np.flip(np.log(poes)), np.flip(np.log(imtls))))
