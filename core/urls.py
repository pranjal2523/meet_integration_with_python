from rest_framework_simplejwt.views import TokenVerifyView, TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import SendOTPViewSet, VerifyOTPViewSet, logout_view

app_name = 'users'

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # authentication APIs
    path('api/send-otp/', SendOTPViewSet.as_view({'post': 'post'}), name='send_otp'),
    path(
        'api/verify-otp/',
        VerifyOTPViewSet.as_view({'post': 'post'}),
        name='verify_otp'
    ),
    path('api/logout/', logout_view, name='logout'),
]