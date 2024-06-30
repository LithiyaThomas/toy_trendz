# user_panel/views.py
from django.views.generic import ListView
from product.models import Product

class UserPanelProductListView(ListView):
    model = Product
    template_name = 'userside/product_list.html'  # Adjust the template name as per your project structure
    context_object_name = 'products'

    def get_queryset(self):
        # Customize the queryset as needed, for example, to filter or order products
        return Product.objects.all().select_related('product_category', 'product_brand') \
                             .prefetch_related('productvariant_set', 'productimage_set')
