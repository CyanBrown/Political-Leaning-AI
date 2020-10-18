import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import smtplib
from src.use.useKNN import guess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = 'spreadsheet id'  # replace with your own id
SAMPLE_RANGE_NAME = 'Form Responses 1!B:V'  # Sheet Name!column:column

# gets data from json that holds how many emails already sent
with open('counter.json', 'r') as f:
    counter = json.load(f)

# setting up smtp server
serversmtp = smtplib.SMTP("smtp.gmail.com", 587)
serversmtp.ehlo()
serversmtp.starttls()
serversmtp.ehlo()
serversmtp.login('your email', 'your password')


def email(answer, email):
    """

    :param answer: str answer from ai about party
    :param email: email that someone enters in the form to email answer to
    :return: none, emails person answer
    """

    message_word = "Hello! This is an automated response from the Political Survey. When you filled out the survey our AI " \
                   "was able to calculate that your political party is: " + answer + ". Thank you for participating in our survey."
    message = MIMEMultipart("alternative")
    message["Subject"] = "Political Survey Results"

    mainMessage = MIMEText(message_word, 'plain')
    message.attach(mainMessage)

    serversmtp.sendmail("you email", email, message.as_string())


def main():
    # this is all just setting up connection to google sheets I just got this from google's tutorial
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
                'creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()

    # gets values returned from sheets
    values = result.get('values', [])
    # removes title row of data
    values = values[1:]

    # only grabs the data we haven't already sent out
    values = values[counter['count']:]

    # saves new count to json
    with open('counter.json', 'w') as f:
        counter['count'] += len(values)
        json.dump(counter, f)

    if values:
        for idx, row in enumerate(values):
            # gets and removes email
            email_to = row[0]
            row = row[1:]

            # checks and removes bad data
            if "" in row or "Democrat" in row or 'Republican' in row:
                values.remove(row)
            else:
                # turns row to int
                row = [int(i) for i in row]
                values[idx] = row

                # gets prediction from ai
                prediction = guess(row)
                # emails prediction
                email(prediction, email_to)


if __name__ == '__main__':
    main()
