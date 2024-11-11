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
    
    path('cartDetails/',views.cartDetails,name='cartDetails'),
    path('addToCart/',views.addToCart,name='addToCart'),
    path('removeCartItems/<int:product_id>/<int:variant_id>/',views.removeCartItems,name='removeCartItems'),
    path('update-quantity/', views.update_quantity, name='update_quantity'),
    path('set-primary-address/', views.set_primary_address, name='set_primary_address'),
    path('user_checkout/',views.user_checkout,name='user_checkout'),
    
    path('addToWishlist/',views.addToWishlist,name='addToWishlist'),
    path('userWishlist/',views.userWishlist,name='userWishlist'),
    path('removeFromWishlist/<int:item_id>/',views.removeFromWishlist,name='removeFromWishlist'),
    
    path('placeOrder/',views.placeOrder,name='placeOrder'),
    path('userYourOrder/',views.userYourOrder,name='userYourOrder'),
    path('cancel_order_item/<int:item_id>/', views.cancel_order_item, name='cancel_order_item'),
    path('return_order_item/<int:item_id>/', views.return_order_item, name='return_order_item'),

    path('categoryProducts/<int:category_id>/',views.categoryProducts,name='categoryProducts'),
]