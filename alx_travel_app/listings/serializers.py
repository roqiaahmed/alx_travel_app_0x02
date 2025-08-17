from rest_framework import serializers
from .models import User, Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "role",
        ]
        read_only_fields = ["id", "created_at"]


class ListingSerializer(serializers.ModelSerializer):
    # reviews = serializers.PrimaryKeyRelatedField(queryset=Review.objects.all())
    host = UserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id",
            "host",
            "name",
            "description",
            "price_per_night",
            "location",
            # "reviews",
        ]


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = Booking
        fields = [
            "id",
            "listing",
            "user",
            "start_date",
            "end_date",
            "total_price",
            "status",
        ]
        read_only_fields = ["id", "user", "created_at", "status"]

    def validate(self, data):
        if data["end_date"] <= data["start_date"]:
            raise serializers.ValidationError("End date must be after start date.")
        return data
