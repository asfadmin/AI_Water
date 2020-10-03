# !/usr/bin/env python3
"""
 Created By:   Jason Herning
 Date Started: 08-05-2020
 Last Updated: 08-05-2020
 File Name:    aiwater.py
 Description:  Main file holding all the argparse
"""

import click
from pathlib import Path
from src.product_download_api import download_metalink_products
import src.geo_utility as gu


@click.group()
def cli():
    pass


# TODO: Add default output_directory and make option.
# TODO: Add loading bar.
@cli.command()
@click.argument('metalink_path')
@click.argument('output_directory')
def download_metalink(metalink_path, output_directory):
    """Download files from products.metalink"""
    download_metalink_products(Path(metalink_path), Path(output_directory))


# TODO: create default file name as granule name with _MASK or _mask appended.
# TODO: make default save directory be the water mask directory
# TODO: Make it so outfile by default looks in mask directory, and if not there checks it as a path in current dir.
@cli.command()
@click.argument('model_path')
@click.argument('vv_path')
@click.argument('vh_path')
@click.argument('outfile')
@click.option('-v', '--verbose', help="keras verbosity",default=1, type=int)
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



# SCRIPTS TO ADD/CREATE

# TODO: MUST create vv/vh tiles along with their statistical water mask
# TODO: Can take products.metalink file as input
# TODO: store in proper dataset folder unless told otherwise
# TODO: Generates a metadata.json file with info on the dataset
@cli.command()
def create_dataset():
    click.echo("NEEDS TO BE IMPLEMENTED!")

# TODO: Combine with download_metalink
"""
    Options/flags to add:
        - date/time
        - frame
        - path 
"""
@cli.command()
def download_subscription():
    click.echo("NEEDS TO BE IMPLEMENTED!")


@cli.command()
def train():
    click.echo("NEEDS TO BE IMPLEMENTED!")

@cli.command()
def test():
    click.echo("NEEDS TO BE IMPLEMENTED!")

# tiles the dataset
@cli.command()
def create_dataset():
    click.echo("NEEDS TO BE IMPLEMENTED!")

# use matplot lib to groom the mask images
@cli.command()
def groom_dataset():
    click.echo("NEEDS TO BE IMPLEMENTED!")


# print stats found in info_model
@cli.command()
def model_info():
    click.echo("NEEDS TO BE IMPLEMENTED!")

@cli.command()
def list():
    """List various data from project. Products, masks, datasets, models"""
    click.echo("NEEDS TO BE IMPLEMENTED!")

# MAY not end up needing
@cli.command()
def compress_datasets():
    click.echo("NEEDS TO BE IMPLEMENTED!")
# def compress_wrapper(args: Namespace) -> None:
#     """Wrapper for script compress_datasets."""
#     directory_path = os.path.join(DATASETS_DIR, args.directory)
#     compress_datasets(directory_path, args.holdout)


if __name__ == '__main__':
    cli()
