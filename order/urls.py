from django.urls import path
from .views import list_orders, change_order_status, cancel_order

urlpatterns = [
    path('orders/', list_orders, name='list_orders'),
    path('orders/<uuid:order_uuid>/status/<str:new_status>/', change_order_status, name='change_order_status'),
    path('orders/<uuid:order_uuid>/cancel/', cancel_order, name='cancel_order'),
]
