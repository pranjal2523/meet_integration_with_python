# meet/urls.py
from django.urls import path
from .views import CreateGoogleMeetEvent, GoogleOAuthCallback

urlpatterns = [
    path('create-meet-event/', CreateGoogleMeetEvent.as_view(), name='create_meet_event'),
    path('oauth2callback/', GoogleOAuthCallback.as_view(), name='oauth_callback'),
]