import time
import json
import os
import sys
import logging

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

def save_to_json(data, file_path):
    # Save data to JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Data successfully saved to: {file_path}")
        logger.info(f"Total records in file: {len(data)}")
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")

def main():
    try:
        # Load configuration
        config = Config()
        logger.info(f"Starting YC scraper...")
        
        # Create Scraper_Data folder
        scraper_data_path = create_scraper_data_folder()
        json_file_path = os.path.join(scraper_data_path, "YCombinator_scraped.json")
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