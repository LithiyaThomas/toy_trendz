from django.urls import path
from .views import (
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductVariantCreateView,
    ProductImageCreateView,
    ProductVariantListView,
    ProductVariantUpdateView,
    ProductVariantDeleteView,
)

urlpatterns = [
    path('product_list/', ProductListView.as_view(), name='product_list'),
    path('product/<int:product_id>/variants/', ProductVariantListView.as_view(), name='product_variants'),
    path('product/new/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:product_id>/variant/new/', ProductVariantCreateView.as_view(), name='product_variant_create'),
    path('product/<int:product_id>/image/new/', ProductImageCreateView.as_view(), name='product_image_create'),
    path('product/variant/<int:pk>/edit/', ProductVariantUpdateView.as_view(), name='product_variant_update'),
    path('product/variant/<int:pk>/delete/', ProductVariantDeleteView.as_view(), name='product_variant_delete'),
]
