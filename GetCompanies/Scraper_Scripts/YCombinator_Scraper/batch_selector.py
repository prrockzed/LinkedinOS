import os
import sys
from urllib.parse import quote

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.get_user_choice import get_user_choice
from tools.info_logger import log_info, log_warning, log_error
from tools.blank_logger import log_blank_line

class YCBatchSelector:
    def __init__(self):
        self.base_url = "https://www.ycombinator.com/companies?batch="
        self.scraper_data_path = os.path.join(os.path.dirname(__file__), "../../Scraper_Data")
        
        # Define allowed seasons for each year
        self.year_seasons = {
            2025: ["Winter", "Summer", "Fall"],
            2024: ["Winter", "Spring", "Summer"],
            # For years 2023 down to 2006, only Summer and Winter
            **{year: ["Summer", "Winter"] for year in range(2023, 2005, -1)},
            # Special case for 2005 - only Summer
            2005: ["Summer"]
        }
    
    def get_valid_year(self):
        """Get a valid year from user input"""
        while True:
            log_blank_line()
            print(f"Enter the year for Y Combinator batch (2005-2025): ", end="", flush=True)
            year_input = input().strip()
            log_blank_line()
            
            try:
                year = int(year_input)
                if 2005 <= year <= 2025:
                    log_info(f"Selected year: {year}")
                    return year
                else:
                    log_warning("Please enter a year between 2005 and 2025")
            except ValueError:
                log_warning("Please enter a valid year (numbers only)")
    
    def get_valid_season(self, year):
        """Get a valid season for the given year"""
        allowed_seasons = self.year_seasons[year]
        
        log_blank_line()
        log_info(f"Available seasons for {year}:")
        for i, season in enumerate(allowed_seasons, 1):
            log_info(f"{i}. {season}")
        
        while True:
            log_blank_line()
            choice = get_user_choice(len(allowed_seasons))
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(allowed_seasons):
                    selected_season = allowed_seasons[choice_idx]
                    log_info(f"Selected season: {selected_season}")
                    return selected_season
                else:
                    log_warning(f"Please enter a number between 1 and {len(allowed_seasons)}")
            except ValueError:
                log_warning("Please enter a valid number")
    
    def build_batch_url(self, season, year):
        """Build the Y Combinator batch URL"""
        batch_param = f"{season} {year}"
        encoded_batch = quote(batch_param)
        url = f"{self.base_url}{encoded_batch}"
        return url
    
    def generate_filename(self, season, year):
        """Generate filename for the scraped data"""
        season_map = {
            'Summer': 'S',
            'Winter': 'W',
            'Fall': 'F',
            'Spring': 'X'
        }
        
        season_char = season_map.get(season, '?')
        year_short = str(year)[-2:]
        
        return f"YC_{season_char}{year_short}_scraped.json"
    
    def check_existing_file(self, filename):
        """Check if the file already exists"""
        file_path = os.path.join(self.scraper_data_path, filename)
        return os.path.exists(file_path), file_path
    
    def confirm_overwrite(self, filename):
        """Ask user if they want to overwrite existing file"""
        log_blank_line()
        log_warning(f"The file '{filename}' already exists!")
        log_info("This means the data for this batch has already been scraped.")
        log_blank_line()
        log_info("Do you want to scrape again and overwrite the existing data?")
        log_info("Caution: This will erase all your data")
        log_info("1. Yes, scrape again")
        log_info("2. No, go back to main menu")
        
        while True:
            log_blank_line()
            choice = get_user_choice(2)
            
            if choice == "1":
                log_info("Proceeding with scraping...")
                return True
            elif choice == "2":
                log_info("Returning to main menu...")
                return False
            else:
                log_warning("Please enter 1 or 2")
    
    def select_batch(self):
        """Main method to select Y Combinator batch"""
        log_info(1, "=== Y Combinator Batch Selection ===", 1)
        
        # Get year from user
        year = self.get_valid_year()
        
        # Get season from user
        season = self.get_valid_season(year)
        
        # Build URL and filename
        batch_url = self.build_batch_url(season, year)
        filename = self.generate_filename(season, year)
        
        log_blank_line()
        log_info(f"Batch Selection Summary:")
        log_info(f"Year: {year}")
        log_info(f"Season: {season}")
        log_info(f"URL: {batch_url}")
        log_info(f"Output file: {filename}")
        
        # Check if file already exists
        file_exists, file_path = self.check_existing_file(filename)
        
        if file_exists:
            if not self.confirm_overwrite(filename):
                return None  # User chose not to overwrite
        
        return {
            'batch_url': batch_url,
            'filename': filename,
            'year': year,
            'season': season
        }

def get_yc_batch_selection():
    """Function to be called from main.py"""
    selector = YCBatchSelector()
    return selector.select_batch()