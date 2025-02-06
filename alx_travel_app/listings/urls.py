from django.urls import path, include
from rest_framework.routers import DefaultRouter
from listings import views


# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename="listing")
router.register(r'bookings', views.BookingViewSet, basename="booking")
router.register(r'reviews', views.ReviewViewSet, basename="review")

urlpatterns = [
    path('', include(router.urls)),
    path('pay/', views.PaymentInitializeView.as_view(), name='payment'),
]