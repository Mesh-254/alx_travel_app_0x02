import requests
import uuid
from django.conf import settings
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


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
                "customization": {
                    "title": "Booking Payment",
                    "description": f"Payment for booking"
                }
            }

            print(f"Received amount: {request.data.get('amount')}")

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}'
            }

            # Send the request with json=payload instead of data=payload
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            print(f'payment response : {response}')

            print(f'payment data : {data}')

            # Check if payment initialization was successful
            if data.get('status') == 'success':
                checkout_url = data.get('data', {}).get('checkout_url')
                if not checkout_url:
                    return Response({'error': 'Payment initialization failed'}, status=status.HTTP_400_BAD_REQUEST)

                # Save the payment details
                Payment.objects.create(
                    amount=payload['amount'],
                    currency=payload['currency'],
                    email=payload['email'],
                    phone_number=payload['phone_number'],
                    tx_ref=payload['tx_ref'],
                    booking=booking
                )
                # Return the checkout URL to redirect the user
                return Response({'checkout_url': checkout_url}, status=status.HTTP_201_CREATED)

            else:
                return Response({'error': 'Payment initialization failed', 'details': data}, status=status.HTTP_400_BAD_REQUEST)

        except Booking.DoesNotExist:
            return Response({'Error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
