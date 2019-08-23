"""
 Creates a tremendous water mask
 tremendous.py UPDATE NAME
 McKade Sorensen
 8-20-19
 Allows a user to create a massive water mask
"""
import os
import re
from argparse import ArgumentParser, Namespace
from datetime import date
from typing import Dict, List

from asf_notebook import download_hyp3_products, earthdata_hyp3_login


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


def get_dates(users_date: str) -> Dict[str, List[int]]:
    """ Returns a dictionary of ints """
    DATE_REGEX = re.compile(r'([0-9]+)/([0-9]+)/([0-9]+)')
    m = re.match(DATE_REGEX, users_date)

    year, month, day = m.groups()

    return {'day': int(day), 'month': int(month), 'year': int(year)}


def get_data(folder: str):
    f_path = make_dirs(folder)
    user = earthdata_hyp3_login()
    start_date = ''
    end_date = ''

    # TODO: Look into turning this into its own function
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

    start_dic = get_dates(start_date)
    end_dic = get_dates(end_date)

    date_range = [
        date(start_dic['year'], start_dic['month'], start_dic['day']),
        date(end_dic['year'], end_dic['month'], end_dic['day']),
    ]

    while True:
        flight_direction = input('Flight direction, a for ascending and d for descending: ')
        if flight_direction.lower() == 'a':
            flight_direction = 'ascending'
            break
        elif flight_direction.lower() == 'd':
            flight_direction = 'descending'
            break
        else:
            print('Incorrect input')

    subscription_id = download_hyp3_products(
        user,
        f_path,
        start_date=date_range[0],
        end_date=date_range[1],
    )

    subscription_info = user.get_subscriptions(subscription_id)
    process_type = subscription_info['process_id']


def create_mask(args: Namespace) -> None:
    """ Creates a tremendous mask """
    get_data(args.name)


if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()

    create = sp.add_parser('create', help='Create a mask')
    create.add_argument('name', help='Name of mask')
    create.set_defaults(func=create_mask)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()
