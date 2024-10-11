from django.urls import path
from .import views


urlpatterns = [
    path('adminLogin/',views.adminLogin, name = 'adminLogin'),
    path('checkAdmin',views.checkAdmin,name='checkAdmin'),
    path('admincustomers/',views.adminCustomers,name='adminCustomers'),
    path('blockUser/<int:id>',views.blockUser,name='blockUser'),
    path('customerSearch/',views.customerSearch,name='customerSearch'),
    path('adminproducts/',views.adminProducts,name = 'adminProducts'),
    path('adminorders/',views.adminOrders,name = 'adminOrders'),
    path('admincoupons/',views.adminCoupons,name ='adminCoupons'),
    path('adminLogout',views.adminLogout,name='adminLogout'),
   
]