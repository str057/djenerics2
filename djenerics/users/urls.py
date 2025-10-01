from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import PaymentViewSet, UserProfileView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),
] + router.urls