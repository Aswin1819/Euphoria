from django.contrib import admin
from .models import *

admin.site.register(EuphoUser)
admin.site.register(Products)
admin.site.register(Images)
admin.site.register(Variant)
admin.site.register(PaymentMethod)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(Coupon)
admin.site.register(UserCoupon)
# Register your models here.
