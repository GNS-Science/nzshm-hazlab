"""This package provieds the loader classes for retrievign hazard curves from a number of sources.

Modules:
    dynamo_loader: Defines the DynamoLoader class.
    oq_csv_loader: Defines the OQCSVLoader class.
    ths_loader: Defines the THSLoader class.
"""

from .dynamo_loader import DynamoLoader
from .oq_csv_loader import OQCSVLoader
from .ths_loader import THSLoader
