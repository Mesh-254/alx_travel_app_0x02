import uuid
import requests
from django.conf import settings
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .tasks import payment_confirmation_email





class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        """
        Save the booking instance, initiate payment, and send the payment link to the user.
        """
        instance = serializer.save()

        # Trigger the payment process if the booking status is confirmed or pending
        if instance.status == 'confirmed' or instance.status == 'pending':
            # Initialize payment
            payment_data = {
                'booking_id': instance.booking_id,
                'amount': "150",
                'email': 'meshack1995@gmail.com',  # Hardcoded email
                'first_name': 'Meshack',  # Hardcoded first name
                'last_name': 'Mutune',  # Hardcoded last name
                'phone_number': '0700123456'  # Hardcoded phone number
            }

            print("payment_data: ", payment_data)

    
           # Send request to PaymentInitializeView class 
            payment_url = "http://127.0.0.1:8000/pay/"  # Adjust URL based on your API endpoint
            response = requests.post(payment_url, json=payment_data)
            data = response.json()
            print(f' Transaction response: {data}')

            if response.status_code == 201:
                checkout_url = response.json().get('checkout_url')
                
                return HttpResponse(f"Payment link: {checkout_url}", content_type="text/plain", status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Payment initialization failed'}, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class PaymentViewSet(viewsets.ModelViewSet):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        """
        Save the payment instance and trigger the email task.
        """
        print('creating object')
        instance = serializer.save()

        if instance.payment_status == 'success':
            # Trigger the email task
            payment_confirmation_email.delay(instance.tx_ref) # Send email asynchronously

    def perform_update(self, serializer):
        """
        Update the payment instance and trigger the email task.
        """
        instance = serializer.save()
        if instance.status == 'confirmed':
            payment_confirmation_email.delay(instance.tx_ref)
        


class PaymentInitializeView(APIView):
    """
        Initialize a payment by sending a request
          to Chapa API and returning a payment link.
    """

    def post(self, request):
        try:
            booking_id = request.data.get('booking_id')
            booking = Booking.objects.get(booking_id=booking_id)

            # Generate a unique transaction reference
            tx_ref = uuid.uuid4().hex

            # Chapa API URL
            url = "https://api.chapa.co/v1/transaction/initialize"

            # Payment Data
            payload = {
                # Ensure it's a string
                "amount": str(request.data.get("amount")),
                "currency": "USD",
                "email": request.data.get('email'),
                "first_name": request.data.get('first_name'),
                "last_name": request.data.get('last_name'),
                "phone_number": request.data.get('phone_number'),
                "tx_ref": tx_ref,
                "callback_url": settings.CHAPA_CALLBACK_URL,  # Redirects user after payment
                # "return_url": settings.CHAPA_SUCCESS_URL,  # User sees this after payment
                "customization": {
                    "title": "Booking Payment",
                    "description": "Payment for booking services"
                }
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}'
            }

            # Send the request with json=payload
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            # Check if payment initialization was successful
            if data.get('status') == 'success':
                checkout_url = data.get('data', {}).get('checkout_url')
                if not checkout_url:
                    return Response({'error': 'Payment initialization failed'}, status=status.HTTP_400_BAD_REQUEST)

                # Save the payment details
                payment = Payment.objects.create(
                    amount=payload['amount'],
                    currency=payload['currency'],
                    email=payload['email'],
                    phone_number=payload['phone_number'],
                    tx_ref=payload['tx_ref'],
                    booking=booking
                )
                payment.save()

                # Return the checkout URL to redirect the user
                return Response({'checkout_url': checkout_url}, status=status.HTTP_201_CREATED)
            else:

                return Response({'error': 'Payment initialization failed', 'details': data}, status=status.HTTP_400_BAD_REQUEST)

        except Booking.DoesNotExist:

            return Response({'Error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:

            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerificationView(APIView):
    """
    Webhook endpoint for verifying Chapa payments.
    """

    def get(self, request):
        try:
            tx_ref = request.GET.get('trx_ref')

            payment = Payment.objects.get(tx_ref=tx_ref)

            # Verify the payment using Chapa API
            verification_data = self.verify_payment(tx_ref)

            if verification_data.get('status') == 'success':

                
                payment.payment_status = 'success'
                payment.save()

                return Response({"message": f"Payment successful"}, status=status.HTTP_200_OK)
               

            elif verification_data.get('status') == 'failed':
             
                payment.payment_status = 'declined'

                payment.save()
                return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Payment.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def verify_payment(self, tx_ref):
        """
        Verify a payment by sending a request to Chapa API.
        """
        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}'
        }
        response = requests.get(url, headers=headers)
        verification_data = response.json()
        print(f'verification_data: {verification_data}')
        return verification_data
