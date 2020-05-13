import json
import logging
import time
from enum import Enum

from flagship import decorators
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
        self.hit_type = hit_type
        self._data = {
            self._k_type: hit_type.value,
            self._k_ds: 'APP',
            self._k_timestamp: int(round(time.time() * 1000))
        }

    @exception_handler()
    @types_validator(True, str)
    def with_ip(self, ip):
        # type: (str) -> Hit
        """
        The IP address of the user. This should be a valid IP address in IPv4 or IPv6 format.
        It will always be anonymized.

        :param ip: ip
        :return: Hit
        """
        self._data[self._k_ip] = ip
        return self

    @exception_handler()
    @types_validator(True, {'types': int, 'max_length': 10, 'min_value': 0},
                     {'types': int, 'max_length': 10, 'min_value': 0})
    def with_resolution(self, width, height):
        # type: (int, int) -> Hit
        """
        Set the user's device resolution.
        :param width: width in pixels. Max length 10 Bytes. Min value 0.
        :param height: height in pixels. Max length 10 Bytes. Min value 0.
        :return: Hit
        """
        self._data[self._k_resolution] = '{}x{}'.format(width, height)
        return self

    @exception_handler()
    @types_validator(True, int)
    def with_session_number(self, number):
        # type: (int) -> Hit
        """
        Number of the current session for the current visitor.

        :param number: session number.
        :return: Hit
        """
        self._data[self._k_session] = number
        return self

    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 20})
    def with_locale(self, locale):
        # type: (str) -> Hit
        """
        Set the user's device locale.
        :param locale: locale of the user's device. Max length 20 Bytes.
        :return: Hit
        """
        self._data[self._k_locale] = locale
        return self

    def get_data(self):
        return self._data

    def __str__(self):
        return 'Hit : ' + json.dumps(self._data)


class Page(Hit):
    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 2048})
    def __init__(self, origin):
        # type: (str) -> None
        """
        Create a Page hit.

        :param origin: current url of the page. Max length 2048 Bytes.
        """
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
    @types_validator(True, EventCategory, {'types': str, 'max_length': 500})
    def __init__(self, category, action):
        # type: (EventCategory, action) -> None

        """
        Create an Event hit.

        :param category: EventCategory.ACTION_TRACKING or EventCategory.USER_ENGAGEMENT
        :param action: Name of the kpi to report. Max length 500 Bytes.
        """
        Hit.__init__(self, HitType.EVENT)
        if isinstance(category, EventCategory):
            data = {
                self._k_event_category: category.value,
                self._k_event_action: action
            }
            self._data.update(data)
        else:
            pass

    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 500})
    def with_event_label(self, label):
        # type: (str) -> Event
        """
        Set the event description.

        :param label: event description. Max length 500 Bytes.
        :return: Page
        """
        self._data[self._k_event_label] = label
        return self

    @exception_handler()
    @types_validator(True, {'types': int, 'max_length': 500, 'min_value': 0})
    def with_event_value(self, value):
        # type: (int) -> Event
        """
        Set a number value to your event.
        :param value: Max length 500 Bytes. Min value 0.
        :return: Event
        """
        t = type(value)
        if t == int or t == str or t == float or t == bool:
            self._data[self._k_event_value] = value
        return self


class Item(Hit):
    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 500}, {'types': str, 'max_length': 500})
    def __init__(self, transaction_id, product_name):
        # type: (str, str) -> None
        """
        Create a new Item hit.

        :param transaction_id: The unique transaction ID to link with this item. Max length: 500 Bytes.
        :param product_name: product name. Max length: 500 Bytes.
        """
        Hit.__init__(self, HitType.ITEM)
        data = {
            self._k_transaction_id: transaction_id,
            self._k_item_name: product_name
        }
        self._data.update(data)

    @exception_handler()
    @types_validator(True, [int, float])
    def with_price(self, price):
        # type: (float) -> Item
        """
        Specifies the price for a single item / unit.

        :param price: item price.
        :return: Item
        """
        self._data[self._k_item_price] = price
        return self

    @exception_handler()
    @types_validator(True, int)
    def with_item_quantity(self, item_quantity):
        # type: (int) -> Item
        """
        Specifies the number of items purchased.

        :param item_quantity:
        :return: Item
        """
        self._data[self._k_item_quantity] = item_quantity
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_item_code(self, item_code):
        # type: (str) -> Item
        """
        Specifies the SKU or item code.

        :param item_code: item sku. Max length 500 Bytes.
        :return: Item
        """
        self._data[self._k_item_code] = item_code
        return self

    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 500})
    def with_item_category(self, category):
        # type: (str) -> Item
        """
        Specifies the category which the item belongs to.

        :param category: category name. Max length 500 Bytes.
        :return: Item
        """
        self._data[self._k_item_category] = category
        return self


class Transaction(Hit):
    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 500}, {'types': str, 'max_length': 500})
    def __init__(self, transaction_id, affiliation):
        # type: (str, str) -> None
        """
        Create a new Transaction hit.

        :param transaction_id: Unique transaction ID. Max length 500 Bytes.
        :param affiliation: kpi name to report. Max length 500 Bytes.
        """
        Hit.__init__(self, HitType.TRANSACTION)
        data = {
            self._k_transaction_id: transaction_id,
            self._k_transaction_affiliation: affiliation
        }
        self._data.update(data)

    @exception_handler()
    @types_validator(True, [int, float])
    def with_total_revenue(self, revenue):
        # type: (float) -> Transaction
        """
        Specifies the total revenue associated with the transaction.
        This value should include any shipping or tax costs.

        :param revenue: total revenue.
        :return: Transaction
        """
        self._data[self._k_transaction_revenue] = revenue
        return self

    @exception_handler()
    @types_validator(True, [int, float])
    def with_shipping_cost(self, shipping):
        # type: (float) -> Transaction
        """
        Specifies the total shipping cost of the transaction.

        :param shipping: total.
        :return: Transaction
        """
        self._data[self._k_transaction_shipping] = shipping
        return self

    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 10})
    def with_shipping_method(self, shipping_method):
        # type: (str) -> Transaction
        """
        Indicate the shipping method.

        :param shipping_method: shipping method. Max length 10 Bytes.
        :return: Transaction
        """
        self._data[self._k_transaction_shipping_method] = shipping_method
        return self

    @exception_handler()
    @types_validator(True, [int, float])
    def with_taxes(self, taxes):
        # type: (float) -> Transaction
        """
        Specifies the total tax of the transaction.

        :param taxes: total taxes.
        :return: Transaction
        """
        self._data[self._k_transaction_tax] = taxes
        return self

    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 10})
    def with_currency(self, currency):
        # type: (str) -> Transaction
        """
        Set the local currency for all transaction currency values. Value should be a valid ISO 4217 currency code.

        :param currency: ISO 4217 currency code. Max length 10 Bytes.
        :return: Transaction
        """
        self._data[self._k_transaction_currency] = currency
        return self

    @exception_handler()
    @types_validator(True, {'types': str, 'max_length': 10})
    def with_payment_method(self, payment):
        # type: (str) -> Transaction
        """
        Indicate the payment method.

        :param payment: payment method. Max 10 Bytes.
        :return: Transaction
        """
        self._data[self._k_transaction_payment_method] = payment
        return self

    @exception_handler()
    @types_validator(True, int)
    def with_item_count(self, item_nb):
        # type: (int) -> Transaction
        """
        Set the number of items.
        :param item_nb: number of items.
        :return: Transaction
        """
        self._data[self._k_transaction_item_count] = item_nb
        return self

    @exception_handler()
    @types_validator(True, str)
    def with_coupon_code(self, coupon):
        # type: (str) -> Transaction
        """
        Set the coupon code associated with the transaction.

        :param coupon: code. Max length 10 Bytes.
        :return: Transaction
        """
        self._data[self._k_transaction_coupon] = coupon
        return self
