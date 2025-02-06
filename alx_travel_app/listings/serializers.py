from rest_framework import serializers
from .models import Listing, Booking, Review, Payment


class ListingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Listing model with custom create and update methods.
    """

    bookings = serializers.HyperlinkedRelatedField(
        many=True, view_name='booking-detail', format='html', read_only=True)

    reviews = serializers.HyperlinkedRelatedField(
        many=True, view_name='review-detail', format='html', read_only=True)

    class Meta:
        model = Listing
        fields = ['listing_id', 'start_location', 'destination', 'total_price',
                  # Serializes specific fields in the Listing model
                  'created_at', 'updated_at', 'bookings', 'reviews']

    def create(self, validated_data):
        """
        Create and return a new Listing instance.

        Args:
            validated_data (dict): Validated data for creating a Listing.

        Returns:
            Listing: A newly created Listing instance.
        """
        return Listing.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing Listing instance.

        Args:
            instance (Listing): The Listing instance to update.
            validated_data (dict): Validated data for updating the Listing.

        Returns:
            Listing: The updated Listing instance.
        """
        instance.start_location = validated_data.get(
            'start_location', instance.start_location)
        instance.destination = validated_data.get(
            'destination', instance.destination)
        instance.total_price = validated_data.get(
            'total_price', instance.total_price)
        instance.save()
        return instance


class BookingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Booking model with custom create and update methods.
    """

    listing = serializers.HyperlinkedRelatedField(
        view_name='listing-detail', queryset=Listing.objects.all())

    class Meta:
        model = Booking
        fields = ['booking_id', 'listing', 'start_date', 'end_date', 'status',
                  'created_at', 'updated_at']  # Serializes specific fields in the Booking model

    def create(self, validated_data):
        """
        Create and return a new Booking instance.

        Args:
            validated_data (dict): Validated data for creating a Booking.

        Returns:
            Booking: A newly created Booking instance.
        """
        return Booking.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing Booking instance.

        Args:
            instance (Booking): The Booking instance to update.
            validated_data (dict): Validated data for updating the Booking.

        Returns:
            Booking: The updated Booking instance.
        """
        instance.listing = validated_data.get('listing', instance.listing)
        instance.start_date = validated_data.get(
            'start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Review model.
    Handles creation, updates, and validations.
    """

    # Nested representation of the listing, you can modify fields or use a ListingSerializer
    listing = serializers.HyperlinkedRelatedField(
        view_name='listing-detail', queryset=Listing.objects.all())

    class Meta:
        model = Review
        fields = ['review_id', 'listing', 'rating', 'comment',
                  'created_at']  # Include necessary fields
        # Fields that are automatically generated and should not be updated
        read_only_fields = ['review_id', 'created_at']

    def create(self, validated_data):
        """
        Create a new Review instance using the provided validated data.
        """
        review = Review.objects.create(**validated_data)
        return review

    def update(self, instance, validated_data):
        """
        Update an existing Review instance with the provided validated data.
        """
        instance.rating = validated_data.get('rating', instance.rating)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Payment model with custom create and update methods.
    """
    booking = serializers.HyperlinkedRelatedField(
        view_name='booking-detail', queryset=Booking.objects.all())

    class Meta:
        model = Payment
        fields = '__all__'  # Serializes all fields in the Payment model
        read_only_fields = ['created_at', 'payment_status']
