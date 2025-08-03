import time
import os
import sys
import logging
from tools.info_logger import log_info, log_warning, log_error
from yc_scraper import get_yc_2025_links
from company_extractor import extract_founders
from yc_scraper_utils import (
    create_scraper_data_folder,
    add_numbering_to_data,
    save_to_json,
    generate_json_filename
)
from batch_selector import get_yc_batch_selection

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
        # Get user's batch selection
        log_info(f"Starting YC scraper with interactive batch selection...")
        
        batch_selection = get_yc_batch_selection()
        
        if not batch_selection:
            log_info("Scraping cancelled. Exiting...")
            return
        
        # Create Scraper_Data folder
        scraper_data_path = create_scraper_data_folder()
        
        # Use the selected batch URL and filename
        y_combinator_url = "https://www.ycombinator.com"
        y_combinator_batch_url = batch_selection['batch_url']
        json_filename = batch_selection['filename']
        
        json_file_path = os.path.join(scraper_data_path, json_filename)
        log_info(f"The json_file_path is: {json_file_path}", 1)
        
        # Get YC company links
        log_info("Scraping started... this will take a while as we need to load all companies")
        log_info("The script will scroll through the page multiple times to load all companies")
        log_info("Please be patient - this process can take 2-5 minutes depending on the batch size", 1)
        
        yc_links = get_yc_2025_links(y_combinator_url, y_combinator_batch_url)
        log_info(f"Successfully found {len(yc_links)} company links", 1)
        
        if len(yc_links) == 0:
            log_warning("No company links found. This might be because:")
            log_warning("1. The batch URL is incorrect")
            log_warning("2. The batch doesn't exist")
            log_warning("3. There are no companies in this batch")
            log_warning("Please verify the batch information and try again.")
            return
        
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
        
        if len(all_founders_data) == 0:
            log_warning("No founder data was extracted. Exiting without saving.")
            return
        
        # Add serial numbers and company numbers
        log_info("Adding serial numbers and company numbers...")
        all_founders_data = add_numbering_to_data(all_founders_data)
        log_info("Numbering completed!", 1)
        
        # Save data to JSON file
        save_to_json(all_founders_data, json_file_path)
        
        log_info(1, "Scraping completed successfully!")
        log_info(f"Data saved to: {json_file_path}")
        log_info(f"Total companies processed: {len(set(record.get('company_number', 0) for record in all_founders_data))}")
        log_info(f"Total founders found: {len(all_founders_data)}", 1)
        
    except KeyboardInterrupt:
        log_warning(1, "Scraping interrupted by user. Exiting...")
    except Exception as e:
        log_error(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()