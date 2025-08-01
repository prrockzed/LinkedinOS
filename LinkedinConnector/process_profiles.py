import os
import time
import random
import logging
from dotenv import load_dotenv
from blank_logger import log_blank_line
from setup_gsheet import setup_gsheet
from setup_driver import setup_driver
from login_to_linkedin import login_to_linkedin
from send_connection_request import send_connection_request

logger = logging.getLogger(__name__)

# Main function to get and process LinkedIn profiles from Google Sheet
def process_profiles():
    load_dotenv()
    
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    spreadsheet_url = os.getenv("SPREADSHEET_URL")

    if not linkedin_email or not linkedin_password:
        logger.warning("Error: LinkedIn email or password not found in .env file.")
        logger.info("Please ensure LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set in the .env file!")
        return
    if not spreadsheet_url:
        logger.warning("Error: Google Sheet URL not found in .env file.")
        logger.info("Please ensure SPREADSHEET_URL is set in the .env file!")
        return

    logger.info(f"Using LinkedIn email from .env: {linkedin_email}")
    logger.info(f"Using Google Sheet URL from .env: {spreadsheet_url}")
    log_blank_line(2)
    
    # Setup browser and login
    driver = setup_driver()
    if not login_to_linkedin(driver, linkedin_email, linkedin_password):
        logger.critical("Failed to login to LinkedIn")
        driver.quit()
        return
    
    # Get profiles from Google Sheet
    sheet = setup_gsheet(spreadsheet_url=spreadsheet_url)
    records = sheet.get_all_records()
    
    # Process each profile
    for i, record in enumerate(records, 1):
        delay_time = random.randint(0, 6)

        founder_linkedin_url = record.get("Founders' LinkedIn URL", "").strip()
        if not founder_linkedin_url:
            logger.warning(f"Skipping row {i} - no LinkedIn URL")
            continue
            
        log_blank_line()
        logger.info(f"Processing {i}/{len(records)}: {founder_linkedin_url}")
        
        try:
            driver.get(founder_linkedin_url)
            time.sleep(5)
            
            # Scroll to ensure Connect button is visible
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(1)
            
            if not send_connection_request(driver):
                logger.warning(f"⚠️ Failed to connect with {founder_linkedin_url.split('/')[-1]}")
                
            # Add delay to avoid rate limiting
            time.sleep(10 + delay_time)  # Randomize delay between 10-16 seconds
        
        except KeyboardInterrupt:
            log_blank_line()
            logger.warning("⛔ Script stopped by user")
            break
        except Exception as e:
            logger.error(f"Error processing {founder_linkedin_url}: {e}")
            time.sleep(20)
    
    driver.quit()
    
    log_blank_line(2)
    logger.info("✅ Done and Dusted. Connection campaign completed!! Go and have some fun")