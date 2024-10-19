from django import template
from django.urls import resolve

register = template.Library()

@register.simple_tag(takes_context=True)
def breadcrumb(context):
    request = context['request']
    url_name = resolve(request.path).url_name
    
    breadcrumbs = []
    path = request.path.split('/')
    
    # Customize breadcrumbs based on URL segments
    breadcrumbs.append(('Home', '/'))
    
    if 'productView' in url_name:
        breadcrumbs.append(('Shop', '/shopNow/'))
        # Add product name dynamically
        product = context.get('product', None)
        if product:
            breadcrumbs.append((product.name, request.path))
    
    return breadcrumbs