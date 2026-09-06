import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SPREADSHEET_ID = "1v5icUgw1T50WSBXToA07_-coJMDmdNAFO-m3s73aUKQ"
WORKSHEET = "Sheet1"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

CLIENT_SECRET_FILE = os.path.join(
    "credentials",
    "client_secret.json"
)

TOKEN_FILE = os.path.join(
    "credentials",
    "token.json"
)


def get_credentials():
    credentials = None

    # Reuse previously authorized credentials
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Refresh expired credentials
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    # First-time login
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES
        )

        credentials = flow.run_local_server(
            port=0
        )

        with open(TOKEN_FILE, "w") as token:
            token.write(credentials.to_json())

    return credentials


print("Authenticating with Google...")

credentials = get_credentials()

print("Authentication successful!")

service = build(
    "sheets",
    "v4",
    credentials=credentials
)

print("Reading Google Sheet...")

result = (
    service.spreadsheets()
    .values()
    .get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{WORKSHEET}!A:Z"
    )
    .execute()
)

values = result.get("values", [])

print(f"Rows found: {len(values)}")
print()

for row in values[:10]:
    print(row)