from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import Product, Cart, Order, OrderItem

def home(request):

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(
            name__icontains=query
        )
    else:
        products = Product.objects.all()

    return render(
        request,
        'home.html',
        {'products': products}
    )

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})


@login_required
def add_to_cart(request, product_id):

    product = Product.objects.get(id=product_id)

    if product.stock <= 0:
        return redirect('/')

    cart_item = Cart.objects.filter(
        user=request.user,
        product=product
    ).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(
            user=request.user,
            product=product,
            quantity=1
        )

    return redirect('/cart/')


@login_required
def cart(request):
    items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


@login_required
def increase_quantity(request, item_id):
    item = Cart.objects.get(id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('/cart/')


@login_required
def decrease_quantity(request, item_id):
    item = Cart.objects.get(id=item_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('/cart/')


@login_required
def remove_item(request, item_id):
    item = Cart.objects.get(id=item_id, user=request.user)
    item.delete()
    return redirect('/cart/')

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items:
        return redirect('/cart/')

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    order = Order.objects.create(
        user=request.user,
        total_price=total
    )

    for item in cart_items:

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

        # Reduce stock
        product = item.product
        product.stock -= item.quantity
        product.save()

    # Clear cart
    cart_items.delete()

    return render(
        request,
        'order_success.html',
        {'order': order}
    )
@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'order_history.html',
        {'orders': orders}
    )

def logout_view(request):
    logout(request)
    return redirect('/')