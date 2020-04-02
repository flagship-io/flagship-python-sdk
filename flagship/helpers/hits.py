import json
import time
from enum import Enum


class HitType(Enum):
    PAGE = 'SCREENVIEW'
    EVENT = 'EVENT'
    TRANSACTION = 'TRANSACTION'
    ITEM = 'ITEM'


class Hit:
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

    def __init__(self, hit_type):
        self._data = {
            self._k_type: hit_type.value,
            self._k_ds: 'APP',
            self._k_timestamp: int(round(time.time() * 1000))
        }

    def add_config(self, env_id, visitor_id):
        self._data[self._k_env_id] = env_id
        self._data[self._k_visitor_id] = visitor_id

    def with_ip(self, ip: str):
        self._data[self._k_ip] = ip
        return self

    def with_resolution(self, width: int, height: int):
        self._data[self._k_resolution] = '{}x{}'.format(width, height)
        return self

    def with_session_number(self, number: int):
        self._data[self._k_session] = number
        return self

    def with_locale(self, locale: str):
        self._data[self._k_locale] = locale
        return self

    def __str__(self):
        return 'Hit : ' + json.dumps(self._data)


class Page(Hit):
    def __init__(self, origin: str):
        super().__init__(HitType.PAGE)
        data = {
            self._k_origin: origin
        }
        self._data.update(data)


class EventCategory(Enum):
    ACTION_TRACKING = 'Action Tracking'
    USER_ENGAGEMENT = 'User Engagement'


class Event(Hit):
    def __init__(self, category: EventCategory, action: str):
        if isinstance(category, EventCategory):
            super().__init__(HitType.EVENT)
            data = {
                self._k_event_category: category.value,
                self._k_event_action: action
            }
            self._data.update(data)
        else:
            pass

    def with_event_label(self, label: str):
        self._data[self._k_event_label] = label
        return self

    def with_event_value(self, value):
        t = type(value)
        if t == int or t == str or t == float or t == bool:
            self._data[self._k_event_value] = value
        return self


class Item(Hit):
    def __init__(self, transaction_id: str, product_name: str):
        super().__init__(HitType.ITEM)
        data = {
            self._k_transaction_id: transaction_id,
            self._k_item_name: product_name
        }
        self._data.update(data)

    def with_price(self, price: float):
        self._data[self._k_item_price] = price
        return self

    def with_item_quantity(self, item_quantity: int):
        self._data[self._k_item_quantity] = item_quantity
        return self

    def with_item_code(self, item_code: str):
        self._data[self._k_item_code] = item_code
        return self

    def with_item_category(self, category: str):
        self._data[self._k_item_category] = category
        return self


class Transaction(Hit):
    def __init__(self, transaction_id: str, affiliation: str):
        super().__init__(HitType.TRANSACTION)
        data = {
            self._k_transaction_id: transaction_id,
            self._k_transaction_affiliation: affiliation
        }
        self._data.update(data)

    def with_total_revenue(self, revenue: float):
        self._data[self._k_transaction_revenue] = revenue
        return self

    def with_shipping_cost(self, shipping: float):
        self._data[self._k_transaction_shipping] = shipping
        return self

    def with_shipping_method(self, shipping_method: float):
        self._data[self._k_transaction_shipping_method] = shipping_method
        return self

    def with_taxes(self, taxes: float):
        self._data[self._k_transaction_tax] = taxes
        return self

    def with_currency(self, currency: str):
        self._data[self._k_transaction_currency] = currency
        return self

    def with_payment_method(self, payment: str):
        self._data[self._k_transaction_payment_method] = payment
        return self

    def with_item_count(self, item_nb: int):
        self._data[self._k_transaction_item_count] = item_nb
        return self
