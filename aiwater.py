# !/usr/bin/env python3
"""
 Created By:   Jason Herning
 File Name:    aiwater.py
 Description:  CLI Interface
"""

import getpass
import click
from pathlib import Path
import src.product_download_api as pda
import src.geo_utility as gu
from tempfile import TemporaryDirectory
from src.config import PROJECT_DIR
from src.api_functions import hyp3_login, grab_subscription
import src.io_tools as io

from src.mask_class import Mask
from src.user_class import User

from src.asf_cnn import test_model_masked, train_model
from src.model import load_model, path_from_model_name
from src.model.architecture.masked import create_model_masked
from src.plots import edit_predictions, plot_predictions

from src.geo_utility import difference, intersection
from src.hyp3lib_functions import data2geotiff, geotiff2data

from src.prepare_data import make_tiles, prepare_mask_data

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
    """Download files from products.metalink"""

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


# # TODO: MUST create vv/vh tiles along with their statistical water mask
# # TODO: Can take products.metalink file as input
# # TODO: store in proper dataset folder unless told otherwise
# # TODO: Generates a metadata.json file with info on the dataset
# @cli.command()
# @click.argument('source', type=click.Path())
# @click.argument('name', type=str)
# def create_dataset_metalink(source, name):
#     netrc_creds = pda.get_netrc_credentials()

#     with TemporaryDirectory() as tmpdir_name:
#         print(f'created temporary directory: {tmpdir_name}')
#         pda.download_metalink_products(source, Path(tmpdir_name), netrc_creds)

#     click.echo("NEEDS TO BE IMPLEMENTED!")

# @cli.command()
# @click.argument('model', type=str)
# @click.argument('name', type=str)
# @click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]))
# @click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]))
# def mask_subscription(model, name, date_start, date_end):
#     api = hyp3_login()

#     # date_start = date_start.date()
#     # date_end = date_end.date()

#     user = User(name, model, api)
#     mask = Mask(user, name, date_start, date_end)

#     mask.mask_subscription()
#     click.echo(f"Start: {date_start}, End: {date_end} ")



# @cli.command()
# @click.argument('model', type=str)
# @click.argument('name', type=str)
# @click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]))
# @click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]))
# def mask_hyp3(model, name, date_start, date_end):
#     api = hyp3_login()
#     subscription = grab_subscription(api)
#     sub_id = subscription['id']
#     date_start = date_start.date()
#     date_end = date_end.date()
#     click.echo(f"Start: {date_start}, End: {date_end} ")
    
if __name__ == '__main__':
    cli()
