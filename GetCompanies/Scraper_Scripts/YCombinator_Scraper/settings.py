import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.y_combinator_url = os.getenv("Y_COMBINATOR_URL", "https://www.ycombinator.com")
        self.y_combinator_batch = os.getenv("Y_COMBINATOR_BATCH")
        
        # Validate required environment variables
        if not self.y_combinator_batch:
            raise ValueError("Y_COMBINATOR_BATCH not found in .env file")