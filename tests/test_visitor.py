import json
import time
import traceback
from flagship.app import Flagship
from flagship.config import Config
import responses
from flagship.handler import FlagshipEventHandler
from flagship.helpers.hits import Page, Event, EventCategory, Transaction, Item, Screen


def test_create_visitor_wrong_param():
    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None))
    try:
        visitor = fs.create_visitor(1, False, None)
        assert False
    except Exception as e:
        assert True


def test_create_visitor():
    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None))

    try:
        visitor = fs.create_visitor("Pam", False, {'isVIP': True})
        assert visitor._visitor_id == 'Pam'
        assert visitor._context['isVIP'] is True
        assert visitor._env_id == "my_env_id"
        assert visitor._api_key == "my_api_key"
        assert visitor._api_manager is not None
        assert visitor._api_manager._env_id == "my_env_id"
        assert visitor._api_manager.api_key == "my_api_key"
        assert len(visitor._modifications) == 0
        assert True
    except Exception as e:
        print(traceback.print_exc())
        assert False


def test_visitor_update_context():
    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None))

    class Eight:
        def __init__(self):
            pass

    visitor = fs.create_visitor("Pam", False, {'isVIP': True})
    visitor.update_context(('one', 1), False)
    visitor.update_context(('two', 2, 2))
    visitor.update_context({
        0: 'zero',
        'three': 3,
        'four': {},
        'five': "five",
        'six': [],
        'seven': 7.334,
        'eight': Eight()
    }, False)
    assert 0 not in visitor._context
    assert visitor._context['isVIP'] is True
    assert visitor._context['one'] == 1
    assert 'two' not in visitor._context
    assert visitor._context['three'] == 3
    assert 'four' not in visitor._context
    assert visitor._context['five'] == 'five'
    assert 'six' not in visitor._context
    assert visitor._context['seven'] == 7.334
    assert 'eight' not in visitor._context


@responses.activate
def test_visitor_synchronize():
    json_response = '{"visitorId":"visitor_1","campaigns":[{"id":"xxxxd0qhl5801abv9ib0",' \
                    '"variationGroupId":"xxxxd0qhl5801abv9ic0","variation":{"id":"xxxxd0qhl5801abv9icg",' \
                    '"modifications":{"type":"FLAG","value":{"featureEnabled":true}}}}]} '

    json_response2 = '{"visitorId":"visitor_1","campaigns":[{"id":"xxxxesjojh803lh57qo0",' \
                     '"variationGroupId":"xxxxesjojh803lh57qp0","variation":{"id":"xxxxesjojh803lh57qpg",' \
                     '"modifications":{"type":"FLAG","value":{"my_flag_nb":100}}}},{"id":"xxxxsp9j5mf4g0fdhkv2g",' \
                     '"variationGroupId":"xxxxp9j5mf4g0fdhkv3g","variation":{"id":"xxxxp9j5mf4g0fdhkv4g",' \
                     '"modifications":{"type":"JSON","value":{"btn-color":"red"}}}},{"id":"xxxxrfe4jaeg0gi1bhog",' \
                     '"variationGroupId":"xxxxrfe4jaeg0gi1bhpg","variation":{"id":"xxxxrfe4jaeg0gi1bhq0",' \
                     '"modifications":{"type":"FLAG","value":{"featureEnabled":true}}}},{"id":"xxxx9b1q4vl00quhh0rg",' \
                     '"variationGroupId":"xxxx9b1q4vl00quhh0sg","variation":{"id":"xxxx9b1q4vl00quhh0tg",' \
                     '"modifications":{"type":"JSON","value":{"k1":"v1","k2":null,"k3":null,"k6":"v6","k7":null}}}}]} '

    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None, mode=Config.Mode.API))
    visitor = fs.create_visitor("visitor_1", True)
    responses.reset()
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent=false',
                  json=json.loads(json_response), status=200)
    responses.add(responses.POST, 'https://decision.flagship.io/v2/my_env_id/events', status=200)

    visitor.synchronize_modifications()
    assert 'featureEnabled' in visitor._modifications
    assert visitor._modifications['featureEnabled'].value is True
    assert visitor._modifications['featureEnabled'].variation_group_id == 'xxxxd0qhl5801abv9ic0'
    assert visitor._modifications['featureEnabled'].variation_id == 'xxxxd0qhl5801abv9icg'

    responses.reset()
    responses.add(responses.POST, 'https://decision.flagship.io/v2/my_env_id/events', status=200)
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent=false',
                  json=json.loads(json_response2), status=200)
    visitor.synchronize_modifications()

    assert 'featureEnabled' in visitor._modifications
    assert visitor._modifications['featureEnabled'].value is True
    assert visitor._modifications['featureEnabled'].variation_group_id == 'xxxxrfe4jaeg0gi1bhpg'
    assert visitor._modifications['featureEnabled'].variation_id == 'xxxxrfe4jaeg0gi1bhq0'

    assert 'my_flag_nb' in visitor._modifications
    assert visitor._modifications['my_flag_nb'].value == 100
    assert visitor._modifications['my_flag_nb'].variation_group_id == 'xxxxesjojh803lh57qp0'
    assert visitor._modifications['my_flag_nb'].variation_id == 'xxxxesjojh803lh57qpg'

    assert 'k7' in visitor._modifications
    assert visitor._modifications['k7'].value is None
    assert visitor._modifications['k7'].variation_group_id == 'xxxx9b1q4vl00quhh0sg'
    assert visitor._modifications['k7'].variation_id == 'xxxx9b1q4vl00quhh0tg'

    info = visitor.get_modification_info('k7')

    assert info['campaignId'] == 'xxxx9b1q4vl00quhh0rg'
    assert info['variationGroupId'] == 'xxxx9b1q4vl00quhh0sg'
    assert info['variationId'] == 'xxxx9b1q4vl00quhh0tg'


@responses.activate
def test_visitor_get_modification():
    print("_______________________________1_____________________________________")
    json_response2 = '{"visitorId":"visitor_1","campaigns":[{"id":"xxxxesjojh803lh57qo0",' \
                     '"variationGroupId":"xxxxesjojh803lh57qp0","variation":{"id":"xxxxesjojh803lh57qpg",' \
                     '"modifications":{"type":"FLAG","value":{"my_flag_nb":100}}}},{"id":"xxxxsp9j5mf4g0fdhkv2g",' \
                     '"variationGroupId":"xxxxp9j5mf4g0fdhkv3g","variation":{"id":"xxxxp9j5mf4g0fdhkv4g",' \
                     '"modifications":{"type":"JSON","value":{"btn-color":"red"}}}},{"id":"xxxxrfe4jaeg0gi1bhog",' \
                     '"variationGroupId":"xxxxrfe4jaeg0gi1bhpg","variation":{"id":"xxxxrfe4jaeg0gi1bhq0",' \
                     '"modifications":{"type":"FLAG","value":{"featureEnabled":true}}}},{"id":"xxxx9b1q4vl00quhh0rg",' \
                     '"variationGroupId":"xxxx9b1q4vl00quhh0sg","variation":{"id":"xxxx9b1q4vl00quhh0tg",' \
                     '"modifications":{"type":"JSON","value":{"k1":"v1","k2":null,"k3":null,"k6":"v6","k7":null}}}}]} '

    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None, mode=Config.Mode.API))
    visitor = fs.create_visitor("visitor_1", True)

    responses.reset()
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent=false',
                  json=json.loads(json_response2), status=200)
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/events', status=200)
    responses.add(responses.POST, 'https://decision.flagship.io/v2/activate', status=200)

    val = visitor.synchronize_modifications()
    assert visitor.get_modification("aaaaaaaa", "bbbb", True) == 'bbbb'
    assert visitor.get_modification("btn-color", 'blue', True) == 'red'


@responses.activate
def test_visitor_get_modification2():
    json_response2 = '{"visitorId":"visitor_1","campaigns":[{"id":"xxxxesjojh803lh57qo0",' \
                     '"variationGroupId":"xxxxesjojh803lh57qp0","variation":{"id":"xxxxesjojh803lh57qpg",' \
                     '"modifications":{"type":"FLAG","value":{"my_flag_nb":100}}}},{"id":"xxxxsp9j5mf4g0fdhkv2g",' \
                     '"variationGroupId":"xxxxp9j5mf4g0fdhkv3g","variation":{"id":"xxxxp9j5mf4g0fdhkv4g",' \
                     '"modifications":{"type":"JSON","value":{"btn-color":"red"}},"reference":true}},' \
                     '{"id":"xxxxrfe4jaeg0gi1bhog","variationGroupId":"xxxxrfe4jaeg0gi1bhpg","variation":{' \
                     '"id":"xxxxrfe4jaeg0gi1bhq0","modifications":{"type":"FLAG","value":{"featureEnabled":true}}}},' \
                     '{"id":"xxxx9b1q4vl00quhh0rg","variationGroupId":"xxxx9b1q4vl00quhh0sg","variation":{' \
                     '"id":"xxxx9b1q4vl00quhh0tg","modifications":{"type":"JSON","value":{"k1":"v1","k2":null,' \
                     '"k3":null,"k6":"v6","k7":null}}}},{"id":"bsbgq4rjhsqg11tntt1g",' \
                     '"variationGroupId":"bsbgq4rjhsqg11tntt2g","variation":{"id":"bsbgq4rjhsqg11tntt3g",' \
                     '"modifications":{"type":"JSON","value":{"array":[1,2,3],"complex":{"carray":[{"cobject":0}]},' \
                     '"object":{"value":123456}}},"reference":false}}]} '

    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None, mode=Config.Mode.API))
    visitor = fs.create_visitor("visitor_1", True)

    responses.reset()
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent=false',
                  json=json.loads(json_response2), status=200)
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/events', status=200)

    responses.add(responses.POST, 'https://decision.flagship.io/v2/activate', status=200)

    visitor.update_context(('titi', 4), True)

    assert visitor.get_modification("aaaaaaaa", "bbbb", True) == 'bbbb'
    assert visitor.get_modification("btn-color", 'blue', True) == 'red'
    assert visitor.get_modification("k2", 'yellow', True) == 'yellow'

    assert visitor.get_modification_info("btn-color")["isReference"] is True
    assert visitor.get_modification_info("k2")["isReference"] is False


    assert visitor.get_modification("btn-color", "yellow") == 'red'
    assert visitor.get_modification("do_not_exists", 'None') is "None"

    assert visitor.get_modification("complex", {}) == {"carray": [{"cobject": 0}]}
    assert visitor.get_modification("array", []) == [1, 2, 3]


@responses.activate
def test_visitor_get_activate():
    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None))
    visitor = fs.create_visitor("visitor_1", True)

    json_response = '{"visitorId":"visitor_1","campaigns":[{"id":"xxxxd0qhl5801abv9ib0",' \
                    '"variationGroupId":"xxxxd0qhl5801abv9ic0","variation":{"id":"xxxxd0qhl5801abv9icg",' \
                    '"modifications":{"type":"FLAG","value":{"featureEnabled":true}}}}]} '

    responses.reset()
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent=false',
                  json=json.loads(json_response), status=200)
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/events', status=200)
    visitor.synchronize_modifications()

    responses.add(responses.POST, 'https://decision.flagship.io/v2/activate', status=200)
    visitor.activate_modification('featureEnabled')
    visitor.activate_modification('xxxxxxx')


hit_nb = 0


@responses.activate
def test_visitor_send_hits():
    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None, mode=Config.Mode.API))
    visitor = fs.create_visitor("visitor_1", True)

    json_response = '{"visitorId":"visitor_1","campaigns":[{"id":"xxxxd0qhl5801abv9ib0",' \
                    '"variationGroupId":"xxxxd0qhl5801abv9ic0","variation":{"id":"xxxxd0qhl5801abv9icg",' \
                    '"modifications":{"type":"FLAG","value":{"featureEnabled":true}}}}]} '

    responses.reset()
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent=false',
                  json=json.loads(json_response), status=200)
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/events', status=200)
    visitor.synchronize_modifications()

    responses.add(responses.POST, 'https://ariane.abtasty.com/', status=200)

    visitor.send_hit(Screen("script.py")
                     .with_ip("133.3.223.1")
                     .with_locale("fr-fr")
                     .with_resolution(640, 480)
                     .with_session_number(3))

    visitor.send_hit(Page("not working"))
    visitor.send_hit(Page("http://working.com"))

    visitor.send_hit(Event(EventCategory.USER_ENGAGEMENT, "this is action")
                     .with_ip('6.6.6.6')
                     .with_event_label('this is my label')
                     .with_locale('lol_hihi')
                     .with_event_value(323))

    visitor.send_hit(Transaction("#309830", "purchases")
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

    visitor.send_hit(Item("#309830", "ATX2080", "#cg_atx_20802020")
                     .with_item_category("hardware")
                     .with_item_quantity(2)
                     .with_price(210.00))

    class FakeHit:
        def __init__(self):
            pass

    visitor.send_hit(FakeHit())
    assert len(responses.calls) == 7


@responses.activate
def test_visitor_panic():
    responses.reset()

    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(event_handler=None, mode=Config.Mode.API))
    visitor = fs.create_visitor("visitor_1", True)

    json_response = '{"visitorId":"visitor_1","campaigns":[{"id":"xxxxd0qhl5801abv9ib0",' \
                    '"variationGroupId":"xxxxd0qhl5801abv9ic0","variation":{"id":"xxxxd0qhl5801abv9icg",' \
                    '"modifications":{"type":"FLAG","value":{"featureEnabled":true}}}}]} '
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent=false',
                  json=json.loads(json_response), status=200)

    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/events', status=200)

    responses.add(responses.POST, 'https://ariane.abtasty.com/', status=200)

    visitor.synchronize_modifications()

    visitor.send_hit(Screen("script.py")
                     .with_ip("133.3.223.1")
                     .with_locale("fr-fr")
                     .with_resolution(640, 480)
                     .with_session_number(3))

    responses.add(responses.POST, 'https://decision.flagship.io/v2/activate', status=200)
    visitor.activate_modification('featureEnabled')

    assert visitor.get_modification("featureEnabled", False) is True
    assert len(responses.calls) == 4

    responses.reset()
    json_response_panic = '{"visitorId":"Toto3000","campaigns":[],"panic":true}'
    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent=false',
                  json=json.loads(json_response_panic), status=200)

    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/events', status=200)

    responses.add(responses.POST, 'https://ariane.abtasty.com/', status=200)

    visitor.synchronize_modifications()

    visitor.send_hit(Page("script.py")
                     .with_ip("133.3.223.1")
                     .with_locale("fr-fr")
                     .with_resolution(640, 480)
                     .with_session_number(3))

    responses.add(responses.POST, 'https://decision.flagship.io/v2/activate', status=200)
    visitor.activate_modification('featureEnabled')

    visitor.synchronize_modifications()

    assert visitor._is_panic_mode() is True
    assert visitor.get_modification("featureEnabled", False) is False
    assert len(responses.calls) == 2


@responses.activate
def test_visitor_authentication():
    responses.reset()

    json_response = '{"visitorId":"visitor_1","campaigns":[{"id":"xxxxd0qhl5801abv9ib0",' \
                    '"variationGroupId":"xxxxd0qhl5801abv9ic0","variation":{"id":"xxxxd0qhl5801abv9icg",' \
                    '"modifications":{"type":"FLAG","value":{"featureEnabled":true}}}}]} '

    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/campaigns/?exposeAllKeys=true&sendContextEvent'
                  '=false', json=json.loads(json_response), status=200)

    responses.add(responses.POST,
                  'https://decision.flagship.io/v2/my_env_id/events', status=200)

    responses.add(responses.POST, 'https://ariane.abtasty.com/', status=200)

    responses.add(responses.POST, 'https://decision.flagship.io/v2/activate', status=200)

    fs = Flagship.instance()
    fs.start("my_env_id", "my_api_key", Config(mode=Config.Mode.API, timeout=3000))
    visitor = fs.create_visitor()
    visitor.synchronize_modifications()

    assert len(json.loads(responses.calls[0].request.body)["visitorId"]) == 19
    assert 'anonymousId' not in json.loads(responses.calls[0].request.body)
    assert len(visitor._visitor_id) == 19

    responses.calls.reset()
    visitor.send_hit(Page("https://www.page.com"))
    assert len(json.loads(responses.calls[0].request.body)["vid"]) == 19
    assert 'cuid' not in json.loads(responses.calls[0].request.body)

    responses.calls.reset()
    visitor.activate_modification("featureEnabled")
    assert len(json.loads(responses.calls[0].request.body)["vid"]) == 19
    assert 'aid' not in json.loads(responses.calls[0].request.body)

    #############
    responses.calls.reset()
    visitor.authenticate("log_1", {"age": 31}, True)
    assert len(json.loads(responses.calls[0].request.body)["anonymousId"]) == 19
    assert json.loads(responses.calls[0].request.body)["visitorId"] == "log_1"
    assert visitor._visitor_id == "log_1"
    assert len(visitor._anonymous_id) == 19
    assert visitor.get_context()['age'] == 31

    responses.calls.reset()
    visitor.send_hit(Page("https://www.page.com"))
    assert len(json.loads(responses.calls[0].request.body)["vid"]) == 19
    assert json.loads(responses.calls[0].request.body)["cuid"] == "log_1"

    responses.calls.reset()
    visitor.activate_modification("featureEnabled")
    assert json.loads(responses.calls[0].request.body)["vid"] == "log_1"
    assert len(json.loads(responses.calls[0].request.body)["aid"]) == 19

    #############
    responses.calls.reset()
    visitor.unauthenticate(dict(), True)
    assert len(json.loads(responses.calls[0].request.body)["visitorId"]) == 19
    assert "anonymousId" not in json.loads(responses.calls[0].request.body)
    assert len(visitor._visitor_id) == 19
    assert visitor._anonymous_id is None
    assert len(visitor.get_context()) == 0

    responses.calls.reset()
    visitor.send_hit(Page("https://www.page.com"))
    assert len(json.loads(responses.calls[0].request.body)["vid"]) == 19
    assert "cuid" not in json.loads(responses.calls[0].request.body)

    responses.calls.reset()
    visitor.activate_modification("featureEnabled")
    assert 'aid' not in json.loads(responses.calls[0].request.body)
    assert len(json.loads(responses.calls[0].request.body)["vid"]) == 19

    #############
    responses.calls.reset()
    visitor.authenticate("log_2", {"age": 31}, True)
    assert len(json.loads(responses.calls[0].request.body)["anonymousId"]) == 19
    assert json.loads(responses.calls[0].request.body)["visitorId"] == "log_2"
    assert visitor._visitor_id == "log_2"
    assert len(visitor._anonymous_id) == 19
    assert visitor.get_context()['age'] == 31

    responses.calls.reset()
    visitor.send_hit(Page("https://www.page.com"))
    assert json.loads(responses.calls[0].request.body)["cuid"] == "log_2"
    assert len(json.loads(responses.calls[0].request.body)["vid"]) == 19

    responses.calls.reset()
    visitor.activate_modification("featureEnabled")
    assert json.loads(responses.calls[0].request.body)["vid"] == "log_2"
    assert len(json.loads(responses.calls[0].request.body)["aid"]) == 19

    #############
    responses.calls.reset()
    visitor2 = fs.create_visitor("visitor_2", True)
    visitor2.synchronize_modifications()

    assert json.loads(responses.calls[0].request.body)["visitorId"] == "visitor_2"
    assert len(json.loads(responses.calls[0].request.body)["anonymousId"]) == 19
    assert visitor2._visitor_id == "visitor_2"
    assert len(visitor2._anonymous_id) == 19

    responses.calls.reset()
    visitor2.send_hit(Screen("Here"))
    assert len(json.loads(responses.calls[0].request.body)["vid"]) == 19
    assert json.loads(responses.calls[0].request.body)["cuid"] == "visitor_2"

    responses.calls.reset()
    visitor2.activate_modification("featureEnabled")
    assert len(json.loads(responses.calls[0].request.body)["aid"]) == 19
    assert json.loads(responses.calls[0].request.body)["vid"] == "visitor_2"
