from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil.parser import parse
import dateparser
import spacy

nlp = spacy.load('en_core_web_md')

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def main():
    """Adds an event on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    print('Starting')
    des, date_time = summary()

    event = {
        'summary': des,
        'start': {
            'dateTime': date_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': date_time,
            'timeZone': 'Asia/Kolkata',
        },

        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    # add event
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


def summary():
    """Extract information from text input"""
    text = input("Enter text\n")
    doc = nlp(text)
    date_list = []
    lis = []
    for ent in doc.ents:
        if ent.label_ in ['DATE', 'TIME']:
            if "oclock" in ent.text:
                ent_pm = ent.text.replace("oclock", "pm")
                date_list.append(ent_pm)
            else:
                date_list.append(ent.text)
    s = ' '.join(date_list)
    date_time = dateparser.parse(s, settings={'PREFER_DATES_FROM': 'future'}).isoformat()
    for time in filter(lambda w: w.ent_type_ in ("TIME", "DATE"), doc):
        if time.dep_ == 'pobj':
            date_list.append(str(time.head))
    for i in doc:
        # get words other than date and time
        if i.text not in str(date_list):
            lis.append(i.text)
    des = ' '.join(lis)
    des = des.replace("oclock", "")
    return des, date_time


if __name__ == '__main__':
    main()
