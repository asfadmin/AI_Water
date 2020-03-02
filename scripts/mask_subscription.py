"""
 McKade Sorensen
 8-20-19
 mask_subscription.py
 This script creates a mask from an ASF HYP3 subscription. The user must
 already have a subscription in HYP3 with finished products.
"""
import time
from argparse import ArgumentParser, Namespace

from asf_hyp3 import API

from scripts.make_vrt import main as vrt
from src.api_functions import hyp3_login
from src.user_class import User
from src.mask_class import Mask

from datetime import datetime

<<<<<<< HEAD
def make_dirs(dir: str) -> str:
    """ If not already created this function creates the mask directory,
        and the directory the user inputs. The mask directory will contain
        subdirectories containing all the masks within
        individual subdirectories. Subdirectories are created each time
        the script is ran. """

    users_dir = os.path.join('mask', dir)
    if not os.path.isdir('mask'):
        os.mkdir('mask')
    if not os.path.isdir(users_dir):
        os.mkdir(users_dir)
    return users_dir


def mask_products(products: List, users_path: str, model_path: str) -> None:
    """ Takes a list of products generated from the HYP3 API,
        the path to save the masks, and the path to a model (.h5 file).
        The function then creates a mask for each product contained in
        the product list. """

    ZIP_REGEX = re.compile(r'(.*).zip')
    SAR_REGEX = re.compile(r'(.*)_(VH|VV).tif')
    for i, product in enumerate(products):
        download_prouducts(products, i, product)
        try:
            with ZipFile(product['name'], 'r') as zf:
                zf.extractall()
            zf.close()
        except FileNotFoundError:
            continue

        m = re.match(ZIP_REGEX, product['name'])
        folder = m.groups()

        for file in os.listdir(folder[0]):
            img = os.path.join(folder[0], file)
            m = re.match(SAR_REGEX, file)

            if not m or file.endswith('.xml'):
                try:
                    os.remove(img)
                    continue
                except FileNotFoundError and IsADirectoryError:
                    continue

            _, band = m.groups()

            if band == "VH":
                vh_img = img
                continue
            vv_img = img

        output = os.path.join(users_path, f"{folder[0]}_{i}.tif")
        # Creating mask
        call(f"python scripts/create_mask.py {model_path} {vv_img} {vh_img} {output}".split())
        shutil.rmtree(folder[0])
        os.remove(f"{folder[0]}.zip")


def mask_sub(sub_id: str, dir: str, model: str,  api: API) -> None:
    """ mask_sub masks a given subscription  """
    count = 0
    while True:
        print(f"Page: {count + 1}")





        products = api.get_products(
            sub_id=sub_id, page=count, page_size=500
        )


    

        products = triage_products(products)



        mask_products(products, dir, model)
        count += 1
=======
def create_mask(args: Namespace, api: API) -> None:
    start_time = time.time()
>>>>>>> dmsorensen_dev

    user = User(args.name, args.model, api)
    mask = Mask(user, args.name)

    mask.mask_subscription()
    vrt(mask.user.mask_path, f"{mask.mask_name}.vrt")

<<<<<<< HEAD



def product_middle_time(product_name):
    """takes in product time; uses regex to take out the date/time of the file name
       then returns a date time object of middle time between the start and end times"""

    PRODUCT_REGEX = re.compile(r'S.*1SDV_(?P<start_year>\d{4})(?P<start_month>\d{2})(?P<start_day>\d{2})T(?P<start_hour>\d{2})(?P<start_minute>\d{2})(?P<start_second>\d{2})_(?P<end_year>\d{4})(?P<end_month>\d{2})(?P<end_day>\d{2})T(?P<end_hour>\d{2})(?P<end_minute>\d{2})(?P<end_second>\d{2})_[0-9]*_.*.zip')
    
    m = re.match(PRODUCT_REGEX, product_name)
    dt = m.groupdict()

    # converts all dates/times values in dictionary from int to string
    for k, v in dt.items(): dt[k] = int(v)

    start = datetime(dt["start_year"], dt["start_month"], dt["start_day"],
                     dt["start_hour"], dt["start_minute"], dt["start_second"])
            
    end = datetime(dt["end_year"], dt["end_month"], dt["end_day"],
                   dt["end_hour"], dt["end_minute"], dt["end_second"])  


    #calculates middle datetime
    middle = start + (end - start)/2


    return middle




def triage_products(products):
    """Takes list of dictionary (products), and then orders them from
       least to most recent based on their start time"""


    return sorted(products, key=lambda product: product_middle_time(product['name']))









def main(args: Namespace, api: API) -> None:
    """ main creates a vrt from a users subscription. """
    start_time = time.time()
    subscription = grab_subscription(api)
    dir = make_dirs(args.name)
    mask_sub(subscription['id'], dir, args.model, api)
    vrt(dir, f"{args.name}.vrt")
=======
>>>>>>> dmsorensen_dev
    end_time = time.time()
    print(end_time - start_time)


if __name__ == '__main__':
    p = ArgumentParser()

    p.add_argument('model', help='Path to model')
    p.add_argument('name', help='Name of mask')
    p.set_defaults(func=create_mask)

    args = p.parse_args()
    if hasattr(args, 'func'):
        api = hyp3_login()
        args.func(args, api)
    else:
        p.print_help()
