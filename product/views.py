from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductVariant
from category.models import Category
from brand.models import Brand

def product_list(request):
    products = Product.objects.filter(is_deleted=False)
    return render(request, 'product/product_list.html', {'product': products})


def product_create(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        featured = 'featured' in request.POST

        category = Category.objects.get(id=category_id)
        brand = Brand.objects.get(id=brand_id)

        product = Product(
            product_name=product_name,
            description=description,
            category=category,
            brand=brand,
            featured=featured
        )
        product.save()
        return redirect('product_list')

    categories = Category.available_objects.all()
    brands = Brand.available_objects.all()
    return render(request, 'product/product_form.html', {
        'categories': categories,
        'brands': brands
    })

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.description = request.POST.get('description')
        product.category = get_object_or_404(Category, id=request.POST.get('category'))
        product.brand = get_object_or_404(Brand, id=request.POST.get('brand'))
        product.featured = request.POST.get('featured', False) == 'on'

        product.save()
        return redirect('product:product_list')

    categories = Category.available_objects.all()
    brands = Brand.available_objects.all()
    return render(request, 'product/product_form.html', {
        'product': product,
        'categories': categories,
        'brands': brands,
    })

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.soft_delete()
    return redirect('product:product_list')

def product_restore(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.restore()
    return redirect('product:product_list')

def product_variant_list(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    variants = product.variants.filter(is_deleted=False)
    return render(request, 'product/product_variant_list.html', {'product': product, 'variants': variants})

def product_variant_create(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        is_active = request.POST.get('is_active', False) == 'on'

        variant = ProductVariant(
            product=product,
            name=name,
            price=price,
            stock=stock,
            is_active=is_active
        )
        variant.save()
        return redirect('product:product_variant_list', product_id=product.id)

    return render(request, 'product/product_variant_form.html', {'product': product})

def product_variant_update(request, product_id, pk):
    product = get_object_or_404(Product, pk=product_id)
    variant = get_object_or_404(ProductVariant, pk=pk)
    if request.method == 'POST':
        variant.name = request.POST.get('name')
        variant.price = request.POST.get('price')
        variant.stock = request.POST.get('stock')
        variant.is_active = request.POST.get('is_active', False) == 'on'

        variant.save()
        return redirect('product:product_variant_list', product_id=product.id)

    return render(request, 'product/product_variant_form.html', {'product': product, 'variant': variant})

def product_variant_delete(request, product_id, pk):
    product = get_object_or_404(Product, pk=product_id)
    variant = get_object_or_404(ProductVariant, pk=pk)
    variant.soft_delete()
    return redirect('product:product_variant_list', product_id=product.id)

def product_variant_restore(request, product_id, pk):
    product = get_object_or_404(Product, pk=product_id)
    variant = get_object_or_404(ProductVariant, pk=pk)
    variant.restore()
    return redirect('product:product_variant_list', product_id=product.id)
