# user_panel/views.py
from django.views.generic import ListView
from product.models import Product, Rating,ProductVariantImage
from django.views.generic import DetailView
from django.shortcuts import redirect, get_object_or_404
from .forms import RatingForm
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from product.models import Product, ProductVariant


class UserPanelProductListView(ListView):
    model = Product
    template_name = 'userside/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.all().select_related('product_category', 'product_brand') \
                             .prefetch_related(Prefetch('productvariant_set', queryset=ProductVariant.objects.prefetch_related('productvariantimage_set')))
class ProductDetailView(DetailView):
    model = Product
    template_name = 'userside/product_detail.html'
    context_object_name = 'product'

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

        # Fetch thumbnail image if available
        context['thumbnail_image'] = product.thumbnail.url if product.thumbnail else None

        # Fetch variant images
        context['variant_images'] = ProductVariantImage.objects.filter(variant__product=product)

        context['ratings'] = ratings
        context['rating_form'] = RatingForm(initial={'product_id': product.id})
        context['rating_range'] = range(1, 6)  # Assuming you want to display a range of ratings

        return context
class AddRatingView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = RatingForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            rating = form.cleaned_data['rating']
            review = form.cleaned_data['review']
            product = get_object_or_404(Product, pk=product_id)

            Rating.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                review=review
            )

            return redirect('user_panel:product_detail', pk=product_id)
        else:
            return redirect('user_panel:user_products')
