from __future__ import unicode_literals

import json
import sys
import time
import traceback
import uuid
from collections import OrderedDict

from enum import Enum

from flagship.constants import TAG_CACHE_MANAGER
from flagship.decorators import param_types_validator
from flagship.errors import HitCacheFormatException
from flagship.utils import log_exception


class HitType(Enum):
    SCREENVIEW = 'SCREENVIEW'
    PAGEVIEW = 'PAGEVIEW'
    EVENT = 'EVENT'
    TRANSACTION = 'TRANSACTION'
    ITEM = 'ITEM'
    ACTIVATE = "ACTIVATE"
    CONSENT = 'CONSENT'
    SEGMENT = 'SEGMENT'
    BATCH = 'BATCH'

class HitFields:
    origin = 'dl'  # origin
    env_id = 'cid'  # env_id
    visitor_id = 'vid'  # visitor id
    anonymous_id = 'aid'  # anonymous id / activate
    customer_visitor_id = 'cuid'
    type = 't'
    ds = 'ds'
    # timestamp = 'cst'
    ip = 'uip'
    resolution = 'sr'
    locale = 'ul'
    session = 'sn'
    event_category = 'ec'
    event_action = 'ea'
    event_label = 'el'
    event_value = 'ev'
    item_name = 'in'
    item_price = 'ip'
    item_quantity = 'iq'
    item_code = 'ic'
    item_category = 'iv'
    transaction_id = 'tid'
    transaction_affiliation = 'ta'
    transaction_revenue = 'tr'
    transaction_shipping = 'ts'
    transaction_tax = 'tt'
    transaction_currency = 'tc'
    transaction_payment_method = 'pm'
    transaction_shipping_method = 'sm'
    transaction_item_count = 'icn'
    transaction_coupon = 'tcc'
    variation_group_id = 'caid'
    # variation_group_id = 'vgid'
    variation_id = 'vaid'
    consent = 'vc'
    segment_list = 's'
    queue_time = 'qt'
    batch = 'h'


class Hit(object):

    HIT_EXPIRATION = 14400000

    @param_types_validator(True, HitType)
    def __init__(self, hit_type):
        self.type = hit_type
        self.id = str(uuid.uuid4())
        self.visitor_id = None
        self.anonymous_id = None
        self.timestamp = int(time.time()) * 1000
        self.hit_data = {
            HitFields.type: hit_type.value,
            HitFields.ds: 'APP',
            # self.timestamp: int(round(time.time() * 1000))
        }

    @param_types_validator(True, str)
    def with_ip(self, ip):
        # type: (str) -> Hit
        """
        The IP address of the user. This should be a valid IP address in IPv4 or IPv6 format.
        It will always be anonymized.

        :param ip: ip
        :return: Hit
        """
        self.hit_data[HitFields.ip] = ip
        return self

    @param_types_validator(True, int, int)
    def with_resolution(self, width, height):
        # type: (int, int) -> Hit
        """
        Set the user's device resolution.
        :param width: width in pixels. Max length 10 Bytes. Min value 0.
        :param height: height in pixels. Max length 10 Bytes. Min value 0.
        :return: Hit
        """
        if width > 0 and height > 0:
            self.hit_data[HitFields.resolution] = '{}x{}'.format(width, height)
        return self

    @param_types_validator(True, int)
    def with_session_number(self, number):
        # type: (int) -> Hit
        """
        Number of the current session for the current visitor.

        :param number: session number.
        :return: Hit
        """
        self.hit_data[HitFields.session] = number
        return self

    @param_types_validator(True, str)
    def with_locale(self, locale):
        # type: (str) -> Hit
        """
        Set the user's device locale.
        :param locale: locale of the user's device. Max length 20 Bytes.
        :return: Hit
        """
        self.hit_data[HitFields.locale] = locale
        return self

    def _with_hit_id(self, hit_id):
        self.id = hit_id
        return self

    def _with_visitor_ids(self, visitor_id, anonymous_id):
        self.visitor_id = visitor_id
        self.anonymous_id = anonymous_id
        if anonymous_id is not None:
            self.hit_data[HitFields.customer_visitor_id] = visitor_id
            self.hit_data[HitFields.visitor_id] = anonymous_id
        else:
            self.hit_data[HitFields.visitor_id] = visitor_id
            self.hit_data[HitFields.customer_visitor_id] = None
        return self

    def _with_timestamp(self, timestamp):
        self.timestamp = timestamp
        return self

    def data(self):
        return self.hit_data

    def size(self):
        return sys.getsizeof(self.hit_data)

    def check_data_validity(self):
        if not ((int(time.time()) * 1000) - self.timestamp) < Hit.HIT_EXPIRATION:
            return False
        if (not bool(self.hit_data[HitFields.type]) or
                (self.hit_data[HitFields.ds] != 'APP')):
            return False
        return True

    def __str__(self):
        return ''+str({
            'id': self.id,
            'type': str(self.type.value),
            'visitor_id': self.visitor_id,
            'anonymous_id': self.anonymous_id,
            'timestamp': self.timestamp,
            'data': self.hit_data
        })


class Page(Hit):
    @param_types_validator(True, str)
    def __init__(self, origin):
        # type: (str) -> None
        """
        Create a Page hit.

        :param origin: current valid url of the page. Max length 2048 Bytes.
        """
        Hit.__init__(self, HitType.PAGEVIEW)
        data = {
            HitFields.origin: origin
        }
        self.hit_data.update(data)

    def check_data_validity(self):
        from urllib.parse import urlparse
        if ((Hit.check_data_validity(self) is False) or
                (not bool(self.hit_data[HitFields.origin])) or
                (bool(urlparse(self.hit_data[HitFields.origin]).scheme) is False) or
                (bool(urlparse(self.hit_data[HitFields.origin]).netloc) is False)):
            return False
        return True

    @staticmethod
    def from_json(content):
        return Page(content[HitFields.origin])


class Screen(Hit):
    @param_types_validator(True, str)
    def __init__(self, origin):
        # type: (str) -> None
        """
        Create a Screen hit.
        :param origin: name of the current screen. Max length 2048 Bytes.
        """
        Hit.__init__(self, HitType.SCREENVIEW)
        data = {
            HitFields.origin: origin
        }
        self.hit_data.update(data)

    def check_data_validity(self):
        if ((Hit.check_data_validity(self) is False) or
                (self.hit_data[HitFields.ds] != 'APP') or
                (not bool(self.hit_data[HitFields.origin]))):
            return False
        return True

    @staticmethod
    def from_json(content):
        return Screen(content[HitFields.origin])


class EventCategory(Enum):
    ACTION_TRACKING = 'Action Tracking'
    USER_ENGAGEMENT = 'User Engagement'


class Event(Hit):
    # @param_types_validator(True, EventCategory, str)
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
                HitFields.event_category: category.value,
                HitFields.event_action: action
            }
            self.hit_data.update(data)
        else:
            pass

    @param_types_validator(True, str)
    def with_event_label(self, label):
        # type: (str) -> Event
        """
        Set the event description.

        :param label: event description. Max length 500 Bytes.
        :return: Event
        """
        self.hit_data[HitFields.event_label] = label
        return self

    @param_types_validator(True, int)
    def with_event_value(self, value):
        # type: (int) -> Event
        """
        Set a number value to your event.
        :param value: Max length 500 Bytes. Min value 0.
        :return: Event
        """
        t = type(value)
        if t == int or t == str or t == float or t == bool:
            self.hit_data[HitFields.event_value] = value
        return self

    def check_data_validity(self):
        if ((Hit.check_data_validity(self) is False) or
                (not bool(self.hit_data[HitFields.event_category])) or
                (not bool(self.hit_data[HitFields.event_action]))):
            return False
        return True

    @staticmethod
    def from_json(content):
        import re
        if HitFields.event_label in content:
            matching = re.match("(python:(true|false))",  content[HitFields.event_label])
            if matching:
                consent = True if (matching.groups()[1] in ['True', 'true']) else True
                return _Consent(consent)
        return Event(content[HitFields.event_category], content[HitFields.event_category])


class Item(Hit):
    @param_types_validator(True, str, str, str)
    def __init__(self, transaction_id, product_name, product_sku):
        # type: (str, str, str) -> None
        """
        Create a new Item hit.

        :param transaction_id: The unique transaction ID to link with this item. Max length: 500 Bytes.
        :param product_name: product name. Max length: 500 Bytes.
        """
        Hit.__init__(self, HitType.ITEM)
        data = {
            HitFields.transaction_id: transaction_id,
            HitFields.item_name: product_name,
            HitFields.item_code: product_sku
        }
        self.hit_data.update(data)

    @param_types_validator(True, [int, float])
    def with_price(self, price):
        # type: (float) -> Item
        """
        Specifies the price for a single item / unit.

        :param price: item price.
        :return: Item
        """
        self.hit_data[HitFields.item_price] = price
        return self

    @param_types_validator(True, int)
    def with_item_quantity(self, item_quantity):
        # type: (int) -> Item
        """
        Specifies the number of items purchased.

        :param item_quantity:
        :return: Item
        """
        self.hit_data[HitFields.item_quantity] = item_quantity
        return self

    # @exception_handler()
    # @types_validator(True, str)
    # def with_item_code(self, item_code):
    #     # type: (str) -> Item
    #     """
    #     Specifies the SKU or item code.
    #
    #     :param item_code: item sku. Max length 500 Bytes.
    #     :return: Item
    #     """
    #     self._data[self.item_code] = item_code
    #     return self

    @param_types_validator(True, str)
    def with_item_category(self, category):
        # type: (str) -> Item
        """
        Specifies the category which the item belongs to.

        :param category: category name. Max length 500 Bytes.
        :return: Item
        """
        self.hit_data[HitFields.item_category] = category
        return self

    def check_data_validity(self):
        if ((Hit.check_data_validity(self) is False) or
                (not bool(self.hit_data[HitFields.transaction_id])) or
                (not bool(self.hit_data[HitFields.item_name])) or
                (not bool(self.hit_data[HitFields.item_code]))):
            return False
        return True

    @staticmethod
    def from_json(content):
        return Item(content[HitFields.transaction_id], content[HitFields.item_name], content[HitFields.item_code])



class Transaction(Hit):
    @param_types_validator(True, str, str)
    def __init__(self, transaction_id, affiliation):
        # type: (str, str) -> None
        """
        Create a new Transaction hit.

        :param transaction_id: Unique transaction ID. Max length 500 Bytes.
        :param affiliation: kpi name to report. Max length 500 Bytes.
        """
        Hit.__init__(self, HitType.TRANSACTION)
        data = {
            HitFields.transaction_id: transaction_id,
            HitFields.transaction_affiliation: affiliation
        }
        self.hit_data.update(data)

    @param_types_validator(True, [int, float])
    def with_total_revenue(self, revenue):
        # type: (float) -> Transaction
        """
        Specifies the total revenue associated with the transaction.
        This value should include any shipping or tax costs.

        :param revenue: total revenue.
        :return: Transaction
        """
        self.hit_data[HitFields.transaction_revenue] = revenue
        return self

    @param_types_validator(True, [int, float])
    def with_shipping_cost(self, shipping):
        # type: (float) -> Transaction
        """
        Specifies the total shipping cost of the transaction.

        :param shipping: total.
        :return: Transaction
        """
        self.hit_data[HitFields.transaction_shipping] = shipping
        return self

    @param_types_validator(True, str)
    def with_shipping_method(self, shipping_method):
        # type: (str) -> Transaction
        """
        Indicate the shipping method.

        :param shipping_method: shipping method. Max length 10 Bytes.
        :return: Transaction
        """
        self.hit_data[HitFields.transaction_shipping_method] = shipping_method
        return self

    @param_types_validator(True, [int, float])
    def with_taxes(self, taxes):
        # type: (float) -> Transaction
        """
        Specifies the total tax of the transaction.

        :param taxes: total taxes.
        :return: Transaction
        """
        self.hit_data[HitFields.transaction_tax] = taxes
        return self

    @param_types_validator(True, str)
    def with_currency(self, currency):
        # type: (str) -> Transaction
        """
        Set the local currency for all transaction currency values. Value should be a valid ISO 4217 currency code.

        :param currency: ISO 4217 currency code. Max length 10 Bytes.
        :return: Transaction
        """
        self.hit_data[HitFields.transaction_currency] = currency
        return self

    @param_types_validator(True, str)
    def with_payment_method(self, payment):
        # type: (str) -> Transaction
        """
        Indicate the payment method.

        :param payment: payment method. Max 10 Bytes.
        :return: Transaction
        """
        self.hit_data[HitFields.transaction_payment_method] = payment
        return self

    @param_types_validator(True, int)
    def with_item_count(self, item_nb):
        # type: (int) -> Transaction
        """
        Set the number of items.
        :param item_nb: number of items.
        :return: Transaction
        """
        self.hit_data[HitFields.transaction_item_count] = item_nb
        return self

    @param_types_validator(True, str)
    def with_coupon_code(self, coupon):
        # type: (str) -> Transaction
        """
        Set the coupon code associated with the transaction.

        :param coupon: code. Max length 10 Bytes.
        :return: Transaction
        """
        self.hit_data[HitFields.transaction_coupon] = coupon
        return self

    def check_data_validity(self):
        if ((Hit.check_data_validity(self) is False) or
                (not bool(self.hit_data[HitFields.transaction_id])) or
                (not bool(self.hit_data[HitFields.transaction_affiliation]))):
            return False
        return True

    @staticmethod
    def from_json(content):
        return Transaction(content[HitFields.transaction_id], content[HitFields.transaction_affiliation])


class _Activate(Hit):
    # @param_types_validator(True, [str, bytes], [str, bytes])
    def __init__(self, visitor_id, anonymous_id, variation_group_id, variation_id):
        Hit.__init__(self, HitType.ACTIVATE)
        self.visitor_id = visitor_id
        self.anonymous_id = anonymous_id
        # self.hit_type = HitType.ACTIVATE
        self.hit_data = {
            # self.env_id: env_id,
            HitFields.variation_group_id: variation_group_id,
            HitFields.variation_id: variation_id
        }
        if anonymous_id is not None:
            self.hit_data[HitFields.anonymous_id] = anonymous_id
            self.hit_data[HitFields.visitor_id] = visitor_id
        else:
            self.hit_data[HitFields.visitor_id] = visitor_id
            self.hit_data[HitFields.anonymous_id] = None
        # self._data.update(data)

    def check_data_validity(self):
        if not ((int(time.time()) * 1000) - self.timestamp) < Hit.HIT_EXPIRATION:
            return False
        if ((not bool(self.hit_data[HitFields.visitor_id])) or
                (not bool(self.hit_data[HitFields.variation_group_id])) or
                (not bool(self.hit_data[HitFields.variation_id]))):
            return False
        return True

    def data(self):
        self.hit_data[HitFields.queue_time] = (int((time.time()) * 1000) - self.timestamp)
        return self.hit_data

    @staticmethod
    def from_json(content):
        anonymous_id = content[HitFields.anonymous_id] if HitFields.anonymous_id in content else None
        visitor_id = content[HitFields.visitor_id]
        variation_group_id = content[HitFields.variation_group_id]
        variation_id = content[HitFields.variation_id]
        return _Activate(visitor_id, anonymous_id, variation_group_id, variation_id)


class _Consent(Event):
    @param_types_validator(True, bool)
    def __init__(self, consent):
        self.consent = consent
        Event.__init__(self, EventCategory.USER_ENGAGEMENT, 'fs_consent')
        data = {
            HitFields.event_label: 'python:{}'.format(str(consent).lower())
        }
        self.hit_data.update(data)

    def check_data_validity(self):
        if ((Hit.check_data_validity(self) is False) or
                (not bool(self.hit_data[HitFields.event_label]))):
            return False
        return True


class _Segment(Hit):
    # @param_types_validator(True, str, dict)
    def __init__(self, visitor_id, context):
        Hit.__init__(self, HitType.SEGMENT)
        data = {
            HitFields.visitor_id: visitor_id,
            HitFields.segment_list: context
        }
        self.hit_data.update(data)

    def check_data_validity(self):
        if ((Hit.check_data_validity(self) is False) or
                (not bool(self.hit_data[HitFields.visitor_id])) or
                (self.hit_data[HitFields.segment_list] is None) or
                (len(self.hit_data[HitFields.segment_list]) < 0)):
            return False
        return True

    @staticmethod
    def from_json(content):
        return _Segment(content[HitFields.visitor_id], content[HitFields.segment_list])


class _Batch(Hit):

    def __init__(self):
        Hit.__init__(self, HitType.BATCH)
        self.hits = list()
        self.hit_data[HitFields.batch] = []

    def add_child(self, hit):
        from flagship.tracking_manager import TrackingManager
        is_timestamp_valid = ((int(time.time()) * 1000) - hit.timestamp) < TrackingManager.HIT_EXPIRATION
        is_size_valid = (sys.getsizeof(self.hit_data) + sys.getsizeof(hit.hit_data)) < TrackingManager.BATCH_MAX_SIZE
        if isinstance(hit, Hit) and is_timestamp_valid and is_size_valid:
            self.hits.append(hit)
            self.hit_data[HitFields.batch].append(hit.hit_data)
            return True
        return False

    def data(self):
        batch_data = []
        for h in self.hits:
            h.hit_data[HitFields.queue_time] = (int((time.time()) * 1000) - h.timestamp)
            batch_data.append(h.hit_data)
        self.hit_data[HitFields.batch] = batch_data
        return self.hit_data

    def check_data_validity(self):
        if Hit.check_data_validity(self) is False:
            return False
        for h in self.hits:
            if h.check_data_validity is False:
                return False
            if h.hit_data[HitFields.queue_time] is None:
                return False
            if len(self.hits) == 0:
                return False
        return True

    def size(self):
        return len(self.hits)


# def from_json(hit_json):
#     try:
#
#         # type = HitType(json['type'])
#         # content = json['content']
#         # if type == HitType.PAGEVIEW:
#         #     return Page.from_json(content)
#         # if type == HitType.PAGEVIEW:
#         #     hit = Page(content[HitFields.origin])
#         # elif type == HitType.SCREENVIEW:
#         #     hit = Screen(content[HitFields.origin])
#         # elif type == HitType.EVENT:
#         #     import re
#         #     matching = re.match("(python:(true|false))",  content[HitFields.event_label])
#         #     if matching:
#         #         consent = True if (matching.groups()[1] in ['True', 'true']) else True
#         #         hit = _Consent(consent)
#         #     else:
#         #         hit = Event(content[HitFields.event_category], content[HitFields.event_category])
#         # elif type == HitType.ITEM:
#         #     hit = Item(content[HitFields.transaction_id], content[HitFields.item_name], content[HitFields.item_code])
#         # elif type == HitType.TRANSACTION:
#         #     hit = Transaction(content[HitFields.transaction_id], content[HitFields.transaction_affiliation])
#         # elif type == HitType.ACTIVATE:
#         #     anonymous_id = content[HitFields.anonymous_id] if HitFields.anonymous_id in content else None
#         #     visitor_id = content[HitFields.visitor_id]
#         #     variation_group_id = content[HitFields.variation_group_id]
#         #     variation_id = content[HitFields.variation_id]
#         #     hit = _Activate(visitor_id, anonymous_id, variation_group_id, variation_id)
#         # elif type == HitType.SEGMENT:
#         #     visitor_id = content[HitFields.visitor_id]
#         #     hit = _Segment(visitor_id, )
#
#         hit = HitFactory(HitType(hit_json['type']).value).value(hit_json['content'])
#     except Exception as e:
#         log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())


class HitFactory:
    @staticmethod
    def from_json(hit_json):
        hit_id = ""
        try:
            hit_id = hit_json['id']
            hit_type = hit_json['type']
            content = hit_json['content']
            hit = {
                'SCREENVIEW': Screen.from_json,
                'PAGEVIEW': Page.from_json,
                'EVENT': Event.from_json,
                'TRANSACTION': Transaction.from_json,
                'ITEM': Item.from_json,
                'ACTIVATE': _Activate.from_json,
                'SEGMENT': _Segment.from_json
            }[hit_type](content)
            hit.id = hit_id
            hit.timestamp = hit_json['timestamp']
            hit.visitor_id = hit_json['visitorId']
            hit.anonymous_id = hit_json['anonymousId']
            hit.hit_data = content
            return hit
        except Exception as e:
            # log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())
            raise HitCacheFormatException(hit_id)
        return None
