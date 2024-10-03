from django.urls import path
from .import views

urlpatterns = [
    path('userlogin/',views.userLogin,name = 'userlogin'),
    path('usersignup/',views.userSignup,name = 'usersignup'),
    path('forg_pass_email',views.forgPassEmailVerification,name = 'forg_pass_email'),
    path('otp_validation',views.otpValidation,name = 'otp_validation'),
    path('change_password',views.changePassword, name = 'change_password'),
]