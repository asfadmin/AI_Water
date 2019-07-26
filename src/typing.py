"""
    Define custom type aliases here.
"""
from typing import Dict, List, Tuple

History = Dict[str, List[float]]
BinaryDatasetMetadata = List[Tuple[str, str]]
MaskedDatasetMetadata = List[Tuple[str, str, str]]
