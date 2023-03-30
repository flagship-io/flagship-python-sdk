import json
from time import sleep

import responses

from flagship import Flagship, LogLevel, Visitor
from flagship.config import DecisionApi
from flagship.hits import Page, Event, EventCategory, Transaction, Item, Screen
from flagship.tracking_manager import TrackingManagerConfig, TrackingManagerStrategy
from test_constants_res import DECISION_API_URL, API_RESPONSE_1, ACTIVATE_URL, EVENTS_URL


@responses.activate
def test_visitor_send_hits():
    Flagship.stop()
    Flagship.start('_env_id_', '_api_key_', DecisionApi(tracking_manager_config=TrackingManagerConfig(
                                                    strategy=TrackingManagerStrategy._NO_BATCHING_CONTINUOUS_CACHING_STRATEGY)))
    responses.reset()

    responses.add(responses.POST, DECISION_API_URL, json=json.loads(API_RESPONSE_1), status=200)
    # responses.add(responses.POST, ARIANE_URL, body="", status=200)
    responses.add(responses.POST, EVENTS_URL, body="", status=200)
    responses.add(responses.POST, ACTIVATE_URL, body="", status=200)

    visitor = Flagship.new_visitor("92bc-e237-a8d7-9234-bb78", instance_type=Visitor.Instance.NEW_INSTANCE,
                                   context={'isVIPUser': False})  # +1 consent

    sleep(0.05)
    visitor.fetch_flags() # +1 /campaigns
    sleep(0.05)

    visitor.send_hit(Screen("script.py")  # +1 Screen
                     .with_ip("133.3.223.1")
                     .with_locale("fr-fr")
                     .with_resolution(640, 480)
                     .with_session_number(3))
    sleep(0.05)

    visitor.send_hit(Page("https://www.script.python.fr")  # +1 Page
                     .with_ip("143.3.223.1")
                     .with_locale("fr-fr")
                     .with_resolution(640, 480)
                     .with_session_number(3))
    sleep(0.05)

    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "this is action")  # +1 Event
                     .with_ip('6.6.6.6')
                     .with_event_label('this is my label')
                     .with_locale('lol_hihi')
                     .with_event_value(323))
    sleep(0.05)

    visitor.send_hit(Transaction("#309830", "purchases")  # +1 Transaction
                     .with_locale("uk-uk")
                     .with_ip("30.334.3.33")
                     .with_session_number(3)
                     .with_currency("EUR")
                     .with_item_count(3)
                     .with_payment_method("credit_card")
                     .with_shipping_cost(4.99)
                     .with_shipping_method("1d")
                     .with_taxes(9.99)
                     .with_total_revenue(420.00)
                     .with_coupon_code("#SAVE10"))
    sleep(0.05)

    visitor.send_hit(Item("#309830", "ATX2080", "#cg_atx_20802020")  # +1 Item
                     .with_item_category("hardware")
                     .with_item_quantity(2)
                     .with_price(210.00))
    sleep(0.05)

    class FakeHit:
        def __init__(self):
            pass

    visitor.send_hit(FakeHit())

    sleep(0.3)

    calls = responses.calls._calls
    assert len(calls) == 7
    for i in range(0, len(calls)):
        c = calls[i]
        try:
            body = json.loads(c.request.body)
        except Exception as e:
            body = None
        if body is not None:
            if i == 0:
                assert body['t'] == 'EVENT'
                assert body['ds'] == 'APP'
                assert body['vid'] == '92bc-e237-a8d7-9234-bb78'
                assert body['cid'] == '_env_id_'
                assert body['ea'] == 'fs_consent'
                assert body['el'] == 'python:true'
                assert body['ec'] == 'User Engagement'
            # i == 1 => /Campaigns
            if i == 2:
                assert body['t'] == 'SCREENVIEW'
                assert body['ds'] == 'APP'
                assert body['vid'] == '92bc-e237-a8d7-9234-bb78'
                assert body['cid'] == '_env_id_'
                assert body['uip'] == '133.3.223.1'
                assert body['dl'] == 'script.py'
                assert body['sr'] == '640x480'
                assert body['ul'] == "fr-fr"
            if i == 3:
                assert body['t'] == 'PAGEVIEW'
                assert body['ds'] == 'APP'
                assert body['vid'] == '92bc-e237-a8d7-9234-bb78'
                assert body['cid'] == '_env_id_'
                assert body['uip'] == '143.3.223.1'
                assert body['dl'] == 'https://www.script.python.fr'
                assert body['sr'] == '640x480'
                assert body['ul'] == "fr-fr"
            if i == 4:
                assert body['t'] == 'EVENT'
                assert body['ds'] == 'APP'
                assert body['vid'] == '92bc-e237-a8d7-9234-bb78'
                assert body['cid'] == '_env_id_'
                assert body['uip'] == '6.6.6.6'
                assert body['ea'] == 'this is action'
                assert body['el'] == 'this is my label'
                assert body['ec'] == 'Action Tracking'
                assert body['ev'] == 323
            if i == 5:
                assert body['t'] == 'TRANSACTION'
                assert body['ds'] == 'APP'
                assert body['vid'] == '92bc-e237-a8d7-9234-bb78'
                assert body['cid'] == '_env_id_'
                assert body['uip'] == '30.334.3.33'
                assert body['ul'] == "uk-uk"
                assert body['icn'] == 3
                assert body['tt'] == 9.99
                assert body['tr'] == 420.00
                assert body['ts'] == 4.99
                assert body['tc'] == 'EUR'
                assert body['sm'] == '1d'
                assert body['tid'] == '#309830'
                assert body['ta'] == 'purchases'
                assert body['tcc'] == '#SAVE10'
                assert body['pm'] == 'credit_card'
            if i == 6:
                assert body['t'] == 'ITEM'
                assert body['ds'] == 'APP'
                assert body['vid'] == '92bc-e237-a8d7-9234-bb78'
                assert body['cid'] == '_env_id_'
                assert body['tid'] == '#309830'
                assert body['iv'] == 'hardware'
                assert body['in'] == 'ATX2080'
                assert body['ic'] == '#cg_atx_20802020'
                assert body['iq'] == 2
                assert body['ip'] == 210



