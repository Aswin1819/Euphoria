from django.http import HttpResponseRedirect
from django.urls import reverse
from functools import wraps

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('adminLogin'))
        if not request.user.is_superuser:
            return HttpResponseRedirect(reverse('adminLogin'))  # Redirect or show error
        return view_func(request, *args, **kwargs)
    return _wrapped_view
