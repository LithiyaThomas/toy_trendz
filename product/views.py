from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy, reverse
from .models import (Product, ProductVariant, Category, Brand, Rating, ProductVariantImage)
from .forms import (ProductForm, ProductVariantForm,ProductVariantImageForm)
from django.shortcuts import get_object_or_404
from django.views.generic.edit import View
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
# Product ListView
class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.select_related('product_category', 'product_brand') \
            .prefetch_related('productvariant_set__productvariantimage_set') \
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
class ProductToggleActiveView(View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(pk=kwargs['pk'])
        product.is_active = not product.is_active
        product.save()
        return HttpResponseRedirect(reverse('product:product_list'))


# Product DetailView
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Fetch ratings for the product
        ratings = Rating.objects.filter(product=product)

        # Calculate average rating if ratings exist
        if ratings.exists():
            total_ratings = ratings.count()
            average_rating = sum([rating.rating for rating in ratings]) / total_ratings
            product.average_rating = round(average_rating, 2)
            product.total_reviews = total_ratings
            product.save()

        context['ratings'] = ratings
        return context

# Product Variant CreateView
class ProductVariantCreateView(CreateView):
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'product/product_variant_form.html'

    def get_success_url(self):
        return reverse_lazy('product:product_variants', kwargs={'product_id': self.kwargs['product_id']})

    def form_valid(self, form):
        product_id = self.kwargs['product_id']
        colour_name = form.cleaned_data['colour_name']

        # Check if the color already exists for this product
        if ProductVariant.objects.filter(product_id=product_id, colour_name=colour_name).exists():
            messages.error(self.request, f"The color '{colour_name}' already exists for this product.")
            return self.form_invalid(form)

        form.instance.product_id = product_id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        context['product'] = product
        return context

# Product Variant UpdateView
class ProductVariantUpdateView(UpdateView):
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'product/product_variant_form.html'

    def get_success_url(self):
        return reverse_lazy('product:product_variants', kwargs={'product_id': self.object.product_id})

# Product Variant DeleteView
class ProductVariantDeleteView(View):
    def get(self, request, pk):
        variant = get_object_or_404(ProductVariant, pk=pk)
        # Toggle active state
        variant.variant_status = not variant.variant_status
        variant.save()
        return redirect('product:product_variants', product_id=variant.product_id)

# Product Variant ListView
class ProductVariantListView(ListView):
    template_name = 'product/product_variant_list.html'
    context_object_name = 'variants'

    def get_queryset(self):
        return ProductVariant.objects.filter(product_id=self.kwargs['product_id']).prefetch_related('productvariantimage_set')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['product_id'])
        return context


class ProductVariantImageCreateView(View):
    template_name = 'product/productvariantimage_form.html'

    def get(self, request, pk):
        variant = get_object_or_404(ProductVariant, pk=pk)
        return render(request, self.template_name, {'variant': variant})

    def post(self, request, pk):
        variant = get_object_or_404(ProductVariant, pk=pk)
        files = request.FILES.getlist('images')
        for file in files:
            ProductVariantImage.objects.create(variant=variant, image=file)
        return redirect(reverse_lazy('product:product_variants', kwargs={'product_id': variant.product.id}))



# Demo View
class DemoView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/crop.html'
    success_url = reverse_lazy('product:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context
