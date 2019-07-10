import argparse
import pathlib

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RectangleSelector, Slider
from osgeo import gdal

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', help='Path to the .SAFE file')

    args = parser.parse_args()

    measurement = pathlib.Path(args.image_path) / 'measurement'
    vv = next(measurement.glob('*-vv-*.tiff'))
    vh = next(measurement.glob('*-vh-*.tiff'))

    # Read data
    print("Reading files")

    tile_size = 5000
    bins = 75

    vv_image = gdal.Open(str(vv)
                         ).ReadAsArray()[0:tile_size, 0:tile_size].clip(0, 512)
    vh_image = gdal.Open(str(vh)
                         ).ReadAsArray()[0:tile_size, 0:tile_size].clip(0, 512)

    vv_array = vv_image.flatten()
    vh_array = vh_image.flatten()

    # bins = 300
    # max = max(np.max(vv_array), np.max(vh_array))
    #
    # # Make histogram
    #
    # print("Making indecies")
    # zipped = np.dstack((vv_array, vh_array))[0]
    #
    # del vv_array
    # del vh_array
    #
    # zipped *= (bins - 1)
    # zipped = zipped // max
    #
    # print("counting bins")
    # hist = np.apply_along_axis(
    #     lambda x: np.bincount(x, minlength=bins), axis=1, arr=zipped
    # )

    selected = ()

    plt.figure()
    plt.subplot(1, 2, 1)
    plt.title('VV')
    plt.imshow(vv_image, cmap=plt.get_cmap('gist_gray'))

    plt.subplot(1, 2, 2)
    plt.title('VH')
    plt.imshow(vh_image, cmap=plt.get_cmap('gist_gray'))

    fig, ax = plt.subplots()

    plt.subplots_adjust(left=0.25, bottom=0.25)

    sbin = Slider(
        plt.axes([0.25, 0.15, 0.65, 0.03]),
        'Bins',
        1,
        500,
        valstep=1,
        valinit=bins
    )

    def update_hist(val):
        plt.hist2d(vv_array, vh_array, bins=val, cmap=plt.cm.jet)
        fig.canvas.draw_idle()

    sbin.on_changed(update_hist)

    button = Button(
        plt.axes([0.8, 0.025, 0.1, 0.04]), 'Mask', hovercolor='0.975'
    )

    def show_mask(event):
        if not selected:
            return

        (vv_min, vh_min), (vv_max, vh_max) = selected
        mask = np.zeros(vv_image.shape)
        indecies = np.where(
            np.logical_and(
                np.logical_and(vv_image >= vv_min, vv_image < vv_max),
                np.logical_and(vh_image >= vh_min, vh_image < vh_max)
            )
        )
        mask[indecies] = 1

        plt.figure()
        plt.imshow(mask)
        plt.show()

    button.on_clicked(show_mask)

    hist_ax = plt.axes()
    plt.xlabel('VV')
    plt.ylabel('VH')
    plt.hist2d(vv_array, vh_array, bins=bins, cmap=plt.cm.jet)

    def line_select_callback(eclick, erelease):
        global selected
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        selected = ((x1, y1), (x2, y2))

    rs = RectangleSelector(
        hist_ax,
        line_select_callback,
        drawtype='box',
        useblit=False,
        button=[1],
        minspanx=5,
        minspany=5,
        spancoords='pixels',
        interactive=True
    )
    plt.colorbar()
    plt.show()
