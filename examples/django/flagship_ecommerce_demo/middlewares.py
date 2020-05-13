import json
import base64
import requests
import functools
from flagship.app import Flagship, Config


def cart(get_response):
    def middleware(request):
        if 'cart' not in request.session:
            request.session['cart'] = {}

        items = request.session['cart'].items()
        if len(items) > 0:
            total = 0
            for _, v in items:
                total += v
            request.session['cart_total'] = total
        else:
            request.session['cart_total'] = 0

        menu = [
            {'path': 'index', 'title': 'home'},
            {'path': 'about', 'title': 'about'},
            {'path': 'shop', 'title': 'shop'},
            {'path': 'shop', 'title': 'catalog'},
            {'path': 'shop', 'title': 'new arrivals'},
            {'path': 'contact', 'title': 'contact'}
        ]
        wishlist = False

        if 'fscookie' in request.COOKIES:
            fsconfig = json.loads(
                base64.b64decode(request.COOKIES['fscookie']))
            request.session['fs_config'] = fsconfig

            Flagship.instance().start(
                Config(fsconfig['environment_id'], ""))

            visitor = Flagship.instance().create_visitor(
                fsconfig['visitor_id'], fsconfig['context'])
            visitor.synchronize_modifications()

            # v1 = visitor.get_modification(3, 'default1')
            order = visitor.get_modification("menuOrder", "", True)
            wishlist = visitor.get_modification("wishlist", False, True)

            order = [x for x in order.split(
                ',')] if isinstance(order, str) else []
            request.session['fs_flags'] = {
                'menuOrder': order,
                'wishlist': wishlist
            }

            new_menu = []
            for m in order:
                found = next((x for x in menu if x['title'] == m), None)
                if found:
                    new_menu.append(found)

            for m in menu:
                found = next((x for x in order if x == m['title']), None)
                if found is None:
                    new_menu.append(m)

            menu = new_menu

        request.session['menu'] = menu
        request.session['wishlist'] = wishlist
        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
    return middleware
