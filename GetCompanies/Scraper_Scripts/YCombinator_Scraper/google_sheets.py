import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsManager:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, self.scope)
        self.client = gspread.authorize(creds)
    
    def setup_sheet(self, spreadsheet_url):
        """Setup and return Google Sheet object"""
        spreadsheet_id = spreadsheet_url.split('/')[5]
        sheet = self.client.open_by_key(spreadsheet_id).sheet1
        return sheet
    
    def write_headers(self, sheet):
        """Write headers to the sheet"""
        headers = ["Company Name", "Founders' Name", "Founders' LinkedIn URL", "Company's LinkedIn URL", 
                  "Company's YC URL", "About Company", "Company's Website", "Team Size", "Founding Year"]
        sheet.clear()
        sheet.append_row(headers)
    
    def write_data_to_sheet(self, sheet, formatted_rows):
        """Write formatted data to Google Sheet with rate limiting"""
        print("Writing to Google Sheet...")
        for i, row in enumerate(formatted_rows, 1):
            try:
                sheet.append_row(row)
                if i % 10 == 0:
                    print(f"  Written {i}/{len(formatted_rows)} rows")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error writing row {i}: {e}")