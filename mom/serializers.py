# meet/serializers.py
from rest_framework import serializers

class GoogleMeetEventSerializer(serializers.Serializer):
    summary = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    attendees = serializers.ListField(
        child=serializers.EmailField()
    )
