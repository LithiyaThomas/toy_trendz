# urls.py
from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('product_list/', views.product_list, name='product_list'),
    path('product_create/', views.product_create, name='product_create'),
    path('<int:pk>/product_update/', views.product_update, name='product_update'),
    path('<int:pk>/product_delete/', views.product_delete, name='product_delete'),
    path('<int:pk>/product_restore/', views.product_restore, name='product_restore'),

    path('<int:product_id>/product_variant_list/', views.product_variant_list, name='product_variant_list'),
    path('<int:product_id>/product_variant_list/product_variant_create/', views.product_variant_create, name='product_variant_create'),
    path('<int:product_id>/product_variant_list/<int:pk>/product_variant_update/', views.product_variant_update, name='product_variant_update'),
    path('<int:product_id>/product_variant_list/<int:pk>/product_variant_delete/', views.product_variant_delete, name='product_variant_delete'),
    path('<int:product_id>/product_variant_list/<int:pk>/product_variant_restore/', views.product_variant_restore, name='product_variant_restore'),
]
