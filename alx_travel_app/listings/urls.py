from django.urls import path, include
from rest_framework import routers
from .views import (
    ListingViewSet,
    BookingViewSet,
    InitiatePaymentView,
    VerifyPaymentView,
)


router = routers.DefaultRouter()
router.register(r"Listing", ListingViewSet, basename="listing")
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/initiate-payment/", InitiatePaymentView.as_view(), name="initiate-payment"
    ),
    path("api/verify-payment/", VerifyPaymentView.as_view(), name="verify-payment"),
]
