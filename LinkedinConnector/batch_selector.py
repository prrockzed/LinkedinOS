import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.get_user_choice import get_user_choice
from tools.info_logger import log_info, log_warning, log_error
from tools.blank_logger import log_blank_line

class LinkedInBatchSelector:
    def __init__(self):
        self.scraper_data_path = os.path.join(os.path.dirname(__file__), "../GetCompanies/Scraper_Data")
        
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
    
    def check_file_exists(self, filename):
        """Check if the scraped data file exists"""
        file_path = os.path.join(self.scraper_data_path, filename)
        return os.path.exists(file_path), file_path
    
    def list_available_files(self):
        """List all available scraped YC files"""
        if not os.path.exists(self.scraper_data_path):
            return []
        
        yc_files = []
        for file in os.listdir(self.scraper_data_path):
            if file.startswith("YC_") and file.endswith("_scraped.json"):
                yc_files.append(file)
        
        return sorted(yc_files)
    
    def show_available_files(self):
        """Show user what files are available"""
        available_files = self.list_available_files()
        
        if available_files:
            log_info("Available scraped YC batch files:")
            for i, file in enumerate(available_files, 1):
                # Parse filename to show readable format
                try:
                    parts = file.replace("YC_", "").replace("_scraped.json", "")
                    season_char = parts[0]
                    year = "20" + parts[1:]
                    
                    season_map = {'S': 'Summer', 'W': 'Winter', 'F': 'Fall', 'X': 'Spring'}
                    season_name = season_map.get(season_char, 'Unknown')
                    
                    log_info(f"  {i}. {season_name} {year} ({file})")
                except:
                    log_info(f"  {i}. {file}")
        else:
            log_warning("No scraped YC batch files found in Scraper_Data folder")
    
    def prompt_to_scrape_first(self, season, year, filename):
        """Prompt user to scrape data first if file doesn't exist"""
        log_blank_line()
        log_error(f"File '{filename}' not found!")
        log_info(f"The data for {season} {year} has not been scraped yet.")
        log_blank_line()
        log_info("To send LinkedIn connections for this batch, you need to:")
        log_info("1. Go back to main menu")
        log_info("2. Choose option 1 (Run YCombinator Scraper)")
        log_info(f"3. Select {season} {year} to scrape the data first")
        log_info("4. Then come back here to send connections")
        log_blank_line()
        
        # Show what files are available
        self.show_available_files()
        
        return False
    
    def select_batch_for_connections(self):
        """Main method to select Y Combinator batch for LinkedIn connections"""
        log_info(1, "=== LinkedIn Connection Batch Selection ===", 1)
        log_info("Select which Y Combinator batch you want to send LinkedIn connections to:")
        
        # Get year from user
        year = self.get_valid_year()
        
        # Get season from user
        season = self.get_valid_season(year)
        
        # Generate filename and check if it exists
        filename = self.generate_filename(season, year)
        file_exists, file_path = self.check_file_exists(filename)
        
        log_blank_line()
        log_info(f"Connection Batch Summary:")
        log_info(f"Year: {year}")
        log_info(f"Season: {season}")
        log_info(f"Looking for file: {filename}")
        
        if not file_exists:
            self.prompt_to_scrape_first(season, year, filename)
            return None
        
        log_info(f"Found data file: {filename}")
        log_info(f"File path: {file_path}")
        
        return {
            'file_path': file_path,
            'filename': filename,
            'year': year,
            'season': season
        }

def get_linkedin_batch_selection():
    """Function to be called from main.py"""
    selector = LinkedInBatchSelector()
    return selector.select_batch_for_connections()