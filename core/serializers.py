"""Serializers for the core module"""
from rest_framework import serializers
from datetime import timedelta
from django.utils.timezone import now


class SendOTPRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Serializer for send otp request"""
    mobile = serializers.CharField(required=True)


class SendOTPResponseSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Serializer for send otp response"""
    message = serializers.CharField()
    otp = serializers.CharField()
    otp_created_at = serializers.CharField()


class VerifyOTPRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Serializer for verify otp request"""
    mobile = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)


class VerifyOTPResponseSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Serializer for verify otp response"""
    message = serializers.CharField()
