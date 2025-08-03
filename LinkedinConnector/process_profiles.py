import os
import time
import random
import logging
import json
from dotenv import load_dotenv
from tools.blank_logger import log_blank_line
from setup_driver import setup_driver
from login_to_linkedin import login_to_linkedin
from send_connection_request import send_connection_request

logger = logging.getLogger(__name__)

def load_json_data(json_file_path):
    # Load founder data from JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded {len(data)} records from JSON file")
        return data
    except FileNotFoundError:
        logger.error(f"JSON file not found: {json_file_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        return []

def get_user_input_for_range(total_records):
    # Get user input for the range of records to process
    log_blank_line()
    logger.info(f"Total founders available: {total_records}")
    
    # Get user input for how many connections to send (default 10)
    while True:
        try:
            user_input = input(f"Enter the number of connection requests to send (default 10, max {total_records}): ").strip()
            
            if not user_input:  # Default case
                limit = min(10, total_records)
                break
            
            limit = int(user_input)
            if limit <= 0:
                print("Please enter a positive number.")
                continue
            elif limit > total_records:
                print(f"Cannot send more than {total_records} requests (total available).")
                continue
            else:
                break
                
        except ValueError:
            print("Please enter a valid number.")
    
    log_blank_line()
    logger.info(f"Will process {limit} connection requests")
    return limit

def update_json_with_status(json_file_path, processed_serials, status="sent"):
    # Update JSON file to mark processed records with connection status
    try:
        # Load current data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update records that were processed
        for record in data:
            if record.get('serial_number') in processed_serials:
                record['connection_status'] = status
        
        # Save updated data
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Updated {len(processed_serials)} records with connection status: {status}")
        
    except Exception as e:
        logger.error(f"Error updating JSON file with status: {e}")

def get_next_unprocessed_records(data, limit):
    # Get the next batch of unprocessed records
    unprocessed = []
    
    for record in data:
        # Skip if already processed (has connection_status)
        if record.get('connection_status'):
            continue
            
        # Skip if no LinkedIn URL
        founder_linkedin_url = record.get("founder_linkedin_url", "").strip()
        if not founder_linkedin_url:
            continue
            
        unprocessed.append(record)
        
        # Stop when we have enough records
        if len(unprocessed) >= limit:
            break
    
    return unprocessed

# Main function to get and process LinkedIn profiles from JSON file
def process_profiles():
    load_dotenv()
    
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    json_file_path = os.getenv("JSON_FILE_PATH")

    if not linkedin_email or not linkedin_password:
        logger.warning("Error: LinkedIn email or password not found in .env file.")
        logger.info("Please ensure LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set in the .env file!")
        return

    logger.info(f"Using LinkedIn email from .env: {linkedin_email}")
    logger.info(f"Using JSON file path: {json_file_path}")
    log_blank_line()
    
    # Load data from JSON file
    all_data = load_json_data(json_file_path)
    if not all_data:
        logger.error("No data loaded from JSON file. Exiting...")
        return
    
    # Get user input for how many connections to send
    limit = get_user_input_for_range(len(all_data))
    
    # Get next unprocessed records
    records_to_process = get_next_unprocessed_records(all_data, limit)
    
    if not records_to_process:
        logger.info("No unprocessed records found. All founders may already have connection requests sent.")
        return
    
    logger.info(f"Found {len(records_to_process)} unprocessed records to work with")
    log_blank_line()
    
    # Setup browser and login
    driver = setup_driver()
    logger.info("now here")
    if not login_to_linkedin(driver, linkedin_email, linkedin_password):
        logger.critical("Failed to login to LinkedIn")
        driver.quit()
        return
    
    # Track processed records
    processed_serials = []
    successful_connections = 0
    
    # Process each profile
    for i, record in enumerate(records_to_process, 1):
        delay_time = random.randint(0, 6)

        founder_linkedin_url = record.get("founder_linkedin_url", "").strip()
        founder_name = record.get("founder_name", "Unknown")
        company_name = record.get("company_name", "Unknown Company")
        serial_number = record.get("serial_number", "N/A")
        
        log_blank_line()
        logger.info(f"Processing {i}/{len(records_to_process)} | Serial: {serial_number}")
        logger.info(f"Founder: {founder_name} from {company_name}")
        logger.info(f"URL: {founder_linkedin_url}")
        
        try:
            driver.get(founder_linkedin_url)
            time.sleep(5)
            
            # Scroll to ensure Connect button is visible
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(1)
            
            if send_connection_request(driver):
                successful_connections += 1
                logger.info(f"✅ Successfully connected with {founder_name}")
            else:
                logger.warning(f"⚠️ Failed to connect with {founder_name}")
            
            # Track this record as processed
            processed_serials.append(serial_number)
                
            # Add delay to avoid rate limiting
            time.sleep(10 + delay_time)  # Randomize delay between 10-16 seconds
        
        except KeyboardInterrupt:
            log_blank_line()
            logger.warning("⛔ Script stopped by user")
            break
        except Exception as e:
            logger.error(f"Error processing {founder_linkedin_url}: {e}")
            processed_serials.append(serial_number)  # Mark as processed even if failed
            time.sleep(20)
    
    # Update JSON file with processed status
    if processed_serials:
        update_json_with_status(json_file_path, processed_serials)
    
    driver.quit()
    
    log_blank_line(2)
    logger.info(f"Done and dusted. Connection campaign completed!")
    logger.info(f"Successfully sent {successful_connections} out of {len(processed_serials)} connection requests")
    logger.info(f"Go and have some fun!")