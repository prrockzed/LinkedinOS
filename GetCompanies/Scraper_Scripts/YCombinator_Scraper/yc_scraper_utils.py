import json
import os
import logging
from urllib.parse import urlparse, parse_qs
from tools.blank_logger import log_blank_line

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
    """Add serial numbers, company numbers, processed_data parameter, and connection_status to the founders data"""
    company_url_to_number = {}
    company_counter = 1
    serial_counter = 1
    
    # Process each founder record
    for founder_data in all_founders_data:
        company_url = founder_data.get('company_yc_url', '')
        
        # Assign company number (same for all founders from the same company)
        if company_url not in company_url_to_number:
            company_url_to_number[company_url] = company_counter
            company_counter += 1
        
        # Create new ordered dictionary with serial number, company number, processed_data, and connection_status first
        numbered_data = {
            "serial_number": serial_counter,
            "company_number": company_url_to_number[company_url],
            "processed_data": False,  # Initially set to False
            "connection_status": "NA"  # Initially set to "NA"
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
            processed_count = len([record for record in data if record.get('processed_data', False)])
            na_status_count = len([record for record in data if record.get('connection_status') == 'NA'])
            logger.info(f"Total unique companies: {unique_companies}")
            logger.info(f"Total founders: {len(data)}")
            logger.info(f"Initially processed: {processed_count} (should be 0 for new scrapes)")
            logger.info(f"Connection status 'NA': {na_status_count} (should be {len(data)} for new scrapes)")
            
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