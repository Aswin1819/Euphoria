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
    path('addVariant/',views.addVariant,name='addVariant'),
    
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
    
    path('adminOrders/',views.adminOrders,name = 'adminOrders'),
    path('UpdateOrderStatus/<int:order_item_id>/',views.UpdateOrderStatus,name='UpdateOrderStatus'),
    path('orderSearch/',views.orderSearch,name='orderSearch'),
    path('manage_requests/',views.manage_requests,name='manage_requests'),
    path('approve_request/<int:request_id>/',views.approve_request,name='approve_request'),
    path('reject_request/<int:request_id>/',views.reject_request,name='reject_request'),
    
    path('admincoupons/',views.adminCoupons,name ='adminCoupons'),
    path('addCoupon/',views.addCoupon,name='addCoupon'),
    path('editCoupon/<int:coupon_id>/',views.editCoupon,name='editCoupon'),
    path('deleteCoupon/<int:coupon_id>/',views.deleteCoupon,name='deleteCoupon'),
    path('searchCoupon/',views.searchCoupon,name='searchCoupon'),
    
    path('adminOffers/',views.adminOffers,name='adminOffers'),
    path('adminAddOffers/',views.adminAddOffers,name='adminAddOffers'),
    path('adminEditOffers/<int:offer_id>/',views.adminEditOffers,name='adminEditOffers'),
    path('adminDeleteOffer/<int:offer_id>/',views.adminDeleteOffer,name='adminDeleteOffer'),
    path('adminSearchOffers/',views.adminSearchOffers,name='adminSearchOffers'),
    
    path('adminDashboard/',views.adminDashboard,name='adminDashboard'),
    path('export-to-excel/', views.export_to_excel, name='export_to_excel'),
    path('export-to-pdf/', views.export_to_pdf, name='export_to_pdf'),
    
    path('adminLogout',views.adminLogout,name='adminLogout'),
   
]