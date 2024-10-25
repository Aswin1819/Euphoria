from django.urls import path
from .import views

urlpatterns = [
    path('userlogin/', views.userlogin, name = 'userlogin'),
    path('usersignup/',views.usersignup,name = 'usersignup'),
    path('forgPassEmailVerification/',views.forgPassEmailVerification,name = 'forgPassEmailVerification'),
    path('otpValidationForPass/',views.otpValidationForPass,name ='otpValidationForPass'),
    path('otpValidation/',views.otpValidation,name = 'otpValidation'),
    path('changePassword/',views.changePassword, name = 'changePassword'),
    path('resendotp/',views.resendotp,name = 'resendotp'),
    path('',views.userhome,name = 'userhome'),
    path('productView/<int:id>',views.productView,name='productView'),
    path('shopNow/',views.shopNow,name='shopNow'),
    path('userlogout/',views.userlogout,name = 'userlogout'),
    path('resendOtpForPass/',views.resendOtpForPass,name='resendOtpForPass'),
    path('userProfileInformation/',views.userProfileInformation,name='userProfileInformation'),
    path('userManageAddress/',views.userManageAddress,name='userManageAddress'),
    path('edit-address/<int:address_id>/', views.editAddress, name='editAddress'),
    path('delete-address/<int:address_id>/', views.deleteAddress, name='deleteAddress'),
]