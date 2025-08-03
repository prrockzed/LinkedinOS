import time
import os
import sys
import logging
from tools.info_logger import log_info, log_warning, log_error
from settings import Config
from yc_scraper import get_yc_2025_links
from company_extractor import extract_founders
from yc_scraper_utils import (
    create_scraper_data_folder,
    add_numbering_to_data,
    save_to_json,
    generate_json_filename
)

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

def main():
    try:
        # Load configuration
        config = Config()
        log_info(f"Starting YC scraper...")
        
        # Create Scraper_Data folder
        scraper_data_path = create_scraper_data_folder()
        
        y_combinator_batch_url = config.y_combinator_batch
        json_filename = generate_json_filename(y_combinator_batch_url)
        
        json_file_path = os.path.join(scraper_data_path, json_filename)
        log_info(f"The json_file_path is: {json_file_path}", 1)
        
        # Get YC company links
        log_info("Scraping started... might have to wait for a while")
        yc_links = get_yc_2025_links(config.y_combinator_url, config.y_combinator_batch)
        log_info(f"Found {len(yc_links)} company links", 1)
        
        # Extract data from each company
        all_founders_data = []
        for i, link in enumerate(yc_links, 1):
            log_info(f"Processing {i}/{len(yc_links)}: {link}")
            try:
                founders = extract_founders(link)
                if founders:
                    all_founders_data.extend(founders)
                    log_info(f"Found {len(founders)} founders", 1)
                else:
                    log_warning(f"No founders found", 1)
            except Exception as e:
                log_error(f"  Error processing {link}: {e}", 1)
            
            # Add delay to avoid rate limiting
            time.sleep(2)

        log_info(1, f"Total founders found: {len(all_founders_data)}")
        
        # Add serial numbers and company numbers
        log_info("Adding serial numbers and company numbers...")
        all_founders_data = add_numbering_to_data(all_founders_data)
        log_info("Numbering completed!", 1)
        
        # Save data to JSON file
        save_to_json(all_founders_data, json_file_path)
        
        log_info(1, "Scraping completed!")
        log_info(f"Data saved to: {json_file_path}", 1)
        
    except Exception as e:
        log_error(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()