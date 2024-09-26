
"""APIs for user authentication"""
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout
from rest_framework import response, status, viewsets, permissions
from . import static_values
from .models import User
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
# from .serializers import authentication
from rest_framework_simplejwt.tokens import (
    RefreshToken,
    AccessToken
)
import random

class SendOTPViewSet(viewsets.ViewSet):
    """Send OTP to the user"""
    http_method_names = ['post']
    permission_classes = [permissions.AllowAny]

    def generate_otp(self) -> str:
        """Generate a 4 character numeric OTP"""
        return str(random.randint(1000, 9999))

    def post(self, request):
        """Send OTP to the user"""
        mobile = request.data.get('mobile')
        type = request.data.get('type')
       # if type:
       #     type = "Student" if str(type) == '2' else "Teacher"
       #     user = User.objects.filter(mobile=mobile, is_active=True, profile_type=type).first()
       # else:
        user = User.objects.filter(mobile=mobile, is_active=True).first()
        if not user:
            return response.Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        otp = self.generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        if settings.DEBUG:
            sms_sent = True
        else:
           pass
            # send OTP to the user
            # message = f'OTP for login verification {otp}. BGIVNS'  # Login verification message
            # sms_sent = send_sms(static_values.SMS_SENDER_ID, mobile, message)

        if not sms_sent:
            return response.Response(
                {'message': 'Failed to send OTP'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return response.Response(
            {
                'message': 'OTP sent successfully',
                'otp': otp,
                'otp_created_at': user.otp_created_at
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPViewSet(viewsets.ViewSet):
    """Verify OTP for the user"""
    http_method_names = ['post']
    permission_classes = [permissions.AllowAny]

    @csrf_exempt
    def post(self, request):
        """Verify OTP for the user"""
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')
        user = User.objects.filter(mobile=mobile, is_active=True).first() # otp=otp,
        if not user \
            or not user.otp \
            or not user.otp_created_at \
            or not user.otp_created_at \
                + timedelta(minutes=static_values.OTP_VALIDITY_IN_MINUTES) > timezone.now():

            return response.Response(
                {'message': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.otp = None
        user.otp_created_at = None
        user.save()

        # return JWT access token and refresh token
        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        login(request, user)
        return response.Response(
            {
                'message': 'OTP verified successfully',
                'refresh': str(refresh),
                'access': str(access),
                'user_id': user.id
            },
            status=status.HTTP_200_OK
        )


# logout_view Swagger Documentation
def logout_view(request):
    """Logout the user"""
    logout(request)
    return HttpResponseRedirect(reverse('frontend:home:login'))

