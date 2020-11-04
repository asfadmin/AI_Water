"""
 Created By:   Jason Herning
 File Name:    aiwater.py
 Description:  class to store info on sar products/granules
"""

import re
import json
import dataclasses as dc
from dataclasses import asdict
from shapely.geometry import Polygon
from datetime import datetime


@dc.dataclass()
class Product:
    name: str
    shape: Polygon = None
    start: datetime = None
    end: datetime = None

    def __post_init__(self):
        self.product_time_regex = re.compile(
            r"S.*1SDV_(?P<start_year>\d{4})(?P<start_month>\d{2})(?P<start_day>\d{2})T(?P<start_hour>\d{2})("
            r"?P<start_minute>\d{2})(?P<start_second>\d{2})_(?P<end_year>\d{4})(?P<end_month>\d{2})(?P<end_day>\d{2})T("
            r"?P<end_hour>\d{2})(?P<end_minute>\d{2})(?P<end_second>\d{2})_*")
        #         self.start = make_start(name)
        #         self.end = make_end(name)
        self.start = self.make_start(self.name)
        self.end = self.make_end(self.name)

    def __make_start(self, product_name) -> datetime:

        regex_match = re.match(self.product_time_regex, product_name)
        time_dict = regex_match.groupdict()
        for k, v in time_dict.items():
            time_dict[k] = int(v)

        return datetime(time_dict["start_year"], time_dict["start_month"], time_dict["start_day"],
                        time_dict["start_hour"], time_dict["start_minute"], time_dict["start_second"])

    def __make_end(self, product_name) -> datetime:

        regex_match = re.match(self.product_time_regex, product_name)
        time_dict = regex_match.groupdict()
        for k, v in time_dict.items():
            time_dict[k] = int(v)

        return datetime(time_dict["end_year"], time_dict["end_month"], time_dict["end_day"],
                        time_dict["end_hour"], time_dict["end_minute"], time_dict["end_second"])

    def to_json(self):
        metadata = asdict(self)
        metadata['start'] = self.start.isoformat()
        metadata['end'] = self.end.isoformat()
        metadata['shape'] = str(self.shape)

        #         for key in list(metadata):
        #             if key is datetime:
        #                 metadata[key] = metadata[key].isoformat()
        #                 print(f"TEST: {key}= {metadata[key]}")
        return json.dumps(metadata)

