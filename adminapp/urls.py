from django.urls import path
from .import views


urlpatterns = [
    path('adminLogin/',views.adminLogin, name = 'adminLogin'),
    path('admincustomers/',views.adminCustomers,name='admincustomers'),
    path('adminproducts/',views.adminProducts,name = 'adminproducts'),
    path('adminorders/',views.adminOrders,name = 'adminorders'),
    path('admincoupons/',views.adminCoupons,name ='admincoupons'),
   
]