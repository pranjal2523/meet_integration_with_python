from __future__ import print_function
from datetime import datetime, timedelta
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2


API_KEY = 'AIzaSyBwqcGu9xWarpAQED2lmouwrD73uDORfjs'

# def create_space():
#         try:
#             # Use the API key to create a client
#             service = build('meet_v2', 'v1', developerKey=API_KEY)
            
#             # Make the API call
#             meet_request = {}
#             response = service.spaces().create(body=meet_request).execute()
#             print(response.get('meetingUri'))
        
#         except Exception as e:
#             print(str(e))

# create_space()
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_google_meet_event(summary, description, start_time, end_time, attendees):
    """Create a Google Calendar event with a Google Meet link."""
    # Check for existing credentials
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Create the service
    service = build('calendar', 'v3', credentials=creds)

    # Event data
    event_data = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Los_Angeles',  # Adjust as needed
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/Los_Angeles',  # Adjust as needed
        },
        'attendees': [{'email': email} for email in attendees],  # Add attendees here
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
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    # Create the event
    event = service.events().insert(calendarId='primary', body=event_data, conferenceDataVersion=1).execute()
    print(f'Event created: {event.get("htmlLink")}')
    print(f'Google Meet link: {event.get("conferenceData").get("entryPoints")[0].get("uri")}')


if __name__ == '__main__':
    # Specify event details
    summary = "My Meeting"
    description = "Discuss project updates"

    # Set the start and end time for the event
    start_time = datetime(2024, 9, 26, 20, 30, 0)  # Year, Month, Day, Hour, Minute, Second
    end_time = start_time + timedelta(minutes=30)  # 1 hour duration
    attendees = ['pranjalbjp2523@gmail.com']
    # attendees = ['rishabh@sortstring.com', 'prabhat@sortstring.com', 'parijat.shrivastava@sortstring.com']
    print(start_time.isoformat())
    create_google_meet_event(summary, description, start_time, end_time, attendees)



# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/meetings.space.created']


# def main():
#     """Shows basic usage of the Google Meet API.
#     """
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     try:
#         client = meet_v2.SpacesServiceClient(credentials=creds)
#         request = meet_v2.CreateSpaceRequest()
#         response = client.create_space(request=request)
#         print(f'Space created: {response.meeting_uri}')
#     except Exception as error:
#         # TODO(developer) - Handle errors from Meet API.
#         print(f'An error occurred: {error}')


# if __name__ == '__main__':
#     main()