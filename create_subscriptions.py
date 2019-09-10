"""
subscriptions.py # TODO: UPDATE NAME
McKade Sorensen
8/30/19

TODO: Update with a description of what this script does.
"""

from asf_hyp3 import API

from scripts.tremendous import hyp3_login

PROCESS_TYPE = [
    {'type': 'Change Detection - Threshold', 'id': 10, 'index': 1},
    {'type': 'Geocode Only', 'id': 31, 'index': 2},
    {'type': 'InSAR - GAMMA', 'id': 7, 'index': 3},
    {'type': 'InSAR - GMT5SAR', 'id': 14, 'index': 4},
    {'type': 'Change Detection - Threshold', 'id': 6, 'index': 5},
    {'type': 'InSAR - S1BX', 'id': 21, 'index': 6},
    {'type': 'Notify Only', 'id': 16, 'index': 7},
    {'type': 'RGB Decomposition', 'id': 12, 'index': 8},
    {'type': 'RGB Difference Image', 'id':  13, 'index': 9},
    {'type': 'RTC - GAMMA', 'id': 2, 'index': 10},
    {'type': 'RTC - S1TBX', 'id': 18, 'index': 11}
]

POLARIZATION_TYPES = [
    {'polarization': 'HH', 'index': 1},
    {'polarization': 'VV', 'index': 2},
    {'polarization': 'HH+VH', 'index': 3},
    {'polarization': 'VV+VH', 'index': 4},
    {'polarization': 'Any single', 'index': 5},
    {'polarization': 'Any dual', 'index': 6},
]


def choose_process() -> int:
    """ This function allows the user to pick a process,
        then returns that process's id """

    print('')
    for process in PROCESS_TYPE:
        print(f'Index: {process["index"]} type: {process["type"]}')

    print('\nPick an index from above: ', end='')

    loop = True
    while loop:
        try:
            process_input = int(input())
        except ValueError:
            print('Please insert a index from above: ', end='')
            continue

        for process in PROCESS_TYPE:
            if process['index'] == process_input:
                choosen_process = process['id']
                loop = False
            else:
                continue

        if loop is not False:
            print('Please insert a index from the list: ', end='')

    return choosen_process


def choose_subscription_name(api: API) -> str:
    users_current_subscriptions = api.get_subscriptions()

    print('\nName of new subscriptions: ', end='')
    while True:
        try:
            new_subscription = input()
        except ValueError:
            print('Error with name, please try a new name: ', end='')
            continue

        match_ = False
        for subscriptions in users_current_subscriptions:
            if subscriptions['name'].lower() == new_subscription.lower():
                match_ = True
                continue
        if match_:
            print(f'{new_subscription} exist, try again: ', end='')
        else:
            return new_subscription


def choose_polarization() -> str:
    print('')
    for polarization in POLARIZATION_TYPES:
        print(f'Index: {polarization["index"]} \
        type: {polarization["polarization"]}')

    print('\nPlease pick an index from above: ', end='')
    while True:
        try:
            polarization_index = int(input())
        except ValueError:
            print('Please insert a index from above: ', end='')
            continue

        for polarization in POLARIZATION_TYPES:
            if polarization['index'] == polarization_index:
                choosen_polarization = polarization['polarization']
                return choosen_polarization
        print('Please insert a index from above: ', end='')


def choose_location() -> str:
    print('\nPlease input location (for example type help): ', end='')

    while True:
        try:
            location = input()
        except ValueError:
            print('Please try again: ', end='')
            continue

        if location.lower() == 'help':
            print('POLYGON((-147.755127 63.597448,-147.095947 63.597448,\
-147.095947 63.927717,-147.755127 63.927717,-147.755127 63.597448))')
            print('Input location: ', end='')
            continue
        return location


def create_subscription(api: API) -> None:
    print('\nName of subscription: ')
    # process_id = choose_process()
    # subscription_name = choose_subscription_name(api)
    # polarization = choose_polarization()
    location = choose_location()
    print(location)


if __name__ == '__main__':
    api = hyp3_login()
    create_subscription(api)
