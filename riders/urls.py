# riders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RiderLocationViewSet,
    PublicRiderLocationsView,
    RiderProfileViewSet,
    RiderEarningsView,
    RiderB2CCallbackView,
)

router = DefaultRouter()
# authenticated CRUD for locations (used by rider device / admin)
router.register(r'locations', RiderLocationViewSet, basename='rider-location')
# profiles (public read, admin write)
router.register(r'profiles', RiderProfileViewSet, basename='rider-profile')

urlpatterns = [
    path("me/earnings/", RiderEarningsView.as_view(), name="rider-earnings"),
    path("mpesa/b2c/<str:callback_type>/", RiderB2CCallbackView.as_view(), name="rider-b2c-callback"),
    # public latest locations: GET /riders/
    path("", PublicRiderLocationsView.as_view(), name="rider-latest"),
    # include viewset routes at /riders/
    path("", include(router.urls)),
]
