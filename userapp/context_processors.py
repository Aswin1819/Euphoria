from adminapp.models import Category

def category_context(request):
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}