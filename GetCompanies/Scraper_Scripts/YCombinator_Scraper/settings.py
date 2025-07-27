import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.spreadsheet_url = os.getenv("SPREADSHEET_URL")
        self.y_combinator_url = os.getenv("Y_COMBINATOR_URL", "https://www.ycombinator.com")
        self.y_combinator_batch = os.getenv("Y_COMBINATOR_BATCH")
        self.credentials_path = os.getenv("CREDENTIALS_PATH", "credentials.json")
        
        # Validate required environment variables
        if not self.spreadsheet_url:
            raise ValueError("SPREADSHEET_URL not found in .env file")
        if not self.y_combinator_batch:
            raise ValueError("Y_COMBINATOR_BATCH not found in .env file")