# coding: utf-8

from flask_restful import Resource, reqparse, request
from .address import Address
from .timing import Timing
from . import db
from google.cloud.firestore_v1beta1._helpers import GeoPoint
from ._util import geopoint_from_dict
parser = reqparse.RequestParser()
parser.add_argument('task')

# todo: change below constant with file name
restaurants_ref = db.get_db().collection(u'restaurants') or None


class Restaurant(Resource):

    def get(self, restaurant_name, area=None):
        res = None
        if restaurants_ref:
            if area:
                res = restaurants_ref.document(restaurant_name)\
                    .collection('branch')\
                    .document(area)\
                    .get()
                res = next(res)
            else:
                res = restaurants_ref.document(restaurant_name)\
                    .collection('branch').get()

                res = {
                        'restaurant': restaurant_name,
                        'branch': [{'name': restaurant.id} for restaurant in res]
                }

        return res

    def post(self, restaurant_name, area):

        # arguments = request.get_json(force=True)
        # arguments = restaurant_argument_parser(arguments)

        if restaurants_ref:
            res = restaurants_ref.document(restaurant_name).set({
                'name': restaurant_name,
                'rating': 0.0,

            })

            res = restaurants_ref.document(restaurant_name).collection('branch').document(area).\
                set({"location": GeoPoint(latitude=3.0, longitude=2.0),
                    "address": {
                        "city": "",
                        "landmark": "",
                        "near_locality": "",
                        "country": "",
                        "area": ""
                    },
                    "table_max_capacity": 4,
                    "no_of_tables": 10,
                    "timing": {
                        "close": 22,
                        "open": 10
                    },
                }, merge=True)

        return True


class Restaurants(Resource):

    def get(self):
        if restaurants_ref:
            restaurant_names = restaurants_ref.get()

            return {'restaurants':
                                [{'id': restaurant.id,
                                  'name': restaurant.get('name')}\
                                 for restaurant in restaurant_names]}

        return {'restaurants': ''}


def update_restaurant_argument_parser(args):
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


def add_restaurant_argument_parser(args):
    assert isinstance(args, dict)

    _fields = {
        'name': str,
        'rating': float,
        'branch': RestaurantBranch.from_dict
    }

    for key, value in args.items():
        _fields[key](value)



class RestaurantDetails:

    def __init__(self, name: str, rating: float):
        self.name = name.lower().title()
        self.rating = float(rating)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, restaurant):
        return cls(**restaurant)


class RestaurantBranch:

    _fields = {
        'address': Address.from_dict,
        'location': geopoint_from_dict,
        'timing': Timing.from_dict,
    }

    def __init__(self, address: Address, location: GeoPoint, timing: Timing,
                 no_of_tables: int, table_max_capacity: int):
        self.address = address
        self.location = location
        self.timing = timing
        self.no_of_tables = no_of_tables
        self.table_max_capacity = table_max_capacity

    @classmethod
    def from_dict(cls, restaurant):
        args = {}
        for key, value in restaurant.items():
            try:
                args[key] = RestaurantBranch._fields[key](**value)
            except TypeError:
                pass

        return cls(**args)

    def to_dict(self):
        return self.__dict__
