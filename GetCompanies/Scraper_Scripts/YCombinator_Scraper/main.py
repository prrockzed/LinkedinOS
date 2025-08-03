import time
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
from yc_scraper_utils import (
    create_scraper_data_folder,
    add_numbering_to_data,
    save_to_json,
    generate_json_filename
)

logger = logging.getLogger(__name__)

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