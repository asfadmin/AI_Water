"""
 Created By:   Jason Herning
 Date Created: 08-27-2020
 File Name:    product_download_api.py
 Description:  functions for downloading from products.metalink file
"""

import xml.etree.ElementTree as ET
from typing import List
from pathlib import Path
from dataclasses import dataclass
import xmltodict
from collections import namedtuple
from subprocess import PIPE, call


# TODO: Move functions into a Class



@dataclass
class ProductZipFile:
    """Object to hold data for each file in a products.metalink file."""
    name: str
    url: str
    hash: str
    size: int

# namedtuple to store username and password
credentials = namedtuple('credentials', 'username password')

# TODO: probably not needed. Will likely delete later.
def metalink_to_list(metalink_path: str) -> List:
    """Takes path to metalink file as input, returns a list of urls of zip files to be downloaded.
       Designed to work with metalink downloaded from hyp3. The current
       file name convention from hype is simply 'products.metalink'. """
    tree = ET.parse(metalink_path)
    zip_urls = [url.text for url in tree.findall(".//*[@type='http']")]
    return zip_urls


def metalink_product_generator(metalink_path: Path) -> ProductZipFile:
    """Takes in a Path to a metalink file (products.metalink).
       Generates ProductZipFiles objects that holds the
       metadata for each product."""

    # ns is used to handle the namespace of the xml (products.metalink) file
    ns = {'': 'http://www.metalinker.org/'}

    tree = ET.parse(str(metalink_path))

    for file in tree.findall('.//files/file', ns):
        name = file.get('name')
        url = file.find('resources/url', ns).text
        hash = file.find('verification/hash', ns).text
        size = int(file.find('size', ns).text)

        yield ProductZipFile(name, url, hash, size)


# TODO: add path to .netrc (Just in case)
# TODO: Split into get_pw and get_un function
# TODO: Make Unit test!
def get_netrc_credentials() -> credentials:
    """Returns credentials from .netrc file."""
    with open('.netrc', 'r') as f:
        contents = f.read()
    username = contents.split(' ')[3]
    password = contents.split(' ')[5].split('\n')[0]

    return credentials(username, password)

# TODO: Get rid of gross subprocess call! (request was far too complicated)
# TODO: add credentials as input
def download_product(product_url: str, save_directory: Path = Path.cwd()) -> None:
    """Downloads the the file from the given ProductZipFile. saves to save_directory Path"""

    username, password = get_netrc_credentials()

    args = ['wget', '-c', '-q', '--show-progress', f"--http-user={username}", f"--http-password={password}",
            product_url, f"-P {str(save_directory)}"]
    call(args, stdout=PIPE)

# TODO: Build Function!
def download_products():
    return None
