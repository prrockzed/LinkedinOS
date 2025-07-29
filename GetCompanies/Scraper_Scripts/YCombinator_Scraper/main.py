import time
import json
import os
import logging
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
        print(f"Created directory: {scraper_data_path}")
    else:
        print(f"Directory already exists: {scraper_data_path}")
    return scraper_data_path

def save_to_json(data, file_path):
    # Save data to JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data successfully saved to: {file_path}")
        print(f"Total records in file: {len(data)}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

def main():
    try:
        # Load configuration
        config = Config()
        print(f"Starting YC scraper...\n")
        
        # Create Scraper_Data folder
        scraper_data_path = create_scraper_data_folder()
        json_file_path = os.path.join(scraper_data_path, "YCombinator_scraped.json")
        logger.info("The json_file_path is: ", json_file_path)
        
        # Get YC company links
        print("\nStarting YC company scraping...")
        yc_links = get_yc_2025_links(config.y_combinator_url, config.y_combinator_batch)
        logger.info(f"Found {len(yc_links)} company links")
        log_blank_line()
        
        # Extract data from each company
        all_founders_data = []
        for i, link in enumerate(yc_links, 1):
            if i > 5:
                break
            logger.info(f"Processing {i}/{len(yc_links)}: {link}")
            try:
                founders = extract_founders(link)
                if founders:
                    all_founders_data.extend(founders)
                    print(f"  Found {len(founders)} founders")
                else:
                    print(f"  No founders found")
            except Exception as e:
                print(f"  Error processing {link}: {e}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)

        print(f"\nTotal founders found: {len(all_founders_data)}")
        
        # Save data to JSON file
        save_to_json(all_founders_data, json_file_path)
        
        print("Scraping completed!")
        print(f"Data saved to: {json_file_path}")
        
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()