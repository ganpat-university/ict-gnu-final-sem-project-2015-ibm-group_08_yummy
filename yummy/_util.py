from google.cloud.firestore_v1beta1._helpers import GeoPoint
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from datetime import datetime


def parse_args_for_update(args):
    assert isinstance(args, dict)

    delete_keys = []
    new_args = {}
    for key, value in args.items():
        if isinstance(value, dict):
            delete_keys.append(key)
            for k, v in value.items():
                new_args[key+'.'+k] = v
    for key in delete_keys:
        args.pop(key, None)

    args.update(new_args)
    return args


def registered_usernames():
    from flask import g

    def init_username_service():
        if 'users' not in g:
            g.usernames = set()

    def get_username_service():
        init_username_service()
        return g.usernames

    def insert_username(username):
        init_username_service()
        g.usernames.add(username)

    def username_exsist(username):
        init_username_service()
        return bool(username in g.users)


def geopoint_from_dict(geopoint):
    return GeoPoint(**geopoint)


def convert_to_date_from_dict(date):
    return DatetimeWithNanoseconds(**date)


def get_current_date():
    return DatetimeWithNanoseconds.from_rfc3339(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
