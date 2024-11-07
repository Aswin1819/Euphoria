from django.contrib import admin
from .models import EuphoUser,Products,Variant,PaymentMethod


admin.site.register(EuphoUser)
admin.site.register(Products)
admin.site.register(Variant)
admin.site.register(PaymentMethod)

# Register your models here.
