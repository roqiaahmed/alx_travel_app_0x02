from django.shortcuts import render
from .models import User, Booking, Review, Listing
from rest_framework import viewsets, permissions, serializers
from rest_framework.response import Response
from .serializers import ListingSerializer, BookingSerializer


class ListingViewSet(viewsets.ModelViewSet):

    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Set host to logged-in user
        user = self.request.user
        if user.role != "host":
            raise serializers.ValidationError(user.role + " can't create a list")
        serializer.save(host=user)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status="pending")

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
