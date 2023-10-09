from rest_framework import serializers
from .models import Order, CartItem
from course.serializer import CourseSerializer
from course.models import Course


class CartCourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = (
            "course_id",
            "title",
            "price",
            "thumbnail",
        )

class CartItemSerializer(serializers.ModelSerializer):
    
    course = CartCourseSerializer()
    class Meta:
        model = CartItem
        fields = (
        "cart_id",
        "user",
        "course",
        )

class OrderSerializer(serializers.ModelSerializer):
    cart = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "order_id",
            "user",
            "payment_intent_id",
            "ordered_date",
            "ordered",
            "is_completed",
            "cart",
        )


