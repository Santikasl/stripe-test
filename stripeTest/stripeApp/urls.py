from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.HomePageView.as_view(), name='Home'),
    path('buy/<pk>', views.CheckoutView, name='buy'),
    path('payment/<pk>', views.OrderPaymentView, name='payment'),
    path('items/', views.ListItemsView.as_view(), name='ListItems'),
    path('items/<pk>', views.ItemsView.as_view(), name='Items'),
    path('orders/', views.ListOrdersView.as_view(), name='ListOrders'),
    path('orders/<pk>', views.OrderView.as_view(), name='Order'),
    path('additem/', views.AddItemView.as_view(), name='AddItem'),
    path('addorder/', views.AddOrderView.as_view(), name='AddOrder'),

]
