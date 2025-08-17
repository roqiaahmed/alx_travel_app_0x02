from django_seed import Seed
from listings.models import User, Booking, Review, Listing
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, date


User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with test data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")
        self.seed_users()
        self.seed_listings()
        self.seed_bookings()
        self.seed_reviews()
        self.stdout.write("Seeding complete.")

    def seed_users(self):
        self.host_user = User.objects.create_user(
            username="host_user",
            email="host@example.com",
            password="password123",
            first_name="Host",
            last_name="User",
            phone_number=1234567890,
            role="host",
        )

        self.guest_user = User.objects.create_user(
            username="guest_user",
            email="guest@example.com",
            password="password123",
            first_name="Guest",
            last_name="User",
            phone_number=9876543210,
            role="guest",
        )

    def seed_listings(self):
        self.listing = Listing.objects.create(
            host=self.host_user,
            name="Cozy Apartment in NYC",
            description="A beautiful and cozy apartment in the heart of NYC.",
            price_per_night=150.00,
            location="New York, NY",
        )

    def seed_bookings(self):
        today = date.today()
        self.booking = Booking.objects.create(
            user=self.guest_user,
            listing=self.listing,
            start_date=today,
            end_date=today + timedelta(days=3),
            total_price=450.00,
            status="confirmed",
        )

    def seed_reviews(self):
        Review.objects.create(
            user_id=self.guest_user,
            list_id=self.listing,
            rating=5,
            comment="Amazing place! Very clean and well-located.",
        )
