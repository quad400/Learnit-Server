import stripe
import json
from django.shortcuts import redirect
from django.conf import settings
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone
from course.models import Course
from .models import CartItem,Order
from .serializer import CartItemSerializer, OrderSerializer


class CartListAPIView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    pagination_class = None

    def get_queryset(self):
        query = CartItem.objects.filter(user=self.request.user)
        return query

    def get(self, request, *args, **kwargs):
        query = self.get_queryset()
        total_item = query.count()
        total_price = 0
        for q in query:
            total_price += q.course.price
        
        serializer = self.get_serializer(instance=query, many=True)
        data = {
            "total_item" : total_item,
            "total_price" : total_price,
            "items" : serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    

class OrderListView(generics.ListAPIView):
    queryset=Order.objects.all()
    serializer_class=OrderSerializer


class OrderDetailView(APIView):
    def get(self, request):
        order = get_object_or_404(Order, user=request.user, ordered=False)
        if not order:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            serializer = OrderSerializer(order)
            return Response(serializer.data)

    def put(self, request, order_id):
        order = Order.objects.filter(user=request.user, pk=order_id).first()

        if not order:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddToCartView(APIView):
    def post(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)

        order_item_qs = CartItem.objects.filter(
            course=course,
            user=request.user,
            ordered=False
        )

        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.save()
        else:
            order_item = CartItem.objects.create(
                course=course,
                user=request.user,
                ordered=False
            )

        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if not order.cart.filter(course__course_id=order_item.cart_id).exists():
                order.cart.add(order_item)
                return Response(status=status.HTTP_200_OK)

        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.cart.add(order_item)
            return Response(status=status.HTTP_200_OK)

    def delete(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)
        order = Order.objects.filter(user=request.user, ordered=False)

        if order.exists():
            order_item_qs = CartItem.objects.filter(
                course=course,
                user=request.user,
                ordered=False
            )[0]
            if not order[0].cart.filter(course__course_id=order_item_qs.cart_id).exists():
                order_item_qs.delete()
                # order[0].cart.remove(order_item_qs)
                # order[0].save()
                return Response("sucessfully deleted",status=status.HTTP_200_OK)
            else: 
                return Response("Course is not in cart",status=status.HTTP_400_BAD_REQUEST)



stripe.api_key = settings.STRIPE_SECRET_KEY
class StripeCheckoutView(APIView):
    def post(self, request, order_id):
        try:
            order=get_object_or_404(Order, order_id=order_id)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price_data': {
                            'currency':'usd',
                             'unit_amount':int(order.get_total()) * 100,
                             'product_data':{
                                 'name':order.order_id,
                             }
                        },
                        'quantity': 1,
                    },
                ],
                metadata={
                    "product_id": order.order_id
                },
                mode='payment',
                success_url=settings.SITE_URL + '?success=true',
                cancel_url=settings.SITE_URL + '?canceled=true',
            )
            order.payment_intent_id = checkout_session.id
            return redirect(checkout_session.url)
        except Exception as e:
            return Response({'msg':'something went wrong while creating stripe session','error':str(e)}, status=500)

def success(request):
   return 

def canceled(request):
   return 

@csrf_exempt
def stripe_webhook(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_KEY
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  # Handle the checkout.session.completed event
  if event['type'] == 'checkout.session.completed':
    session = event['data']['object']
    print(session)
    if session.payment_status == "paid":
      customer_email = session["customer_details"]["email"]
      order_id = session["metadata"]["order_id"]
      # Fulfill the purchase
      order = Order.objects.get(pk=order_id)
      order.is_completed=True
      order.ordered_date = timezone.now()
      order.save()

      send_mail(
         subject="Your ordered course",
         message=f"Thanks for your purchase. Here is the course you ordered {order.payment_intent_id}",
         recipient=[customer_email],
         from_email="adedijiabdulquadri@gmail.com"
      )
      fulfill_order(session)

  elif event['type'] == 'checkout.session.async_payment_succeeded':
    session = event['data']['object']

    # Fulfill the purchase
    fulfill_order(session)

  elif event['type'] == 'checkout.session.async_payment_failed':
    session = event['data']['object']

    # Send an email to the customer asking them to retry their order
    email_customer_about_failed_payment(session)

  # Passed signature verification
  return HttpResponse(status=200)

def fulfill_order(session):
  # TODO: fill me in
  print("Fulfilling order")

def create_order(session):
  # TODO: fill me in
  print("Creating order")

def email_customer_about_failed_payment(session):
  # TODO: fill me in
  print("Emailing customer")