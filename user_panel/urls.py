from django.urls import path
from.views import UserPanelProductListView,ProductDetailView

app_name = 'user_panel'

urlpatterns = [
    path('products/', UserPanelProductListView.as_view(), name='user_products'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]