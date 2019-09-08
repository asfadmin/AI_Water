"""
 tremendous.py # TODO: UPDATE NAME
 McKade Sorensen
 8-20-19
 Allows a user to create a massive water mask
"""
import os
import re
from argparse import ArgumentParser, Namespace
from datetime import date
from typing import Dict, List

from asf_hyp3 import API
from src.api_functions import (
    display_subscriptions, download_granules, hyp3_login
)

# from prepare_data.py import make_tiles

# from make_vrt import main as vrt


def make_dirs(dir: str) -> str:
    users_dir = os.path.join('mask', dir)
    if not os.path.isdir('mask'):
        os.mkdir('mask')
    if not os.path.isdir(users_dir):
        os.mkdir(users_dir)
    return users_dir


def check_dates(users_date: str) -> bool:
    """ Checks the format of a date and returns a bool"""
    DATE_REGEX = re.compile(r'([0-9]+)/([0-9]+)/([0-9]+)')
    m = re.match(DATE_REGEX, users_date)

    try:
        year, month, day = m.groups()
    except AttributeError:
        print('Please insert a date')
        return False

    if not m:
        print('In correct format.')
        return False

    if len(day) != 2 or int(day) > 31 or int(day) < 1:
        print('Day format is incorrect')
        return False

    if len(month) != 2 or int(month) > 12 or int(day) < 1:
        print('Month format is incorrect')
        return False

    if len(year) != 4 or int(year) > date.today().year or int(year) < 1992 or int(day) < 1:
        if int(year) < 1992:
            print('Vertex only has dates from 1992 and after')
            return False
        print('Year format is incorrect')
        return False

    if int(year) == date.today().year:
        if int(month) > date.today().month:
            print(f"{users_date}: check the month")
            return False
        if int(month) == date.today().month:
            if int(day) > date.today().day:
                print(f"{users_date}: check the day")
                return False

    return True


def pull_dates(users_date: str) -> Dict[str, List[int]]:
    """ Returns a dictionary of ints """
    DATE_REGEX = re.compile(r'([0-9]+)/([0-9]+)/([0-9]+)')
    m = re.match(DATE_REGEX, users_date)

    year, month, day = m.groups()

    return {'day': int(day), 'month': int(month), 'year': int(year)}


def get_dates() -> List:
    start_date = ''
    end_date = ''

    while True:
        start_date = input('Starting date year/mm/day: ')
        check = check_dates(start_date)
        if check is True:
            break

    while True:
        end_date = input('Ending date year/mm/day: ')
        check = check_dates(end_date)
        if check is True:
            break

    start_dic = pull_dates(start_date)
    end_dic = pull_dates(end_date)

    return [
        date(start_dic['year'], start_dic['month'], start_dic['day']),
        date(end_dic['year'], end_dic['month'], end_dic['day']),
    ]


def create_mask(args: Namespace, api: API) -> None:
    """ Creates a tremendous mask """
    subsciption = display_subscriptions(api)
    print(subsciption)
    granules = api.get_products(sub_id=subsciption['id'])
    download_granules(granules)
    # print(granule['url'])


if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()

    create = sp.add_parser('create', help='Create a mask')
    create.add_argument('name', help='Name of mask')
    create.set_defaults(func=create_mask)

    args = p.parse_args()
    if hasattr(args, 'func'):
        api = hyp3_login()
        args.func(args, api)
    else:
        p.print_help()
