# !/usr/bin/env python3
"""
 Created By:   Jason Herning
 File Name:    aiwater.py
 Description:  CLI Interface
"""

import getpass
import click
import time
from pathlib import Path
from shapely import wkt

import src.product_download_api as pda
import src.geo_utility as gu
from tempfile import TemporaryDirectory
from src.config import PROJECT_DIR, MASK_DIR
from src.api_functions import hyp3_login, grab_subscription
import src.io_tools as io

from src.metadata_class import get_sub_products, populate_cmr_product_shape, get_min_granule_coverage, Product, \
    triage_products_newest, MaskMetadata
from src.asf_cnn import test_model_masked, train_model
from src.model.architecture.masked import create_model_masked
import matplotlib.pyplot as plt
from src.model import load_model, load_history, path_from_model_name
from src.model.architecture.masked import create_model_masked
from src.plots import edit_predictions, plot_predictions, print_summary, view_filters, plot_history

from src.geo_utility import difference, intersection
from src.hyp3lib_functions import data2geotiff, geotiff2data

from src.prepare_data import make_tiles, prepare_mask_data, groom_imgs, move_imgs
import src.identify_water as iw

@click.group()
def cli():
    pass


# TODO: Should work if some dirs already created
@cli.command()
def setup():
    """
    Create data directories
    data/
    -input/
        -products
        -aoi
    -working/
        -datasets
    -output/
        -models
        -mask
        -tensorboard
    """
    io.create_directories()
    click.echo("Data directory created")


# TODO: Add default output_directory and make option.
# TODO: Add loading bar.
@cli.command()
@click.argument('metalink_path')
@click.argument('output_directory')
def download_metalink(metalink_path, output_directory):
    """Download files from products.metalink

    \b
    metalink_path     Path to the metalink file
    output_directory  The directory the products will be saved in
    """
    netrc_path = PROJECT_DIR / '.netrc'

    if netrc_path.exists():
        creds = pda.get_netrc_credentials()
    else:
        print("Input earthdata credentials")
        username = input("username: ")
        password = getpass.getpass(prompt="password: ")
        creds = pda.credentials(username, password)

    pda.download_metalink_products(Path(metalink_path), Path(output_directory), creds)


# TODO: create default file name as granule name with _MASK or _mask appended.
# TODO: make default save directory be the water mask directory
# TODO: Make it so outfile by default looks in mask directory, and if not there checks it as a path in current dir.
@cli.command()
@click.argument('model_path')
@click.argument('vv_path')
@click.argument('vh_path')
@click.argument('outfile')
@click.option('-v', '--verbose', help="keras verbosity", default=1, type=int)
def create_mask(model_path, vv_path, vh_path, outfile, verbose):
    """Create a water mask for an image.
    The image must be dual pol (VV + VH) and must be calibrated. ****** NOTE ******
    create_mask.py contains a memory leak. Use a subprocess call when using main in a loop to prevent memory issues.

    \b
    MODEL_PATH Name of the trained model
    VV_PATH    Path to the calibrated VV tiff
    VH_PATH    Path to the calibrated VH tiff
    OUTFILE    Name of the generated mask
    """
    gu.create_water_mask(model_path, vv_path, vh_path, outfile, verbose)


# TODO: Create vrt file
@cli.command()
@click.argument('model', type=str)
@click.argument('source_dir', type=click.Path())
@click.argument('output_dir', type=click.Path())
@click.argument('name', type=str)
def mask_directory(model, source_dir, output_dir, name):
    """Creates mask of all products in given directory.
       Products must be in original zipfile format."""

    product_list = io.list_products(source_dir)
    print(f"{len(product_list)} products in directory")

    mask_save_directory = Path(output_dir) / name
    if not mask_save_directory.is_dir():
        mask_save_directory.mkdir()

    for product in product_list:
        print(f"Masking {product.name}")
        with TemporaryDirectory() as tmpdir_name:
            vv_path, vh_path = io.extract_from_product(product, Path(tmpdir_name))
            output_file = mask_save_directory / f"{product.stem}.tif"
            gu.create_water_mask(model, str(vv_path), str(vh_path), str(output_file))
            print(f"Mask for {product.stem} is finished")


@cli.command()
@click.argument('model', type=str)
@click.argument('dataset', type=str)
@click.option('-e', '--epochs', default=10, type=int)
def train(model, dataset, epochs):
    # model_path = path_from_model_name(model)

    model = create_model_masked(model)
    history = {"loss": [], "accuracy": [], "val_loss": [], "val_accuracy": []}

    train_model(model, history, dataset, epochs)

@cli.command()
@click.argument('vv_image_path', type=str)
@click.argument('vh_image_path', type=str)
@click.argument('mask_name', type=str)
def identify_water(vv_image_path, vh_image_path, mask_name):
    """identify water using numeric method for training"""
    prod = iw.Product(vv_image_path, vh_image_path)
    iw.show_mask(prod, iw.create_mask(prod.vv_image, prod.vh_image, 0.01))

@cli.command()
@click.argument('first_mask', type=str)
@click.argument('second_mask', type=str)
@click.argument('name', type=str)
def mask_difference(first_mask, second_mask, name):
    """generate difference mask"""
    _, mask1_transform, projection, epsg, data_type, no_data = geotiff2data(first_mask)
    mask1_intersect, mask2_intersect, col, row, bounds = intersection(first_mask, second_mask)
    mask_difference = difference(mask1_intersect, mask2_intersect)
    transform = (bounds[0], mask1_transform[1], 0, bounds[3], 0, mask1_transform[5])
    data2geotiff(mask_difference, transform, projection, data_type, 0, name)

@cli.command()
@click.argument('image', type=str)
@click.argument('tile_size', default=512, type=int)
def tile_image(image, tile_size):
    """tile tif image to tiles of tile_size with padding"""
    make_tiles(image, (tile_size, tile_size))

@cli.command()
@click.argument('directory', type=str)
@click.argument('holdout', default=0.2, type=float)
def divide_dataset(directory, holdout):
    """divide dataset into test and train directories based on holdout"""
    prepare_mask_data(directory, holdout)


@cli.command()
@click.argument('directory', type=str)
@click.argument('holdout', default=0.2, type=float)
def groom_images(directory, holdout):
    """groom images to remove inaccurate masks"""
    groom_imgs(directory)

@cli.command()
@click.argument('directory', type=str)
@click.argument('new_directory', type=str)
def move_images(directory, new_directory):
    """groom images to remove inaccurate masks"""
    move_imgs(directory, new_directory)

@cli.command()
@click.argument('model', type=str)
@click.argument('name', type=str)
@click.option('--id')
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--aoi', type=click.Path(exists=True, readable=True))
@click.option('--min-cover', is_flag=True)
@click.option('--display', is_flag=True)
@click.option('--dry-run', is_flag=True)
@click.option('--output_dir', type=click.Path(), default=MASK_DIR)
def mask_sub(model, name, id, date_start, date_end, aoi, min_cover, display, dry_run, output_dir):
    """Finds list of prodcuts meeting given criteria"""

    api = hyp3_login()  # login if .netrc not found

    # Interactively find sub-id if not given already
    if not id:
        subscription = grab_subscription(api)
        id = subscription['id']

    # Get list of Products objects from subscription
    products = get_sub_products(api, id)

    # Removes products not in date bounds
    if date_start and date_end:
        products = [product for product in products if product.time_bounds(date_start, date_end)]

    aoi_poly = io.polygon_from_shapefile(aoi)
    # print(f"aoi_poly={aoi_poly}")
    if aoi:
        products_inbounds = []
        for product in products:
            product.get_shape_cmr()
            if product.shape is None:
                continue
            if product.intersects(aoi_poly):
                products_inbounds.append(product)

        products = products_inbounds

    print("Products after checking shape bounds")
    print(f"{len(products)} products in list")
    # for product in products:
    #     print(product.granule)

    if min_cover:
        min_products = get_min_granule_coverage(products, aoi_poly)
        products = min_products

    print(f"{len(products)} products after getting min cover by aoi")
    # for product in products:
    #     print(product.granule)

    if display:
        x, y = aoi_poly.exterior.xy
        plt.plot(x, y)
        for p in products:
            x, y = p.shape.exterior.xy
            plt.plot(x, y)
        plt.show()

    metadata = MaskMetadata(name=name, model=model, aoi=aoi_poly, start=date_start, end=date_end, products=products)
    # print(metadata.to_json())

    if not dry_run:
        netrc_path = PROJECT_DIR / '.netrc'
        if netrc_path.exists():
            creds = pda.get_netrc_credentials()
        else:
            print("Input earthdata credentials")
            username = input("username: ")
            password = getpass.getpass(prompt="password: ")
            creds = pda.credentials(username, password)

        mask_save_directory = Path(output_dir) / name
        if not mask_save_directory.is_dir():
            mask_save_directory.mkdir()

        # with TemporaryDirectory() as tmpdir_name:
        #     temp_product_dir = Path(tmpdir_name)
        #     for product in products:
        #         print(f"Downloading {product.url}")
        #         pda.download_product(product.url, temp_product_dir, creds)
        #
        #         product_path = temp_product_dir / product.name
        #
        #         vv_path, vh_path = io.extract_from_product(product_path, temp_product_dir)
        #         output_file = mask_save_directory / f"{product_path.stem}.tif"
        #         gu.create_water_mask(model, str(vv_path), str(vh_path), str(output_file))
        #         print(f"Mask for {product_path.stem} is finished")

        for product in products:
            with TemporaryDirectory() as tmpdir_name:
                temp_product_dir = Path(tmpdir_name)

                print(f"Downloading {product.url}")
                pda.download_product(product.url, temp_product_dir, creds)
                product_path = temp_product_dir / product.name

                print(f"Product_path = {str(product_path)}")

                vv_path, vh_path = io.extract_from_product(product_path, temp_product_dir)

                output_file = mask_save_directory / f"{product.stem}.tif"
                print(f"output_file = {str(output_file)}")

                print(f"Creating mask {product.stem}")
                gu.create_water_mask(model, str(vv_path), str(vh_path), str(output_file))
                print(f"Mask for {product.stem} is finished")

        print(f"Mask {name} is finished")



    # for product in product_list:
    #     print(f"Masking {product.name}")
    #     with TemporaryDirectory() as tmpdir_name:
    #         vv_path, vh_path = io.extract_from_product(product, Path(tmpdir_name))
    #         output_file = mask_save_directory / f"{product.stem}.tif"
    #         gu.create_water_mask(model, str(vv_path), str(vh_path), str(output_file))
    #         print(f"Mask for {product.stem} is finished")

def model_history(model):
    """groom images to remove inaccurate masks"""
    plot_history(model, load_history(model))

@cli.command()
@click.argument('model', type=str)
def model_filters(model):
    """groom images to remove inaccurate masks"""
    view_filters(model)

@cli.command()
@click.argument('model', type=str)
def model_summary(model):
    """groom images to remove inaccurate masks"""
    print_summary(model)



if __name__ == '__main__':
    cli()
