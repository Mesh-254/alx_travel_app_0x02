from django.urls import path, include
from rest_framework.routers import DefaultRouter
from listings import views


# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename="listing")
router.register(r'bookings', views.BookingViewSet, basename="booking")
router.register(r'reviews', views.ReviewViewSet, basename="review")
router.register(r'payments', views.PaymentViewSet, basename="payment")

urlpatterns = [
    path('', include(router.urls)),
    path('pay/', views.PaymentInitializeView.as_view(), name='payment'),
    path('verify_payment/', views.PaymentVerificationView.as_view(), name='verify_payment')
]