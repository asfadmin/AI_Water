"""
 McKade Sorensen
 09/05/2019
 api_functions.py
 api_functions contains useful functions that interact with the HYP3 API.
"""

import os
from getpass import getpass
from subprocess import PIPE, call
from typing import Dict, List

from asf_hyp3 import API, LoginError


def hyp3_login() -> API:
    """ Takes users information to log in to NASA EarthData,
    updates .netrc with user's credentials then returns an API object. """

    username = ""
    try:
        f = open('.netrc', 'r')
        contents = f.read()
        username = contents.split(' ')[3]
        password = contents.split(' ')[5].split('\n')[0]
    except IndexError:
        pass

    error = None
    while True:
        if error:
            print(error)
            print('Please try agian.\n')

        if username == "":
            print("Enter your NASA EarthData username: ", end='')
            username = input()
            password = getpass()

        try:
            api = API(username)
        except Exception:
            raise
        else:
            try:
                api.login(password)
            except LoginError as e:
                error = e
                continue
            except Exception:
                raise
            else:
                print(f' Welcome {username}')
                with open('.netrc', 'w+') as f:
                    f.write(
                        f"machine urs.earthdata.nasa.gov login {username} password {password}\n"
                    )
                return api


def grab_subscription(api: API) -> Dict:
    """ Displays all of the user's HYP3 subscriptions, the user then selects
        which subscription they would like to access. The function then returns
        that subscription. """

    data = api.get_subscriptions()

    if not data:
        print("This account has no subscriptions.")
        exit()

    for subsciption in data:
        print(f"ID: {subsciption['id']}: {subsciption['name']}")
    print('Pick an id from the list above: ', end='')

    while True:
        try:
            user_input = int(input())
        except ValueError:
            print('Please insert an integer from above: ', end='')
            continue

        for subscription in data:
            if int(subscription['id']) == user_input:
                return subscription
            else:
                continue
        # Prints if the ID wasn't apart of the users API
        print("That id wasn't an option, please try again: ", end='')


def make_dir(dir: str) -> str:
    if not os.path.isdir(dir):
        os.mkdir(dir)
    return dir


def download_prouducts(products: List, i: int, product) -> None:
    """ download_products takes in a list of products, an index (i),
        and an individual product. The function uses the product variable to
        download the zip file. The function uses the list and index to display
        how many products have finished. """

    print(f'Downloading {i+1} granule of {len(products)}')
    f = open('.netrc', 'r')
    contents = f.read()
    username = contents.split(' ')[3]
    password = contents.split(' ')[5].split('\n')[0]
    args = ['wget', '-c', '-q', '--show-progress', f"--http-user={username}\
", f"--http-password={password}", product['url']]
    call(args, stdout=PIPE)
