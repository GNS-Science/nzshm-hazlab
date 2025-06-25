"""This package provieds the loader classes for retrievign hazard curves from a number of sources.

Modules:
    dynamo_loader: Defines the DynamoHazardLoader class.
    oq_csv_loader: Defines the OQCSVHazardLoader and OQCSVDisaggLoader classes.
    ths_loader: Defines the THSHazardLoader class.
"""

from .dynamo_loader import DynamoHazardLoader
from .oq_csv_loader import OQCSVDisaggLoader, OQCSVHazardLoader
from .ths_loader import THSHazardLoader
