from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.http import JsonResponse
from django.contrib import messages
from decimal import Decimal
from decouple import config
from .models import *
import stripe

stripe.api_key = config('STRIPE_SECRET_KEY')


def CheckoutView(request, pk):
    item = Item.objects.get(pk=pk)
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': item.currency,
                'unit_amount': item.price * 100,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000',
        cancel_url=request.META.get('HTTP_REFERER'),
    )
    return JsonResponse({"session_id": session.id})


def OrderPaymentView(request, pk):
    order = Order.objects.get(pk=pk)
    session = stripe.checkout.Session.create(
        line_items=_get_order_items(order),
        mode='payment',
        discounts=_get_discount(order),
        success_url='http://127.0.0.1:8000',
        cancel_url=request.META.get('HTTP_REFERER'),
    )
    return JsonResponse({"session_id": session.id})


class HomePageView(TemplateView):
    template_name = 'index.html'


class ListItemsView(ListView):
    model = Item
    template_name = "ListItems.html"
    context_object_name = 'items'


class ItemsView(ListView):
    model = Item
    template_name = "item.html"
    context_object_name = 'item'

    def get(self, request, pk):
        item = Item.objects.get(pk=pk)
        context = {
            'item': item,
        }
        return render(request, 'item.html', context)


class ListOrdersView(ListView):
    model = Order
    template_name = "Listorders.html"
    context_object_name = 'orders'


class OrderView(ListView):
    model = Order

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        items = order.order_items.all()
        total_cost = 0
        for item in items:
            total_cost += _converter(item, order)
        context = {
            'order': order,
            'items': items,
            'total_cost': total_cost,
        }
        return render(request, 'order.html', context)


class AddItemView(ListView):
    model = Item
    template_name = "addItem.html"

    def post(self, request):
        try:
            item = Item.objects.create(name=request.POST.get("name"),
                                       description=request.POST.get("description"),
                                       price=request.POST.get("price"),
                                       img=request.FILES.get("img"),
                                       currency=request.POST.get("currency")
                                       )
            item.save()
            return redirect('ListItems')
        except:
            messages.error(request, "Проверьте введённые данные, возможно такой товар уже существует")
            return redirect('AddItem')


class AddOrderView(ListView):
    model = Item
    template_name = "addOrder.html"
    context_object_name = 'items'

    def get(self, request):
        super().get(request)
        discounts = Discount.objects.all()
        taxs = Tax.objects.all()
        items = Item.objects.all()
        context = {
            'discounts': discounts,
            'items': items,
            'taxs': taxs,
        }
        return self.render_to_response(context)

    def post(self, request):
        try:
            order = Order.objects.create()
            selected_items = request.POST.getlist("items")
            order.order_items.add(*Item.objects.filter(name__in=selected_items))
            order.currency = request.POST.get("currency")
            order.discounts.add(Discount.objects.get(name=request.POST.get("discounts")))
            order.tax.add(Tax.objects.get(name=request.POST.get("tax")))
            order.save()
            return redirect('ListOrders')
        except:
            messages.error(request, "Проверьте введённые данные")
            return redirect('AddOrder')


def _converter(item, order):
    total_cost = 0
    if item.currency == order.currency:
        total_cost += item.price
    else:
        match item.currency:
            case "BYN":
                total_cost += item.price / float(config('CURRENCY_RATE'))
            case "USD":
                total_cost += item.price * float(config('CURRENCY_RATE'))

    return Decimal('{:.2f}'.format(total_cost))


def _get_order_items(order):
    all_items = []
    for item in order.order_items.all():
        all_items.append(
            {
                'price_data': {
                    'currency': order.currency,
                    'product_data': {
                        'name': item.name,
                    },
                    'unit_amount_decimal': Decimal((_converter(item, order)).quantize(Decimal("1.00"))) * 100,
                },
                'quantity': 1,
                'tax_rates': _get_tax(order),
            }
        )
    return all_items


def _get_discount(order):
    discounts = []
    for discount in order.discounts.all():
        discounts.append(
            {
                'coupon': stripe.Coupon.create(
                    percent_off=discount.percent_off,
                    duration=discount.duration,
                ).id
            }
        )
    return discounts


def _get_tax(order):
    tax = []
    for taxs in order.tax.all():
        tax.append(
                stripe.TaxRate.create(
                    display_name=taxs.name,
                    inclusive=taxs.inclusive,
                    percentage=taxs.percentage,
                ).id
        )
    return tax

