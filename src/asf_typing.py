"""
    Define custom type aliases here.
"""
from typing import Dict, List, Tuple
from collections import namedtuple

History = Dict[str, List[float]]
MaskedDatasetMetadata = List[Tuple[str, str, str]]
sar_set = namedtuple('sar_set', ['mask', 'vh', 'vv'])
