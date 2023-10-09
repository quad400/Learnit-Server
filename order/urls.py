from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import (
                AddToCartView,
                CartListAPIView,
                OrderDetailView,
                OrderListView,
                StripeCheckoutView,
                stripe_webhook,
                success,
                canceled,
            )

urlpatterns = [
    path("cart/<slug:course_id>/", AddToCartView.as_view(), name='cart'),
    path("cart/", CartListAPIView.as_view(), name='cart_list'),
    path("", OrderDetailView.as_view(), name='order'),
    path("create-checkout-session/<slug:order_id>/", StripeCheckoutView.as_view()),
    path("webhooks/stripe/", stripe_webhook, name="webhook_stripe"),
    path("success/", success, name="success"),
    path("canceled/", canceled, name="canceled"),
]