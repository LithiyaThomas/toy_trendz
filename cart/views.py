from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from product.models import Product, ProductVariant
from coupon.models import Coupon
from django.views.decorators.http import require_POST
# Create your views here.

@login_required
@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        try:
            product_id = request.POST.get("product")
            variant_id = request.POST.get("variant")
            quantity = int(request.POST.get("quantity", 1))  # Default quantity to 1 if not provided

            if not variant_id:
                return JsonResponse({"error": "Variant ID is required"}, status=400)

            user = request.user
            product = get_object_or_404(Product, id=product_id)
            variant = get_object_or_404(ProductVariant, id=variant_id)

            if quantity > variant.variant_stock:
                return JsonResponse({"error": "Not enough stock available"}, status=400)

            with transaction.atomic():
                cart, _ = Cart.objects.get_or_create(user=user)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    defaults={"quantity": quantity},
                )

                if not created:
                    if cart_item.quantity + quantity > variant.variant_stock:
                        return JsonResponse({"error": "Not enough stock available"}, status=400)
                    cart_item.quantity += quantity
                    cart_item.save()

                total_price = cart.get_total_price()
                cart.discount_amount, cart.discounted_price = apply_coupon(cart, total_price)
                cart.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Variant added to cart',
                    'total_price': total_price,
                    'discount_amount': cart.discount_amount,
                    'discounted_price': cart.discounted_price
                })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def apply_coupon(cart, total_price):
    if cart.coupon_code:
        coupon = Coupon.objects.get(code=cart.coupon_code)
        if not (coupon.minimum_order_amount <= total_price <= coupon.maximum_order_amount):
            cart.coupon_code = None
            return 0, total_price
        discount_amount = (total_price * coupon.offer_percentage) / 100
        return discount_amount, total_price - discount_amount
    return 0, total_price


@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        # Create a new cart if it doesn't exist
        cart = Cart.objects.create(user=request.user)

    cart_items = CartItem.objects.filter(cart=cart)
    return render(request, 'cart/view_cart.html', {'cart': cart, 'cart_items': cart_items})


@login_required
@csrf_exempt
def update_cart_item(request, item_id):
    if request.method == "POST":
        try:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            quantity = int(request.POST.get("quantity"))
            variant = cart_item.variant

            if quantity > variant.variant_stock:
                return JsonResponse({"error": "Not enough stock available"}, status=400)

            cart_item.quantity = quantity
            cart_item.save()

            cart = cart_item.cart
            total_price = cart.get_total_price()
            cart.discount_amount, cart.discounted_price = apply_coupon(cart, total_price)
            cart.save()

            return JsonResponse({
                'success': True,
                'message': 'Cart item updated',
                'total_price': total_price,
                'discount_amount': cart.discount_amount,
                'discounted_price': cart.discounted_price
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
@csrf_exempt
def remove_cart_item(request, item_id):
    if request.method == "POST":
        try:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart_item.delete()

            cart = cart_item.cart
            total_price = cart.get_total_price()
            cart.discount_amount, cart.discounted_price = apply_coupon(cart, total_price)
            cart.save()

            return JsonResponse({
                'success': True,
                'message': 'Cart item removed',
                'total_price': total_price,
                'discount_amount': cart.discount_amount,
                'discounted_price': cart.discounted_price
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def filter_out_of_stock(request):
    show_out_of_stock = request.GET.get('show_out_of_stock') == 'true'
    products = Product.objects.all()

    if not show_out_of_stock:
        products = products.filter(variants__variant_stock__gt=0).distinct()

    return render(request, 'product/product_list.html', {'products': products})

@login_required
def advanced_search(request):
    query = request.GET.get('q')
    sort_by = request.GET.get('sort_by', 'name')  # Default sorting by name
    products = Product.objects.filter(name__icontains=query).order_by(sort_by)
    return render(request, 'product/product_list.html', {'products': products})
