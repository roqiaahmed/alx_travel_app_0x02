from .models import Booking, Listing, Payment
from rest_framework import viewsets, permissions, serializers
from .serializers import ListingSerializer, BookingSerializer
import json
import uuid
import os
import requests
from django.http import JsonResponse


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


class InitiatePaymentView(viewsets.View):
    def post(self, request):
        data = json.loads(request.body)
        booking_reference = data.get("booking_reference")
        amount = data.get("amount")
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        tx_ref = str(uuid.uuid4())
        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": "http://127.0.0.1:8000/api/verify-payment/",
            "return_url": "http://127.0.0.1:8000/payment-success/",
            "customization[title]": "Travel Booking Payment",
            "customization[description]": f"Payment for booking {booking_reference}",
        }

        headers = {
            "Authorization": f"Bearer {os.environ.get('CHAPA_SECRET_KEY')}",
            "Content-Type": "application/json",
        }
        url = "https://api.chapa.co/v1/transaction/initialize"
        response = requests.post(url, json=payload, headers=headers)
        resp_data = response.json()
        if resp_data.get("status") == "success":
            Payment.objects.create(
                booking_reference=booking_reference,
                amount=amount,
                transaction_id=tx_ref,
                status="Pending",
            )
            return JsonResponse({"checkout_url": resp_data["data"]["checkout_url"]})
        return JsonResponse(resp_data, status=400)


class VerifyPaymentView(viewsets.View):
    def get(self, request):
        tx_ref = request.GET.get("tx_ref")
        if not tx_ref:
            return JsonResponse(
                {"error": "Transaction reference is required"}, status=400
            )

        headers = {
            "Authorization": f"Bearer {os.environ.get('CHAPA_SECRET_KEY')}",
        }
        url = "https://api.chapa.co/v1/transaction/verify"
        response = requests.get(f"{url}/{tx_ref}", headers=headers)
        resp_data = response.json()

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment record not found"}, status=404)

        if (
            resp_data.get("status") == "success"
            and resp_data["data"]["status"] == "success"
        ):
            payment.status = "Completed"
            payment.save()
            return JsonResponse(
                {"message": "Payment verified successfully", "status": payment.status}
            )

        payment.status = "Failed"
        payment.save()
        return JsonResponse(
            {"message": "Payment verification failed", "status": payment.status}
        )
