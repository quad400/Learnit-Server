from django.db import models
from django.contrib.auth import get_user_model
from course.models import Course
# from shortuuidfield.fields import ShortUUIDField
from shortuuidfield import ShortUUIDField
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class CartItem(models.Model):
    cart_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.course.title
    

class Order(models.Model):
    order_id = ShortUUIDField(editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ManyToManyField(CartItem)
    payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.fullname
        
    def get_total(self):
        total = 0
        for calc in self.cart.all():
            total+=calc.course.price
        return total


