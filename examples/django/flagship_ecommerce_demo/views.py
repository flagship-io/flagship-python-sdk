from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django import forms
import functools

products = [{
    "id": 1,
    "name": "Tank Top",
    "image": "ecommerce/images/cloth_1.jpg",
    "description": "Finding perfect t-shirt",
    "price": 50
}, {
    "id": 2,
    "name": "Corater",
    "image": "ecommerce/images/shoe_1.jpg",
    "description": "Finding perfect products",
    "price": 70
}, {
    "id": 3,
    "name": "T-Shirt",
    "image": "ecommerce/images/cloth_2.jpg",
    "description": "The perfect T-Shirt",
    "price": 30
}, {
    "id": 4,
    "name": "Polo",
    "image": "ecommerce/images/cloth_3.jpg",
    "description": "The perfect polo",
    "price": 80
}]


def index(request):
    return render(request, 'index.html', {})


def shop(request):
    return render(request, 'shop.html', {"products": products})


def product(request, id):
    if request.method == 'POST':
        if request.POST['id'] not in request.session['cart']:
            request.session['cart'][request.POST['id']] = 0

        request.session['cart'][request.POST['id']] += int(
            request.POST['quantity'])

        total = 0
        for _, v in request.session['cart'].items():
            total += v
        request.session['cart_total'] = total

    product = [p for p in products if p['id'] == id][0]
    return render(request, 'product.html', {"product": product})


def about(request):
    return render(request, 'about.html', {})


def contact(request):
    return render(request, 'contact.html', {})


def cart(request):
    if request.method == 'POST':
        new_cart = {}
        for k in request.POST:
            try:
                _ = int(k)
                new_cart[k] = int(request.POST[k][0])
            except:
                continue
        request.session['cart'] = new_cart

    products_cart = []
    total = 0
    for id, quantity in request.session['cart'].items():
        product = [p for p in products if str(p['id']) == id][0]
        product['quantity'] = quantity
        product['total_price'] = quantity * product['price']
        total += quantity * product['price']
        products_cart.append(product)

    return render(request, 'cart.html', {'products': products_cart, 'total': total})


def checkout(request):
    products_cart = []
    total = 0
    for id, quantity in request.session['cart'].items():
        product = [p for p in products if str(p['id']) == id][0]
        product['quantity'] = quantity
        product['total_price'] = quantity * product['price']
        total += quantity * product['price']
        products_cart.append(product)

    return render(request, 'checkout.html', {'products': products_cart, 'total': total})


def thankyou(request):
    return render(request, 'thankyou.html', {})
