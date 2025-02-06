# ALX Travel App Backend Documentation

## Overview

The goal of this project is to create and manage a backend system for an online travel platform. The system will involve managing listings, bookings, and reviews of travel destinations. The primary objective is to define the **database models**, create **serializers** for API data representation, and implement a **management command** to seed the database with sample data.

## Table of Contents

- [Objective](#objective)
- [Models](#models)
- [Serializers](#serializers)
- [Seeders](#seeders)
- [Running the Seed Command](#running-the-seed-command)
- [Testing the Seeder](#testing-the-seeder)

## Objective

1. **Create Models**:
    - **Listing**, **Booking**, and **Review** models will be created with appropriate fields, relationships, and constraints.

2. **Set Up Serializers**:
    - Serializers will be set up to handle data representation for **Listing** and **Booking** models.

3. **Implement Seeders**:
    - A management command will be written to populate the database with sample listing data.

4. **Test the Seeder**:
    - After implementing, you will run a custom command to populate the database and verify functionality.

## Models

Models are the core part of the app, and they are responsible for the structure of the database tables. Here’s how the models will be defined:

### Listing Model (`listings/models.py`)

The `Listing` model represents a property or a listing on the platform.

```python
from django.db import models
import uuid

class Listing(models.Model):
    listing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)  # UUID as primary key
    start_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.start_location} to {self.destination}"
```

### Booking Model (`listings/models.py`)

The `Booking` model represents a reservation made for a listing.

```python
from django.db import models
import uuid
from django.utils import timezone

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)  # UUID as primary key
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Booking ID {self.booking_id} for {self.listing}"
```

### Review Model (`listings/models.py`)

The `Review` model represents a review left by a user for a listing.

```python
from django.db import models
import uuid
from django.utils import timezone

class Review(models.Model):
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)  # UUID as primary key
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review for {self.listing} by Rating {self.rating}"
```

### Relationships

- **Listing** has a one-to-many relationship with **Booking** (A listing can have many bookings).
- **Listing** has a one-to-many relationship with **Review** (A listing can have many reviews).

## Serializers

Serializers are used to represent model data in a format that is easy to use for APIs. We'll define serializers for both `Listing` and `Booking` models.

### Listing Serializer (`listings/serializers.py`)

```python
from rest_framework import serializers
from .models import Listing

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['listing_id', 'start_location', 'destination', 'total_price', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Listing.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.start_location = validated_data.get('start_location', instance.start_location)
        instance.destination = validated_data.get('destination', instance.destination)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.save()
        return instance
```

### Booking Serializer (`listings/serializers.py`)

```python
from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    listing_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'listing_id', 'start_date', 'end_date', 'status', 'created_at']

    def create(self, validated_data):
        listing_id = validated_data.pop('listing_id')
        listing = Listing.objects.get(listing_id=listing_id)
        return Booking.objects.create(listing=listing, **validated_data)

    def update(self, instance, validated_data):
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
```

## Seeders

Seeders are used to populate the database with sample or default data. We will implement a **management command** to populate the database with sample listings.

### Seeder Command (`listings/management/commands/seed.py`)

```python
from django.core.management.base import BaseCommand
from listings.models import Listing, Booking, Review
from datetime import date
import uuid

class Command(BaseCommand):
    help = 'Seeds the database with sample data for listings, bookings, and reviews'

    def handle(self, *args, **kwargs):
        # Sample Listings
        listing_1 = Listing.objects.create(
            start_location="New York",
            destination="Paris",
            total_price=1500.00
        )

        listing_2 = Listing.objects.create(
            start_location="London",
            destination="Tokyo",
            total_price=2000.00
        )

        # Sample Bookings
        Booking.objects.create(
            listing=listing_1,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 22),
            status='confirmed'
        )

        Booking.objects.create(
            listing=listing_2,
            start_date=date(2024, 2, 10),
            end_date=date(2024, 2, 17),
            status='pending'
        )

        # Sample Reviews
        Review.objects.create(
            listing=listing_1,
            rating=5,
            comment="Fantastic experience!"
        )

        Review.objects.create(
            listing=listing_2,
            rating=4,
            comment="Great place, but a bit too expensive."
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with sample data!'))
```

## Running the Seed Command

After you have defined the models, serializers, and the seeder, run the custom management command to seed your database.

### Steps:
1. **Make Migrations**:
    First, run Django migrations to create the database tables:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

2. **Run Seeder Command**:
    Use the following command to populate the database with sample data:

    ```bash
    python manage.py seed
    ```

3. **Verify Data in the Database**:
    You can query your database directly (using a MySQL client) or use the Django admin to verify that the listings, bookings, and reviews have been successfully added.

## Testing the Seeder

Once the data is seeded into the database, use Django’s built-in admin or shell to query the `Listing`, `Booking`, and `Review` tables and ensure everything was inserted correctly:

```bash
python manage.py shell
```

Inside the shell, run:

```python
from listings.models import Listing, Booking, Review

# Check listings
listings = Listing.objects.all()
print(listings)

# Check bookings
bookings = Booking.objects.all()
print(bookings)

# Check reviews
reviews = Review.objects.all()
print(reviews)
```

### Expected Output:

After running the seed command, you should see:

- 2 listings inserted into the `Listing` table.
- Bookings for each listing in the `Booking` table.
- Reviews for each of those listings in the `Review` table.

---

### Conclusion

With this setup, you now have:

1. Defined database models for `Listing`, `Booking`, and `Review` with relationships and constraints.
2. Created serializers to handle data representation for these models.
3. Implemented a management command (`seed.py`) to populate the database with sample data.
4. Instructions for running and testing the database seeding. 

This system can be extended further by adding more models, serializers, and features such as user management and payment processing.