# user_panel/views.py
from django.views.generic import ListView
from product.models import Product
from django.views.generic import DetailView

class UserPanelProductListView(ListView):
    model = Product
    template_name = 'userside/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):

        return Product.objects.all().select_related('product_category', 'product_brand') \
                             .prefetch_related('productvariant_set', 'productimage_set')



class ProductDetailView(DetailView):
    model = Product
    template_name = 'userside/product_detail.html'
