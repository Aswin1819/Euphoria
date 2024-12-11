from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from .models import EuphoUser
from django.contrib.auth import login

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user.id:
            return
        try:
            user = EuphoUser.objects.filter(email=user.email).first()
            sociallogin.connect(request, user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Your Google account has been connected to your existing account.')
            raise ImmediateHttpResponse(redirect('userhome'))
        except EuphoUser.DoesNotExist:
            pass
