from adminapp.models import Category,Cart

def category_context(request):
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}

def cart_item_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_count = cart.items.count() if cart else 0
    else:
        cart_count = 0
    return {'cart_item_count': cart_count}