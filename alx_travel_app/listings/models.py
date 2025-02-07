from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


def generate_uuid():
    """
    Generate a 36-character UUID string.
    """
    return str(uuid.uuid4())


class Listing(models.Model):
    """
    Model to represent a travel listing.
    """
    listing_id = models.CharField(
        primary_key=True,
        default=generate_uuid,
        max_length=36,
        editable=False,
        unique=True,
        db_index=True,
    )
    start_location = models.CharField(
        max_length=255, null=False, help_text="Starting location of the trip")
    destination = models.CharField(
        max_length=255, null=False, help_text="Destination location")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, help_text="Total cost of the trip")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.start_location} to {self.destination}"


class Booking(models.Model):
    """
    Model to represent a booking for a listing.
    """
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]

    booking_id = models.CharField(
        primary_key=True,
        default=generate_uuid,
        max_length=36,
        editable=False,
        unique=True,
        db_index=True,
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="The listing being booked"
    )
    start_date = models.DateField(
        null=False, help_text="Start date of the booking")
    end_date = models.DateField(
        null=False, help_text="End date of the booking")
    status = models.CharField(
        max_length=10,
        choices=BOOKING_STATUS_CHOICES,
        default='pending',
        help_text="Status of the booking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    

    def __str__(self):
        return f"Booking {self.booking_id} for {self.listing}"


class Review(models.Model):
    """
    Model to represent user reviews for listings.
    """
    review_id = models.CharField(
        primary_key=True,
        default=generate_uuid,
        max_length=36,
        editable=False,
        unique=True,
        db_index=True,
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="The listing being reviewed"
    )
    rating = models.IntegerField(
        null=False,
        help_text="Rating (1-5)",
        validators=[MinValueValidator(
            1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=False, help_text="Review comment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Review {self.review_id} - Rating {self.rating}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('declined', 'Declined'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="ETB")
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    tx_ref = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="payments")

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"
