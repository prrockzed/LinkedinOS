import os
import time
import random
from dotenv import load_dotenv
from setup_gsheet import setup_gsheet
from setup_driver import setup_driver
from login_to_linkedin import login_to_linkedin
from send_connection_request import send_connection_request

def process_profiles():
    """Main function to process LinkedIn profiles from Google Sheet"""
    load_dotenv()
    
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    spreadsheet_url = os.getenv("SPREADSHEET_URL")

    if not linkedin_email or not linkedin_password:
        print("Error: LinkedIn email or password not found in .env file.")
        print("Please ensure LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set in the .env file!")
        return
    if not spreadsheet_url:
        print("Error: Google Sheet URL not found in .env file.")
        print("Please ensure SPREADSHEET_URL is set in the .env file!")
        return

    print(f"\nUsing LinkedIn email from .env: {linkedin_email}")
    print(f"Using Google Sheet URL from .env: {spreadsheet_url}\n")
    
    # Setup browser and login
    driver = setup_driver()
    if not login_to_linkedin(driver, linkedin_email, linkedin_password):
        print("Failed to login to LinkedIn")
        driver.quit()
        return
    
    # Get profiles from Google Sheet
    sheet = setup_gsheet(spreadsheet_url=spreadsheet_url)
    records = sheet.get_all_records()
    
    # Process each profile
    for i, record in enumerate(records, 1):
        delay_time = random.randint(0, 6)

        linkedin_url = record.get("Founders' LinkedIn URL", "").strip()
        if not linkedin_url:
            print(f"Skipping row {i} - no LinkedIn URL")
            continue
            
        print(f"\nProcessing {i}/{len(records)}: {linkedin_url}")
        
        try:
            driver.get(linkedin_url)
            time.sleep(5)
            
            # Scroll to ensure Connect button is visible
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(1)
            
            if not send_connection_request(driver):
                print(f"⚠️ Failed to connect with {linkedin_url.split('/')[-1]}")
                
            # Add delay to avoid rate limiting
            time.sleep(10 + delay_time)  # Randomize delay between 10-16 seconds
        
        except KeyboardInterrupt:
            print("\n⛔ Script stopped by user")
            break
        except Exception as e:
            print(f"Error processing {linkedin_url}: {e}")
            time.sleep(20)
    
    driver.quit()
    print("\n\n✅ Done and Dusted. Connection campaign completed!! Go and have some fun")