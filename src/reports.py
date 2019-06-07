import csv
from typing import Any, Dict, List, TextIO


def write_dict_to_csv(data: Dict[Any, Any], f: TextIO) -> None:
    writer = csv.writer(f)

    rows: List[List[Any]] = []
    for header, values in data.items():
        if not rows:
            rows.append([header])
            for value in values:
                rows.append([value])
        else:
            rows[0].append(header)
            for i, value in enumerate(values):
                rows[i + 1].append(value)

    writer.writerows(rows)
