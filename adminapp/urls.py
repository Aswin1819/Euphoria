from django.urls import path
from .import views


urlpatterns = [
    path('adminLogin/',views.adminLogin, name = 'adminLogin'),
    path('checkAdmin',views.checkAdmin,name='checkAdmin'),
    path('admincustomers/',views.adminCustomers,name='adminCustomers'),
    path('blockUser/<int:id>',views.blockUser,name='blockUser'),
    path('customerSearch/',views.customerSearch,name='customerSearch'),
    
    path('adminproducts/',views.adminProducts,name = 'adminProducts'),
    path('addProducts/',views.addProducts,name='addProducts'),
    path('editProducts/<int:id>/',views.editProducts,name='editProducts'),
    path('productSearch/',views.productSearch,name='productSearch'),
    path('removeProducts/<int:id>',views.removeProducts,name='removeProducts'),
    
    path('admincategory/',views.adminCategory,name= 'adminCategory'),
    path('addCategory/',views.addCategory,name='addCategory'),
    path('editCategory/<int:id>',views.editCategory,name='editCategory'),
    path('removeCategory/<int:id>',views.removeCategory,name='removeCategory'),
    path('categorySearch/',views.categorySearch,name='categorySearch'),
    
    path('adminBrands/',views.adminBrands,name='adminBrands'),
    path('addBrands/',views.addBrands,name='addBrands'),
    path('removeBrands/<int:id>',views.removeBrands,name='removeBrands'),
    path('editBrands/<int:id>',views.editBrands,name='editBrands'),
    path('brandSearch/',views.brandSearch,name='brandSearch'),
    
    path('adminorders/',views.adminOrders,name = 'adminOrders'),
    path('admincoupons/',views.adminCoupons,name ='adminCoupons'),
    path('adminLogout',views.adminLogout,name='adminLogout'),
   
]