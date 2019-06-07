"""
Define custom type aliases here.
"""
from typing import Any, Dict, List, Tuple, Union

History = Dict[str, List[float]]
ConfMatrix = List[List[float]]
DatasetMetadata = List[Tuple[str, str]]
JsonParsed = Union[Dict[Any, Any], List[Any]]
