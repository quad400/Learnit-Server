from django.contrib import admin

# Register your models here.
from .models import Order, CartItem

admin.site.register(Order)
admin.site.register(CartItem)