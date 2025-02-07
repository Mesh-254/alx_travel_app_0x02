from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Payment





@shared_task
def payment_confirmation_email(tx_ref):
    """
    Task to send an e-mail notification when a payment has been confirmed for a booking.
    """
    try:
        # Get the payment object using the transaction reference (tx_ref)
        payment = Payment.objects.get(tx_ref=tx_ref)
        print(payment)
        # Fetch the associated booking
        booking = payment.booking
        print(f'this is the booking Id{booking.booking_id}')
        
        # Prepare the email subject and message
        subject = f'Payment Confirmation - {booking.booking_id}'
        message = (
            f'Dear Customer,\n\n'
            f'Your payment has been successfully processed!\n'
            f'Booking ID: {booking.booking_id}\n'
            f'Listing: {booking.listing.start_location} to {booking.listing.destination}\n'
            f'Start Date: {booking.start_date}\n'
            f'End Date: {booking.end_date}\n\n'
            f'Thank you for choosing us!\n'
            f'If you have any questions, please feel free to reach out.'
        )


        print(f'Message to be sent: {message}')
        
        # Send the confirmation email
        mail_sent = send_mail(
            subject, 
            message, 
            settings.EMAIL_HOST_USER,  # Sender email from settings
            [payment.email],  # Send to the customer's email (from payment data)
            fail_silently=False
        )
        
        return mail_sent
    
    except Payment.DoesNotExist:
        return f"Payment with transaction reference {tx_ref} not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"