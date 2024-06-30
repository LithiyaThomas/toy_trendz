from django.urls import path
from.views import UserPanelProductListView

app_name = 'user_panel'

urlpatterns = [
    path('products/', UserPanelProductListView.as_view(), name='user_products'),
]