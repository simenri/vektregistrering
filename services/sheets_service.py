import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google_sheet(sheet_name, worksheet_name="Sheet1"):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_sheet_creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    return sheet
