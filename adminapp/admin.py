from django.contrib import admin
from .models import EuphoUser,Products,Variant,PaymentMethod,Images,Cart,Order,OrderItem


admin.site.register(EuphoUser)
admin.site.register(Products)
admin.site.register(Images)
admin.site.register(Variant)
admin.site.register(PaymentMethod)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
# Register your models here.
