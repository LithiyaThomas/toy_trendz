from django.urls import path
from .views import *

app_name = 'product'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('<int:product_id>/variants/', ProductVariantListView.as_view(), name='product_variants'),
    path('<int:product_id>/variants/create/', ProductVariantCreateView.as_view(), name='product_variant_create'),
    path('<int:product_id>/variants/<int:pk>/edit/', ProductVariantUpdateView.as_view(), name='edit_variant'),  # Define edit_variant URL here
    path('<int:product_id>/variants/<int:pk>/delete/', ProductVariantDeleteView.as_view(), name='delete_variant'),
    path('<int:product_id>/images/', ProductImageListView.as_view(), name='product_images'),
    path('<int:product_id>/images/create/', ProductImageCreateView.as_view(), name='product_image_create'),
    path('product/<int:product_id>/images/<int:pk>/edit/', ProductImageUpdateView.as_view(), name='edit_image'),
    path('product/<int:product_id>/images/<int:pk>/delete/', ProductImageDeleteView.as_view(), name='delete_image'),

]
