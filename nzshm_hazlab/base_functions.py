"""This module provides basic functions for parsing intensity measure type strings and probability-rate conversions."""

import math
import re
from enum import Enum
from typing import TYPE_CHECKING, Literal

import numpy as np

if TYPE_CHECKING:
    import numpy.typing as npt


class _GMType(Enum):
    acc = "A"
    disp = "D"
    vel = "V"


def prob_to_rate(prob: 'npt.NDArray', inv_time: float) -> 'npt.NDArray':
    """Convert probability of exceedance to rate assuming Poisson distribution.

    Args:
        prob: probability of exceedance
        inv_time: time period for probability (e.g. 1.0 for annual probability)

    Returns:
        return rate in inv_time
    """
    return -np.log(1.0 - prob) / inv_time


def rate_to_prob(rate: 'npt.NDArray', inv_time: float) -> 'npt.NDArray':
    """Convert rate to probabiility of exceedance assuming Poisson distribution.

    Args:
        rate: rate over inv_time
        inv_time: time period of rate (e.g. 1.0 for annual rate)

    Returns:
        probability of exceedance in inv_time
    """
    return 1.0 - np.exp(-inv_time * rate)


def period_from_imt(imt: str) -> float:
    """Convert intensity measure type string to a time period.

    Peak values (e.g. "PGA", "PGV") are converted to 0 seconds.

    Args:
        imt: The intensity measure type (e.g. "PGA", "SA(1.0)", "SD(5.0)").

    Returns:
        The period in seconds.
    """
    if imt[0:2] == "PG":
        period = 0.0
    else:
        period = float(re.split('\\(|\\)', imt)[1])
    return period


def imt_from_period(period: float, imt_type: Literal["acc", "vel", "disp"]) -> str:
    """Convert shaking period to an intensity measure type string.

    Valid values of the IMT type are "acc", "vel", and "disp".

    Args:
        period: The shaking period in seconds.
        imt_type: The type of intensity measure ("acc", "vel", "disp").

    Returns:
        The intensity measure type string.
    """
    prefix = _GMType[imt_type.lower()].value
    if period == 0:
        return f"PG{prefix}"
    imt = f"{period:.10g}"
    if "." not in imt and "e" not in imt:
        imt += ".0"
    return f"S{prefix}({imt})"


def rp_from_poe(poe: float, inv_time: float) -> float:
    """Convert a proability of exceedance to a return period using the Poison proability function.

    Args:
        poe: The fractional probability of exceedance.
        inv_time: The investigation time.

    Returns:
        The repeat period in the same units as inv_time (e.g. years).

    Example:
        To find the return period for a 10% probability of exceedance in 50 years

        ```py
        >>> rp_from_poe(0.1, 50)
        474.56107905149526
        ```
    """
    return -inv_time / math.log(1 - poe)


def poe_from_rp(rp: float, inv_time: float) -> float:
    """Convert a return period to a propability of exceedance using the Poison probablity function.

    Args:
        rp: Return period.
        inv_time: Inverstigation time.

    Returns:
        Fractional probability of exceedance.

    Example:
        To find the probability of exceedance in 50 years for a return period of 500 years
        ```py
        >>> poe_from_rp(500.0, 50.0)
        0.09516258196404048
        ```
    """
    return 1 - math.exp(-inv_time / rp)


def convert_poe(poe_in: float, inv_time_in: float, inv_time_out: float) -> float:
    """Convert probablity of exceedance from one investigation time to another.

    Args:
        poe_in: Origional probability of exceedance.
        inv_time_in: Origional investigation time.
        inv_time_out: Desired investigation time.

    Returns:
        The probability of exceedance for inv_time_out.
    """
    return poe_from_rp(rp_from_poe(poe_in, inv_time_in), inv_time_out)


def calculate_hazard_at_poe(poe: float, imtls: 'npt.NDArray', poes: 'npt.NDArray') -> float:
    """Calculate the hazard at a given probability of exceedance using interpolation.

    A hazard curve and a desired probablity at which to calculate hazard are provided.
    No conversion of time is performed (e.g. if the hazard curve is in annual PoE, the desired poe must also be annual),
    use the convert_poe function to convert probabilty investigation times.

    Args:
        poe: The probability of exceedance at which to calculate hazard.
        imtls: The shaking values of the hazard curve.
        poes: The probability values of the hazard curve.

    Returns:
        The hazard (shaking value) at the desired probablity of exceedance.
    """
    return math.exp(np.interp(np.log(poe), np.flip(np.log(poes)), np.flip(np.log(imtls))))
