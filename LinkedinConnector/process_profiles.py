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

def update_json_with_connection_status(json_file_path, status_updates):
    """Update JSON file with connection status for specific records
    
    Args:
        json_file_path (str): Path to the JSON file
        status_updates (dict): Dictionary mapping serial_number to connection_status
                                e.g., {1: 'Connection Sent', 2: 'Failed to connect'}
    """
    try:
        # Load current data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update records with new connection status
        updated_count = 0
        for record in data:
            serial_number = record.get('serial_number')
            if serial_number in status_updates:
                record['connection_status'] = status_updates[serial_number]
                record['processed_data'] = True
                updated_count += 1
        
        # Save updated data
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        log_blank_line()
        logger.info(f"Updated {updated_count} records with connection status")
        
        # Log status summary
        status_summary = {}
        for status in status_updates.values():
            status_summary[status] = status_summary.get(status, 0) + 1
        
        for status, count in status_summary.items():
            logger.info(f"{status}: {count} records")
        
    except Exception as e:
        logger.error(f"Error updating JSON file with connection status: {e}")

def get_next_unprocessed_records(data, limit):
    """Get the next batch of unprocessed records starting from the first False in processed_data"""
    unprocessed = []
    
    # First, sort data by serial_number to ensure correct order
    sorted_data = sorted(data, key=lambda x: x.get('serial_number', 0))
    
    # Find the first record with processed_data = False
    start_processing = False
    
    for record in sorted_data:
        # Start processing from the first False value
        if not start_processing and not record.get('processed_data', False):
            start_processing = True
            logger.info(f"Starting from serial number: {record.get('serial_number', 'N/A')}")
        
        # If we haven't reached the first False yet, skip
        if not start_processing:
            continue
            
        # Skip if already processed (processed_data is True)
        if record.get('processed_data', False):
            continue
            
        # Skip if no LinkedIn URL
        founder_linkedin_url = record.get("founder_linkedin_url", "").strip()
        if not founder_linkedin_url:
            logger.warning(f"Skipping serial {record.get('serial_number', 'N/A')} - no LinkedIn URL")
            continue
            
        unprocessed.append(record)
        
        # Stop when we have enough records
        if len(unprocessed) >= limit:
            break
    
    if unprocessed:
        first_serial = unprocessed[0].get('serial_number', 'N/A')
        last_serial = unprocessed[-1].get('serial_number', 'N/A')
        logger.info(f"Selected records from serial {first_serial} to {last_serial}")
    
    return unprocessed

def get_batch_info_from_filename(json_file_path):
    """Extract batch information from filename for display"""
    filename = os.path.basename(json_file_path)
    
    if filename.startswith("YC_") and filename.endswith("_scraped.json"):
        try:
            parts = filename.replace("YC_", "").replace("_scraped.json", "")
            season_char = parts[0]
            year = "20" + parts[1:]
            
            season_map = {'S': 'Summer', 'W': 'Winter', 'F': 'Fall', 'X': 'Spring'}
            season_name = season_map.get(season_char, 'Unknown')
            
            return f"{season_name} {year}"
        except:
            pass
    
    return filename

def show_processing_stats(data, json_file_path):
    """Show statistics about the data to be processed"""
    total_records = len(data)
    
    # Count processed records using processed_data parameter
    processed_records = len([r for r in data if r.get('processed_data', False)])
    unprocessed_records = total_records - processed_records
    
    # Connection status statistics
    status_counts = {}
    for record in data:
        status = record.get('connection_status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Find the first unprocessed record's serial number
    sorted_data = sorted(data, key=lambda x: x.get('serial_number', 0))
    first_unprocessed_serial = None
    for record in sorted_data:
        if not record.get('processed_data', False) and record.get("founder_linkedin_url", "").strip():
            first_unprocessed_serial = record.get('serial_number', 'N/A')
            break
    
    # Count records with LinkedIn URLs that can be processed (from first False onwards)
    processable_records = 0
    start_counting = False
    for record in sorted_data:
        if not start_counting and not record.get('processed_data', False):
            start_counting = True
        
        if start_counting and not record.get('processed_data', False) and record.get("founder_linkedin_url", "").strip():
            processable_records += 1
    
    unique_companies = len(set(r.get('company_number', 0) for r in data if r.get('company_number')))
    
    batch_info = get_batch_info_from_filename(json_file_path)
    
    log_blank_line()
    logger.info(f"Data Statistics for {batch_info}:")
    logger.info(f"Total founders: {total_records}")
    logger.info(f"Unique companies: {unique_companies}")
    logger.info(f"Already processed: {processed_records}")
    logger.info(f"Remaining unprocessed: {unprocessed_records}")
    
    # Show connection status breakdown
    logger.info("Connection Status Breakdown:")
    for status, count in sorted(status_counts.items()):
        logger.info(f"  {status}: {count}")
    
    if first_unprocessed_serial:
        logger.info(f"Next processing will start from serial: {first_unprocessed_serial}")
    logger.info(f"Available for processing (from first False): {processable_records}")

# Main function to get and process LinkedIn profiles from JSON file
def process_profiles_with_file(json_file_path):
    """Process profiles using a specific JSON file path"""
    load_dotenv()
    
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")

    if not linkedin_email or not linkedin_password:
        logger.warning("Error: LinkedIn email or password not found in .env file.")
        logger.info("Please ensure LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set in the .env file!")
        return

    logger.info(f"Using LinkedIn email from .env: {linkedin_email}")
    logger.info(f"Using JSON file: {json_file_path}")
    
    # Load data from JSON file
    all_data = load_json_data(json_file_path)
    if not all_data:
        logger.error("No data loaded from JSON file. Exiting...")
        return
    
    # Show processing statistics
    show_processing_stats(all_data, json_file_path)
    
    # Get user input for how many connections to send
    available_records = 0
    sorted_data = sorted(all_data, key=lambda x: x.get('serial_number', 0))
    start_counting = False
    
    # Count available records from the first False onwards
    for record in sorted_data:
        if not start_counting and not record.get('processed_data', False):
            start_counting = True
        
        if start_counting and not record.get('processed_data', False) and record.get("founder_linkedin_url", "").strip():
            available_records += 1
    
    if available_records == 0:
        logger.info("No unprocessed records with LinkedIn URLs found. All founders may already have been processed.")
        return
    
    limit = get_user_input_for_range(available_records)
    
    # Get next unprocessed records
    records_to_process = get_next_unprocessed_records(all_data, limit)
    
    if not records_to_process:
        logger.info("No unprocessed records found. All founders may already have been processed.")
        return
    
    logger.info(f"Found {len(records_to_process)} unprocessed records to work with")
    log_blank_line()
    
    # Setup browser and login
    driver = setup_driver()
    if not login_to_linkedin(driver, linkedin_email, linkedin_password):
        logger.critical("Failed to login to LinkedIn")
        driver.quit()
        return
    
    # Track connection results
    status_updates = {}  # serial_number -> connection_status
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
                status_updates[serial_number] = "Connection Sent"
                logger.info(f"Successfully sent connection request to {founder_name}")
            else:
                status_updates[serial_number] = "Failed to connect"
                logger.warning(f"Failed to send connection requet to {founder_name}")
                
            # Add delay to avoid rate limiting
            time.sleep(10 + delay_time)  # Randomize delay between 10-16 seconds
        
        except KeyboardInterrupt:
            log_blank_line()
            logger.warning("Script stopped by user")
            break
        except Exception as e:
            logger.error(f"Error processing {founder_linkedin_url}: {e}")
            status_updates[serial_number] = "Failed to connect"
            time.sleep(20)
    
    # Update JSON file with connection status
    if status_updates:
        update_json_with_connection_status(json_file_path, status_updates)
    
    driver.quit()
    
    log_blank_line(2)
    logger.info(f"Done and dusted. Connection campaign completed!")
    logger.info(f"Successfully sent {successful_connections} out of {len(status_updates)} connection requests")
    logger.info(f"Updated {len(status_updates)} founders with connection status")
    logger.info(f"Go and have some fun!")

# Legacy function for backward compatibility (if needed)
def process_profiles():
    """Legacy function that uses .env file path - kept for backward compatibility"""
    load_dotenv()
    json_file_path = os.getenv("JSON_FILE_PATH")
    
    if not json_file_path:
        logger.error("JSON_FILE_PATH not found in .env file")
        return
    
    process_profiles_with_file(json_file_path)