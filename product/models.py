from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from PIL import Image
from category.models import Category
from brand.models import Brand

class Type(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def permanent_delete(self):
        super(Type, self).delete()

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='brand_products', on_delete=models.CASCADE)
    product_type = models.ForeignKey(Type, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'product'
        ordering = ['-id']

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def permanent_delete(self):
        super(Product, self).delete()

    objects = models.Manager()
    available_objects = models.Manager()  # For retrieving non-deleted items

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

def validate_price_within_range(value):
    if not (0 <= value <= ProductVariant.MAX_PRICE):
        raise ValidationError(f'Price must be between 0 and {ProductVariant.MAX_PRICE}.')

def validate_stock_within_range(value):
    if not (0 <= value <= ProductVariant.MAX_STOCK):
        raise ValidationError(f'Stock must be between 0 and {ProductVariant.MAX_STOCK}.')

class ProductVariant(models.Model):
    MAX_PRICE = 1000
    MAX_STOCK = 1000

    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_price_within_range])
    stock = models.PositiveIntegerField(validators=[validate_stock_within_range])
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def permanent_delete(self):
        super(ProductVariant, self).delete()

    @property
    def discounted_price(self):
        best_discount_percentage = self.product.get_best_discount_percentage()
        discount_amount = self.price * best_discount_percentage / 100
        return round(self.price - discount_amount, 2)

    @property
    def get_variant_image(self):
        return self.images.first().image.url if self.images.exists() else 'default_image_path'

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='photos/productvariant')
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(ProductImage, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def permanent_delete(self):
        super(ProductImage, self).delete()

    def __str__(self):
        return f"Image for {self.variant.name}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'variant')

    def __str__(self):
        return f"Review of {self.user}"
