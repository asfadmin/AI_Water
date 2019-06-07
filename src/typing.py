"""
Define custom type aliases here.
"""
from typing import Dict, List, Tuple

History = Dict[str, List[float]]
ConfMatrix = List[List[float]]
DatasetMetadata = List[Tuple[str, str]]
