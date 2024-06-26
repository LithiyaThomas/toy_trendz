from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy,reverse
from .models import Product, ProductVariant, ProductImage, Category, Brand
from .forms import ProductForm, ProductVariantForm, ProductImageForm
from django.shortcuts import get_object_or_404

# Product ListView
class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.select_related('product_category', 'product_brand') \
                              .prefetch_related('productvariant_set', 'productimage_set') \
                              .all()
# Product CreateView
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_form.html'
    success_url = reverse_lazy('product:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context

# Product UpdateView
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_form.html'
    success_url = reverse_lazy('product:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context

    def get_queryset(self):
        return Product.objects.select_related('product_category', 'product_brand').all()

# Product DeleteView
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = reverse_lazy('product:product_list')

# Product Variant CreateView
class ProductVariantCreateView(CreateView):
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'product/product_variant_form.html'

    def get_success_url(self):
        return reverse_lazy('product_variants', kwargs={'product_id': self.kwargs['product_id']})

    def form_valid(self, form):
        form.instance.product_id = self.kwargs['product_id']
        return super().form_valid(form)

# Product Variant UpdateView
class ProductVariantUpdateView(UpdateView):
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'product/product_variant_form.html'

    def get_success_url(self):
        return reverse_lazy('product_variants', kwargs={'product_id': self.object.product_id})

# Product Variant DeleteView
class ProductVariantDeleteView(DeleteView):
    model = ProductVariant
    template_name = 'product/product_variant_confirm_delete.html'
    success_url = reverse_lazy('product_list')  # Adjust as per your application

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['variant'] = self.get_object()  # Ensure `get_object()` retrieves the correct variant
        return context


class ProductVariantListView(ListView):
    model = ProductVariant
    template_name = 'product/product_variant_list.html'
    context_object_name = 'variants'

    def get_queryset(self):
        self.product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return ProductVariant.objects.filter(product=self.product)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context


# Product Image CreateView
class ProductImageCreateView(CreateView):
    model = ProductImage
    form_class = ProductImageForm
    template_name = 'product/product_image_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.instance.product_id = self.kwargs['product_id']
        return super().form_valid(form)


class ProductImageListView(ListView):
    model = ProductImage
    template_name = 'product/product_image_list.html'
    context_object_name = 'product_images'

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        self.product = get_object_or_404(Product, pk=product_id)
        return ProductImage.objects.filter(product=self.product)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

# ProductImageUpdateView
class ProductImageUpdateView(UpdateView):
    model = ProductImage
    form_class = ProductImageForm
    template_name = 'product/product_image_form.html'

    def get_success_url(self):
        return reverse('product_images', kwargs={'product_id': self.object.product.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object.product
        return context

# ProductImageDeleteView
class ProductImageDeleteView(DeleteView):
    model = ProductImage
    template_name = 'product/product_image_confirm_delete.html'

    def get_success_url(self):
        return reverse('product_images', kwargs={'product_id': self.object.product.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object.product
        return context



