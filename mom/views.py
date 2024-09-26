# meet/views.py
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path
from .serializers import GoogleMeetEventSerializer
import webbrowser
from rest_framework.permissions import AllowAny


SCOPES = ['https://www.googleapis.com/auth/calendar']

class CreateGoogleMeetEvent(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        credential_path = os.path.join(settings.BASE_DIR, 'credentials.json')
        
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        # Initialize the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credential_path,
            SCOPES,
            redirect_uri=request.build_absolute_uri('/api/oauth2callback/')
        )

        # Generate the authorization URL
        auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

        # Store the flow state in the session AFTER calling authorization_url()
        request.session['oauth_state'] = state
        request.session['user_id'] = request.user.id

        # Redirect the user to the auth_url instead of opening the browser manually
        return redirect(auth_url)

    def post(self, request):
        serializer = GoogleMeetEventSerializer(data=request.data)
        if serializer.is_valid():
            summary = serializer.validated_data['summary']
            description = serializer.validated_data['description']
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']
            attendees = serializer.validated_data['attendees']

            # Check for existing credentials
            creds = None
            # Get the path for token.json
            token_path = os.path.join(settings.BASE_DIR, 'meet_token', f'{request.user_id}_token.json')
            credential_path = os.path.join(settings.BASE_DIR, 'credentials.json')
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credential_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            # Create the service
            service = build('calendar', 'v3', credentials=creds)
            reminders = serializer.validated_data.get(
                'reminders', [{
                    'method': 'email',
                    'minutes': 24 * 60
                },
                {'method': 'popup', 'minutes': 10}
                ])

            # Event data
            event_data = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Los_Angeles',
                },
                'attendees': [{'email': email} for email in attendees],
                'conferenceData': {
                    'createRequest': {
                        'requestId': 'some-random-string',
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        },
                    },
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': reminders,
                },
            }

            location = serializer.validated_data.get('location', None)
            if location:
                event_data['location'] = location
            recurrence = serializer.validated_data.get('recurrence', [])
            
            if recurrence:
                event_data['recurrence'] = recurrence
            # 'recurrence': ['RRULE:FREQ=WEEKLY;COUNT=10'],  # Weekly, 10 occurrences

            # Create the event
            try:
                event = service.events().insert(calendarId='primary', body=event_data, conferenceDataVersion=1).execute()
                return Response({
                    'event_link': event.get("htmlLink"),
                    'meet_link': event.get("conferenceData").get("entryPoints")[0].get("uri")
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    

class GoogleOAuthCallback(APIView):

    def get(self, request):
        credential_path = os.path.join(settings.BASE_DIR, 'credentials.json')
        user_id = request.session.get('user_id')
        token_path = os.path.join(settings.BASE_DIR, 'meet_token', f'{user_id}_token.json')
        # Create token directory if it doesn't exist
        token_dir = os.path.join(settings.BASE_DIR, 'meet_token')
        if not os.path.exists(token_dir):
            os.makedirs(token_dir)

        # Allow insecure HTTP transport for local development
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        # Reconstruct the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credential_path,
            SCOPES,
            redirect_uri=request.build_absolute_uri('/api/oauth2callback/')
        )
        
        # Set the state from the session
        flow.state = request.session.get('oauth_state')
        if not flow.state:
            return Response({'error': 'OAuth state not found in session.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Capture the authorization response URL
        authorization_response = request.build_absolute_uri()

        # Fetch the token using the authorization response
        flow.fetch_token(authorization_response=authorization_response)

        # Get the credentials and save them to token.json
        creds = flow.credentials
        # token_path = os.path.join(settings.BASE_DIR, 'token.json')
       
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

        return Response({'message': 'Authentication successful, token saved.'}, status=status.HTTP_200_OK)