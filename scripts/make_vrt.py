import json
import os
import re
from argparse import ArgumentParser
from collections import Counter

from osgeo import gdal

PROJECTION = re.compile(r'ID\[\"([A-Z]+)\",([0-9]+)\]')


def main(path: str, vrtname: str):
    path_and_proj = []

    proj_counter = Counter()
    for fname in os.listdir(path):
        if not fname.endswith(".tif"):
            continue

        fpath = os.path.join(path, fname)
        info = gdal.Info(fpath, options=['-json'])
        info = json.loads(info)['coordinateSystem']['wkt']

        m = re.findall(PROJECTION, info)
        typ, zone = m[-1]
        proj = f"{typ}:{zone}"
        path_and_proj.append((fpath, proj))

        proj_counter.update([proj])

    dst_proj, count = proj_counter.most_common(1)[0]
    print(f"Most common projection with {count} votes: {dst_proj}")
    for fpath, proj in path_and_proj:
        if proj == dst_proj:
            continue
        print(f"Reprojecting {fpath}")
        gdal.Warp(fpath, fpath, srcSRS=proj, dstSRS=dst_proj)

    vrtpath = os.path.join(path, vrtname)
    print(f"Creating VRT: {vrtpath}")
    gdal.BuildVRT(vrtpath, list(map(lambda x: x[0], path_and_proj)))


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument("path", help="path to the folder with individual tiffs")
    p.add_argument("vrtname", help="name of the resulting vrt file")

    args = p.parse_args()
    main(args.path, args.vrtname)
