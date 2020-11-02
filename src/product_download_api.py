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
from collections import namedtuple
import requests
import getpass
from src.config import PROJECT_ROOT

# TODO: Move functions into a Class


@dataclass
class MetalinkProduct:
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


def metalink_product_generator(metalink_path: Path):
    """Takes in a Path to a metalink file (products.metalink).
       Generates ProductZipFiles objects that holds the
       metadata for each product."""

    # ns is used to handle the namespace of the xml (products.metalink) file.
    ns = {'': 'http://www.metalinker.org/'}

    tree = ET.parse(str(metalink_path))

    for file in tree.findall('.//files/file', ns):
        name = file.get('name')
        url = file.find('resources/url', ns).text
        hash = file.find('verification/hash', ns).text
        size = int(file.find('size', ns).text)

        yield MetalinkProduct(name, url, hash, size)


# TODO: add path to .netrc (Just in case)
# TODO: Split into get_pw and get_un function
def get_netrc_credentials() -> credentials:
    """Returns credentials from .netrc file."""

    netrc_path = PROJECT_ROOT / '.netrc'

    if netrc_path.exists():
        with open('.netrc', 'r') as f:
            contents = f.read()
        username = contents.split(' ')[3]
        password = contents.split(' ')[5].split('\n')[0]
    else:
        print("Input earthdata credentials")
        username = input("username: ")
        password = getpass.getpass(prompt="password: ")

    return credentials(username, password)


def get_redirect_url(url: str) -> str:
    response_redirect = requests.get(url)
    return response_redirect.url


# TODO: add credentials as input
# TODO: MetalinkProduct class as input to get file size for print log???
# TODO: Add progress bar (TQDM)
# TODO: Split function. creates get_redirect
# TODO: *************REMINDER***************************** have creds input normally. Not with function call !!! THATS THE FIX
# TODO: Should not overrite existing files. Instead tack on a (1), (2), etc
def download_product(product_url: str, save_directory: Path, creds: credentials) -> None:
    """Download sar product from given url."""

    filename = product_url.split('/')[-1]
    save_path = save_directory / filename

    # Authenticate and then get redirect
    response_redirect = requests.get(product_url)
    redirect_url = response_redirect.url

    # authenticate with .netrc and then Download fjle from redirect_url
    with requests.get(redirect_url, stream=True, auth=(creds.username, creds.password)) as response:
        with open(save_path, 'wb') as f:
            print(f"Downloading {filename}")

            # Downloads files in chucks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        f.close()


def download_metalink_products(metalink_path: Path, save_directory_path: Path, creds: credentials):
    """Download all products from metalink file (products.metalink)."""
    for product in metalink_product_generator(metalink_path):
        download_product(product.url, save_directory_path, creds)
