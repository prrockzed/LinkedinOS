import gspread
from oauth2client.service_account import ServiceAccountCredentials

def setup_gsheet(spreadsheet_url):
  """Setup Google Sheets connection and return sheet object"""
  spreadsheet_id = spreadsheet_url.split('/')[5]
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name('../credentials.json', scope)
  client = gspread.authorize(creds)
  sheet = client.open_by_key(spreadsheet_id).sheet1
  return sheet