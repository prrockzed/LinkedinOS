import time
import json
import os
import sys
import logging
from urllib.parse import urlparse, parse_qs


# Configure logging for this script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from settings import Config
from tools.blank_logger import log_blank_line
from yc_scraper import get_yc_2025_links
from company_extractor import extract_founders

logger = logging.getLogger(__name__)

def create_scraper_data_folder():
    # Create Scraper_Data folder if it doesn't exist
    scraper_data_path = "GetCompanies/Scraper_Data"
    if not os.path.exists(scraper_data_path):
        os.makedirs(scraper_data_path)
        logger.info(f"Created directory: {scraper_data_path}")
    else:
        logger.info(f"Directory already exists: {scraper_data_path}")
    log_blank_line()
    return scraper_data_path

def add_numbering_to_data(all_founders_data):
    """Add serial numbers and company numbers to the founders data"""
    company_url_to_number = {}
    company_counter = 1
    serial_counter = 1
    
    # Process each founder record
    for founder_data in all_founders_data:
        company_url = founder_data.get('company_url', '')
        
        # Assign company number (same for all founders from the same company)
        if company_url not in company_url_to_number:
            company_url_to_number[company_url] = company_counter
            company_counter += 1
        
        # Create new ordered dictionary with serial number and company number first
        numbered_data = {
            "serial_number": serial_counter,
            "company_number": company_url_to_number[company_url]
        }
        
        # Add all existing data
        numbered_data.update(founder_data)
        
        # Replace the original data with numbered data
        all_founders_data[all_founders_data.index(founder_data)] = numbered_data
        
        serial_counter += 1
    
    return all_founders_data

def save_to_json(data, file_path):
    # Save data to JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Data successfully saved to: {file_path}")
        logger.info(f"Total records in file: {len(data)}")
        
        # Log summary statistics
        if data:
            unique_companies = len(set(record.get('company_number', 0) for record in data))
            logger.info(f"Total unique companies: {unique_companies}")
            logger.info(f"Total founders: {len(data)}")
            
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")

def generate_json_filename(batch_url):
    """
    Generates a filename like 'YC_S25_scraped.json' from a URL like
    'https://www.ycombinator.com/companies?batch=Summer%202025'.
    """
    try:
        # Parse the URL to extract the 'batch' query parameter
        parsed_url = urlparse(batch_url)
        query_params = parse_qs(parsed_url.query)
        
        # The value will be a list, e.g., ['Summer 2025']
        batch_info = query_params.get('batch', [''])[0]
        
        if not batch_info:
            # Fallback filename if batch info is not found
            return "YC_UNKNOWN_scraped.json"

        # Split the batch info into season and year, e.g., "Summer", "2025"
        parts = batch_info.split()
        if len(parts) != 2:
            return "YC_INVALID_scraped.json"
            
        season, year = parts[0], parts[1]

        # Map the full season name to its first letter
        season_map = {
            'Summer': 'S',
            'Winter': 'W',
            'Fall': 'F',
            'Spring': 'X' # As requested
        }
        
        season_char = season_map.get(season, '?') # '?' for unknown seasons
        
        # Get the last two digits of the year
        year_short = year[-2:]
        
        # Construct the final filename
        return f"YC_{season_char}{year_short}_scraped.json"

    except Exception as e:
        logger.error(f"Could not generate filename from URL '{batch_url}': {e}")
        return "YC_ERROR_scraped.json"


def main():
    try:
        # Load configuration
        config = Config()
        logger.info(f"Starting YC scraper...")
        
        # Create Scraper_Data folder
        scraper_data_path = create_scraper_data_folder()
        
        y_combinator_batch_url = config.y_combinator_batch
        json_filename = generate_json_filename(y_combinator_batch_url)
        
        json_file_path = os.path.join(scraper_data_path, json_filename)
        logger.info(f"The json_file_path is: {json_file_path}")
        log_blank_line()
        
        # Get YC company links
        logger.info("Scraping started... might have to wait for a while")
        yc_links = get_yc_2025_links(config.y_combinator_url, config.y_combinator_batch)
        logger.info(f"Found {len(yc_links)} company links")
        log_blank_line()
        
        # Extract data from each company
        all_founders_data = []
        for i, link in enumerate(yc_links, 1):
            logger.info(f"Processing {i}/{len(yc_links)}: {link}")
            try:
                founders = extract_founders(link)
                if founders:
                    all_founders_data.extend(founders)
                    logger.info(f"Found {len(founders)} founders")
                else:
                    logger.warning(f"No founders found")
            except Exception as e:
                logger.error(f"  Error processing {link}: {e}")
                
            log_blank_line()
            
            # Add delay to avoid rate limiting
            time.sleep(2)

        log_blank_line()
        logger.info(f"Total founders found: {len(all_founders_data)}")
        
        # Add serial numbers and company numbers
        logger.info("Adding serial numbers and company numbers...")
        all_founders_data = add_numbering_to_data(all_founders_data)
        logger.info("Numbering completed!")
        log_blank_line()
        
        # Save data to JSON file
        save_to_json(all_founders_data, json_file_path)
        
        log_blank_line()
        logger.info("Scraping completed!")
        logger.info(f"Data saved to: {json_file_path}")
        log_blank_line()
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()