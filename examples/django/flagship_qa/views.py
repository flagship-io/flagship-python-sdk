from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
import json
from flagship.app import Flagship, Config
from flagship.helpers.hits import Page, EventCategory, Event, Transaction, Item, Hit, HitType


def index(request):
    template = loader.get_template('flagship_qa/index.html')
    return HttpResponse(template.render({}, request))


def events(request):
    template = loader.get_template('flagship_qa/events.html')
    return HttpResponse(template.render({}, request))


def currentEnv(request):
    # if 'env_id' not in request.session:
    #     request.session['env_id'] = ''
    # return JsonResponse({'env_id': request.session['env_id']})
    conf = Flagship.instance()._config
    env_id = conf.env_id if conf is not None else ''
    return JsonResponse({'env_id': env_id})


@csrf_exempt
def setEnv(request):
    jsonData = json.loads(request.body)
    request.session['env_id'] = jsonData['environment_id']
    Flagship.instance().start(
        Config(request.session['env_id'], ""))
    return JsonResponse({})


@csrf_exempt
def setVisitor(request):
    try:
        jsonData = json.loads(request.body)
        visitor = Flagship.instance().create_visitor(
            jsonData['visitor_id'], jsonData['context'])

        result = visitor.update_context(jsonData['context'])

        error = ''
        if len(result) >= 1:
            for r in result[0]:
                if len(r) >= 2 and r[1] is False:
                    error += (r[2] + ', ')

        visitor.synchronize_modifications()

        request.session['visitor_id'] = jsonData['visitor_id']
        request.session['context'] = jsonData['context']

        modif = {}
        for key in visitor._modifications:
            modif[key] = visitor._modifications[key].value

        data = {
            'modifications': modif,
            'campaigns': json.loads(campaigns_to_str(visitor.campaigns)),
        }
        if len(error) > 0:
            data['error'] = error
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
        }, status=400)


def campaigns_to_str(campaigns):
    result = '['
    for c in campaigns:
        result += str(c) + ','
    result = result[:-1]
    result += ']'
    return result


@csrf_exempt
def sendHit(request):
    try:
        jsonData = json.loads(request.body)
        visitor = Flagship.instance().create_visitor(request.session['visitor_id'], request.session['context'])
        event = None
        if jsonData['t'] == 'EVENT':
            event = Event(EventCategory.USER_ENGAGEMENT, jsonData['ea'])
            if 'el' in jsonData:
                event.with_event_label(jsonData['el'])
            if 'ev' in jsonData:
                event.with_event_value(jsonData['ev'])

        if jsonData['t'] == 'PAGE':
            event = Page(jsonData['dl'])

        if jsonData['t'] == 'TRANSACTION':
            event = Transaction(jsonData['tid'], jsonData['ta'])
            if 'tt' in jsonData:
                event.with_taxes(jsonData['tt'])
            if 'tcc' in jsonData:
                event.with_coupon_code(jsonData['tcc'])
            if 'tc' in jsonData:
                event.with_currency(jsonData['tc'])
            if 'pm' in jsonData:
                event.with_payment_method(jsonData['pm'])
            if 'icn' in jsonData:
                event.with_item_count(jsonData['icn'])
            if 'ts' in jsonData:
                event.with_shipping_cost(jsonData['ts'])
            if 'sm' in jsonData:
                event.with_shipping_method(jsonData['sm'])
            if 'tr' in jsonData:
                event.with_total_revenue(jsonData['tr'])

        if jsonData['t'] == 'ITEM':
            event = Item(jsonData['tid'], jsonData['in'])
            if 'iv' in jsonData:
                event.with_item_category(jsonData['iv'])
            if 'ic' in jsonData:
                event.with_item_code(jsonData['ic'])
            if 'iq' in jsonData:
                event.with_item_quantity(jsonData['iq'])
            if 'ip' in jsonData:
                event.with_price(jsonData['ip'])

        if 'srw' in jsonData and 'srh' in jsonData:
            event.with_resolution(jsonData['srw'], jsonData['srh'])
        if 'uip' in jsonData:
            event.with_ip(str(jsonData['uip']))
        if 'ul' in jsonData:
            event.with_locale(jsonData['ul'])

        result = visitor.send_hit(event)
        if len(result) >= 2 and result[0] is False:
            return JsonResponse({
                'error': "Hit not sent, http code {}".format(result[1]),
            }, status=400)
        else:
            return JsonResponse({})
    except Exception as e:
        return JsonResponse({
            'error': str(e),
        }, status=400)


def getFlag(request, name):
    try:
        visitor = Flagship.instance().create_visitor(
            request.session['visitor_id'], request.session['context'])

        visitor.synchronize_modifications()

        activation = request.GET.get('activation', 'false')
        defaultValue = request.GET.get('defaultValue', '')
        valueType = request.GET.get('type', 'string')

        if valueType == 'bool':
            defaultValue = defaultValue == 'true'
        if valueType == 'number':
            defaultValue = float(defaultValue)

        flag_info = visitor.get_modification_with_info(name, defaultValue, activation == 'true')
        return JsonResponse({
            'err': False,
            'value': str(flag_info[0]),
            'info_f': flag_info[1],
            'info': str(flag_info[2]),
            'activated': flag_info[3][0] if (len(flag_info) >= 3 and flag_info[3] is not None) else False
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
        }, status=400)


@csrf_exempt
def activate(request, name):
    try:

        visitor = Flagship.instance().create_visitor(
            request.session['visitor_id'], request.session['context'])
        visitor.synchronize_modifications()
        result = visitor.activate_modification(name)
        print(result)
        if result[0] is False and len(result) >= 2:
            return JsonResponse({
                'error': result[1],
            }, status=400)
        else:
            return JsonResponse({
                'err': False,
                'value': 'Sent'
            }, status=200)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
        }, status=400)
