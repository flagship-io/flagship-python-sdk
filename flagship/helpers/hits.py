import json
import time
from enum import Enum

from flagship.decorators import types_validator, exception_handler


class HitType(Enum):
    PAGE = 'SCREENVIEW'
    EVENT = 'EVENT'
    TRANSACTION = 'TRANSACTION'
    ITEM = 'ITEM'


class Hit(object):
    _k_origin = 'dl'  # origin
    _k_env_id = 'cid'  # env_id
    _k_visitor_id = 'vid'  # visitor id
    _k_type = 't'
    _k_ds = 'ds'
    _k_timestamp = 'cst'
    _k_ip = 'uip'
    _k_resolution = 'sr'
    _k_locale = 'ul'
    _k_session = 'sn'
    _k_event_category = 'ec'
    _k_event_action = 'ea'
    _k_event_label = 'el'
    _k_event_value = 'ev'
    _k_item_name = 'in'
    _k_item_price = 'ip'
    _k_item_quantity = 'iq'
    _k_item_code = 'ic'
    _k_item_category = 'iv'
    _k_transaction_id = 'tid'
    _k_transaction_affiliation = 'ta'
    _k_transaction_revenue = 'tr'
    _k_transaction_shipping = 'ts'
    _k_transaction_tax = 'tt'
    _k_transaction_currency = 'tc'
    _k_transaction_payment_method = 'pm'
    _k_transaction_shipping_method = 'sm'
    _k_transaction_item_count = 'icn'
    _k_transaction_coupon = 'tcc'

    @exception_handler()
    @types_validator(True, HitType)
    def __init__(self, hit_type):
        self._data = {
            self._k_type: hit_type.name,
            self._k_ds: 'APP',
            self._k_timestamp: int(round(time.time() * 1000))
        }

    @exception_handler()
    @types_validator(True, str)
    def with_ip(self, ip):
        self._data[self._k_ip] = ip
        return self

    @exception_handler()
    @types_validator(True, int, int)
    def with_resolution(self, width, height):
        self._data[self._k_resolution] = '{}x{}'.format(width, height)
        return self

    @exception_handler()
    @types_validator(True, int)
    def with_session_number(self, number):
        self._data[self._k_session] = number
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_locale(self, locale):
        self._data[self._k_locale] = locale
        return self

    def get_data(self):
        return self._data

    def __str__(self):
        return 'Hit : ' + json.dumps(self._data)


class Page(Hit):
    @exception_handler()
    @types_validator(True, str)
    def __init__(self, origin):
        # super(self).__init__(HitType.PAGE)
        Hit.__init__(self, HitType.PAGE)
        data = {
            self._k_origin: origin
        }
        self._data.update(data)


class EventCategory(Enum):
    ACTION_TRACKING = 'Action Tracking'
    USER_ENGAGEMENT = 'User Engagement'


class Event(Hit):
    @exception_handler()
    @types_validator(True, EventCategory, str)
    def __init__(self, category, action):
        Hit.__init__(self, HitType.EVENT)
        if isinstance(category, EventCategory):
            # super(self).__init__(HitType.EVENT)
            # Hit.__init__(self, HitType.EVENT)
            data = {
                self._k_event_category: category.name,
                self._k_event_action: action
            }
            self._data.update(data)
        else:
            pass

    @exception_handler()
    @types_validator(True, str)
    def with_event_label(self, label):
        self._data[self._k_event_label] = label
        return self

    @exception_handler()
    @types_validator(True, [int, float, str, bool])
    def with_event_value(self, value):
        t = type(value)
        if t == int or t == str or t == float or t == bool:
            self._data[self._k_event_value] = value
        return self


class Item(Hit):
    @exception_handler()
    @types_validator(True, str, str)
    def __init__(self, transaction_id, product_name):
        # super(self).__init__(HitType.ITEM)
        Hit.__init__(self, HitType.ITEM)
        data = {
            self._k_transaction_id: transaction_id,
            self._k_item_name: product_name
        }
        self._data.update(data)

    @exception_handler()
    @types_validator(True, [int, float])
    def with_price(self, price):
        self._data[self._k_item_price] = price
        return self

    @exception_handler()
    @types_validator(True, int)
    def with_item_quantity(self, item_quantity):
        self._data[self._k_item_quantity] = item_quantity
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_item_code(self, item_code):
        self._data[self._k_item_code] = item_code
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_item_category(self, category):
        self._data[self._k_item_category] = category
        return self


class Transaction(Hit):
    @exception_handler()
    @types_validator(True, str, str)
    def __init__(self, transaction_id, affiliation):
        # super(self).__init__(HitType.TRANSACTION)
        Hit.__init__(self, HitType.TRANSACTION)
        data = {
            self._k_transaction_id: transaction_id,
            self._k_transaction_affiliation: affiliation
        }
        self._data.update(data)

    @exception_handler()
    @types_validator(True, [int, float])
    def with_total_revenue(self, revenue):
        self._data[self._k_transaction_revenue] = revenue
        return self

    @exception_handler()
    @types_validator(True, [int, float])
    def with_shipping_cost(self, shipping):
        self._data[self._k_transaction_shipping] = shipping
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_shipping_method(self, shipping_method):
        self._data[self._k_transaction_shipping_method] = shipping_method
        return self

    @exception_handler()
    @types_validator(True, [int, float])
    def with_taxes(self, taxes):
        self._data[self._k_transaction_tax] = taxes
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_currency(self, currency):
        self._data[self._k_transaction_currency] = currency
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_payment_method(self, payment):
        self._data[self._k_transaction_payment_method] = payment
        return self

    @exception_handler()
    @types_validator(True, int)
    def with_item_count(self, item_nb):
        self._data[self._k_transaction_item_count] = item_nb
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_coupon_code(self, coupon):
        self._data[self._k_transaction_coupon] = coupon
        return self

