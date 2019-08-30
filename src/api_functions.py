"""
 api_functions.py # TODO: UPDATE NAME
 # TODO: Update the description
 Uses the asf hyp3 api to create usefull functions
"""

import os
import re
import zipfile
from getpass import getpass
from subprocess import PIPE, call
from typing import List

from asf_hyp3 import API, LoginError


def hyp3_login() -> API:
    """ Takes users information to login to NASA EarthData,
    updates .netrc with users credentials then returns an api
    object """

    error = None
    while True:
        if error:
            print(error)
            print('Please try agian.\n')

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
                        f"machine urs.earthdata.nasa.gov login {username}\
password {password}\n"
                    )
                return api


def display_subscriptions(api: API):
    data = api.get_subscriptions()
    for subsciption in data:
        print(f"ID: {subsciption['id']}: {subsciption['name']}")
    print('Pick an id from the list above: ', end='')
    # TODO: ADD CODE TO ABORT IF USER HAS NO DATA, or give them the option
    # Create a subscription

    while True:
        try:
            user_input = int(input())
        except ValueError:
            print('Please insert an integer from above: ', end='')
            continue

        for granule in data:
            if int(granule['id']) == user_input:
                return granule
            else:
                continue
        # Prints if the ID wasn't apart of the users API
        print("That id wasn't an option, please try again: ", end='')


def download_granules(granules: List) -> None:
    ZIP_REGEX = re.compile(r'(.*).zip')
    SAR_REGEX = re.compile(r'(.*)_(VH|VV).tif(.*)')

    print(len(granules))
    for i, granule in enumerate(granules):
        print(granule['name'])
        print(f'Downloading {i+1} granule of {len(granules)}')
        f = open('.netrc', 'r')
        contents = f.read()
        username = contents.split(' ')[3]
        password = contents.split(' ')[5].split('\n')[0]
        args = ['wget', '-c', '-q', '--show-progress', f"--http-user={username}\
", f"--http-password={password}", granule['url']]
        call(args, stdout=PIPE)

        try:
            zf = zipfile.ZipFile(granule['name'], 'r')
            zf.extractall()
            zf.close()
        except FileNotFoundError:
            continue

        m = re.match(ZIP_REGEX, granule['name'])
        folder = m.groups()

        for file in os.listdir(folder[0]):
            m = re.match(SAR_REGEX, file)
            if not m:
                try:
                    os.remove(file)
                except FileNotFoundError:
                    continue
