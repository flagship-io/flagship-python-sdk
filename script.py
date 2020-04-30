import sys
from threading import Timer

from typing import Any, Union

from flagship.app import Flagship
from flagship.config import Config
from flagship.handler import FlagshipEventHandler
from flagship.helpers.hits import Page, EventCategory, Event, Transaction, Item, Hit, HitType
from flagship.visitor import FlagshipVisitor


class Test():
    def __init__(self):
        pass


class CustomEventHandler(FlagshipEventHandler):
    def __init__(self):
        FlagshipEventHandler.__init__(self)

    def on_log(self, level, message):
        FlagshipEventHandler.on_log(self, level, ">>> " + message)
        # print("on log >> " + message)
        pass

    def on_exception_raised(self, exception, traceback):
        FlagshipEventHandler.on_exception_raised(self, exception, traceback)
        # print("on exception >> " + str(exception))
        pass


def init():
    print(sys.version)
    t = CustomEventHandler()
    Flagship.instance().start(
        Config("bkk4s7gcmjcg07fke9dg", "j2jL0rzlgVaODLw2Cl4JC3f4MflKrMgIaQOENv36", event_handler=t))
    # print(Flagship()._config)
    visitor = Flagship.instance().create_visitor("8888", {'isVIPUser': True})  # type: FlagshipVisitor
    # visitor2 = Flagship.instance().create_visitor(23, 22)
    visitor.synchronize_modifications()

    print(str(visitor.get_modification_with_info("k1", "coucou", True)))
    print(str(visitor.get_modification_with_info("kzjfke", 9487, True)))
    v1 = visitor.get_modification('k1', 'default1', True)
    v2 = visitor.get_modification('k2', 'default2', True)
    v3 = visitor.get_modification('k3', 'default3', True)
    v6 = visitor.get_modification('k6', 'default6', True)
    v7 = visitor.get_modification('k7', 'default7', True)
    print("v1 = " + str(v1))
    print("v2 = " + str(v2))
    print("v3 = " + str(v3))
    print("v6 = " + str(v6))
    print("v7 = " + str(v7))

    act = visitor.activate_modification('jeoz')
    print(act)

    visitor.update_context(('age', 666))
    visitor.update_context({'name': 'toto', 'tx': 9.99})

    t = Timer(2, send_visitor_hits, [visitor])
    t.start()
    visitor.synchronize_modifications()

    v = {'titi': 3}
    t = ('toto', 3)

   # test returned tuples

    updt = visitor.update_context((1, 3), False)
    print("False update = " + str(updt))
    updt2 = visitor.update_context({'toto': 34, 3: 4}, True)
    print("False update2 = " + str(updt2))

    # visitor.update_preset_context(True, toto="3", titi=True, tata=2, t=v)




    # qa_python_2(visitor)
    # qa_python_3(visitor)


def send_visitor_hits(visitor):
    # type: (FlagshipVisitor) -> None
    toto = visitor.send_hit(Page("script.py")
                            .with_ip("133.3.223.1")
                            .with_locale("fr-fr")
                            .with_resolution(640, 480)
                            .with_session_number(3))

    print("))) " + str(toto[0]) + ' ' + (str(toto[1])))

    visitor.send_hit(Event(EventCategory.USER_ENGAGEMENT, "kpi_qa_python_1")
                     .with_ip('6.6.6.6')
                     .with_event_label('this is my label')
                     .with_locale('fr-fr')
                     .with_event_value(666))

    visitor.send_hit(Event(EventCategory.USER_ENGAGEMENT, "KPI_QA_PYTHON_1")
                     .with_ip('x.x.x.x')
                     .with_event_label('this is my label')
                     .with_locale('fr-fr')
                     .with_event_value(777))

    visitor.send_hit(Transaction("#309830", "purchases")
                     .with_locale("uk-uk")
                     .with_ip("30.334.3.33")
                     .with_session_number(3)
                     .with_currency("EUR")
                     .with_item_count(3)
                     .with_payment_method("cb")
                     .with_shipping_cost(4.99)
                     .with_shipping_method("1d")
                     .with_taxes(9.99)
                     .with_total_revenue(420.00)
                     .with_coupon_code("#SAVE10"))

    visitor.send_hit(Item("#309830", "ATX2080")
                     .with_item_category("hardware")
                     .with_item_code("cg_atx_20802020")
                     .with_item_quantity(2)
                     .with_price(210.00))


def qa_python_2(visitor):
    print('___________qa_python_2___________')
    visitor.update_context(('isVIPUser', False))
    visitor.synchronize_modifications()
    my_flag_number = visitor.get_modification('my_flag_nb', -1)
    print(my_flag_number)
    visitor.activate_modification('my_flag_nb')
    print('___________qa_python_2___________')
    t = Timer(2, send_hit_qa_python_2, [visitor])
    t.start()


def send_hit_qa_python_2(visitor):
    print('___________qa_python_2______hit_____')
    visitor.send_hit(Transaction("#10101010101", "kpi_qa_python_2")
                     .with_locale("uk-uk")
                     .with_ip("30.334.3.33")
                     .with_session_number(3)
                     .with_currency("EUR")
                     .with_item_count(3)
                     .with_payment_method("cb")
                     .with_shipping_cost(4.99)
                     .with_shipping_method("1d")
                     .with_taxes(9.99)
                     .with_total_revenue(420.00)
                     .with_coupon_code("#SAVE10"))

    visitor.send_hit(Transaction("#10101010102", "KPI_QA_PYTHON_2")
                     .with_locale("uk-uk")
                     .with_ip("30.334.3.33")
                     .with_session_number(3)
                     .with_currency("EUR")
                     .with_item_count(3)
                     .with_payment_method("cb")
                     .with_shipping_cost(4.99)
                     .with_shipping_method("1d")
                     .with_taxes(9.99)
                     .with_total_revenue(10420.00)
                     .with_coupon_code("#SAVE10"))
    print('___________qa_python_2______hit_____')


def qa_python_3(visitor):
    print('___________qa_python_3___________')
    visitor.update_context({'age': 5}, True)
    text = visitor.get_modification('text', "default", True)
    print("Result : " + text)
    visitor.update_context({'age': 25}, True)
    text = visitor.get_modification('text', "default", True)
    print("Result : " + text)
    visitor.update_context({'age': 45}, True)
    text = visitor.get_modification('text', "default", True)
    print("Result : " + text)
    print('___________qa_python_3___________')
    t = Timer(2, send_hit_qa_python_3, [visitor])
    t.start()


def send_hit_qa_python_3(visitor):
    # type: (FlagshipVisitor) -> None
    print('___________qa_python_3______hit_____')
    # visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "qa_python_3")
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "kpi_qa_python_3")
                     .with_ip('6.6.6.6')
                     .with_resolution(1920, 1080)
                     .with_event_label('click')
                     .with_locale('fr-fr')
                     .with_event_value(111))
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "kpi_qa_python_3b")
                     .with_ip('6.6.6.6')
                     .with_resolution(1920, 1080)
                     .with_event_label('click')
                     .with_locale('fr-fr')
                     .with_event_value(111))
    visitor.send_hit(Event(EventCategory.ACTION_TRACKING, "KPI_QA_PYTHON_3c")
                     .with_ip('6.6.6.6')
                     .with_resolution(1920, 1080)
                     .with_event_label('click')
                     .with_locale('fr-fr')
                     .with_event_value(111))
    print('___________qa_python_3______hit_____')


init()
