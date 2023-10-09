# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from django.db import transaction

# from .models import Order, CartItem

# @receiver(post_save, sender=Order)
# def clear_cart(sender, instance, created, **kwargs):
#     order = Order.objects.get(user=instance.user, is_completed=True)
#         with transaction.atomic():
#             CartItem.objects.filter(user=instance.user).delete()