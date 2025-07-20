import os
import time
import random
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException,
)


def setup_gsheet(spreadsheet_url):
    spreadsheet_id = spreadsheet_url.split('/')[5]
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).sheet1
    return sheet

def setup_driver():
    options = webdriver.ChromeOptions()
    
    # To persist session and avoid frequent logins
    options.add_argument("--user-data-dir=./chrome_profile")
    
    # Recommended options for stability
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login_to_linkedin(driver, email, password):
    """Log in to LinkedIn if not already logged in"""
    driver.get("https://www.linkedin.com/login")
    
    try:
        # Check if already logged in by looking for feed element
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".scaffold-finite-scroll__content"))
        )
        print("Already logged in to LinkedIn")
        return True
    except TimeoutException:
        pass
    
    try:
        # Fill in login form
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        
        # Click login button
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for login to complete
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".scaffold-finite-scroll__content"))
        )
        print("Successfully logged in to LinkedIn")
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False

def send_connection_request(driver):
    # Try both variants of Connect button
    connect_button = None
    
    # Variant 1: Handle potential "More" button dropdown first
    try:
        # First check if there's a "More" button
        more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(@class, 'artdeco-dropdown__trigger') and .//span[text()='More']]"))
        )
        
        # Click the More button to expand dropdown
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", more_button)
        print("🔘 More button clicked to expand menu")
        time.sleep(1)  # Wait for dropdown to appear
        
        # Now look for Connect button in dropdown
        try:
            connect_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//div[contains(@class, 'artdeco-dropdown__content')]//span[contains(@class, 'display-flex') and contains(@class, 't-normal') and contains(@class, 'flex-1') and text()='Connect']"))
            )
            print("Found Connect button in More dropdown")
        except TimeoutException:
            print("No Connect button found in More dropdown")
            return False
            
    except TimeoutException:
        # If no More button, proceed with normal Connect button check
        try:
            connect_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//span[contains(@class, 'display-flex') and contains(@class, 't-normal') and contains(@class, 'flex-1') and text()='Connect']"))
            )
            print("Found standard Connect button (no More menu needed)")
        except TimeoutException:
            print("No standard Connect button found")
            pass
    
    # Variant 2: <span class="artdeco-button__text">Connect</span> (with parent class check)
    if not connect_button:
        try:
            connect_span = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                    "//span[contains(@class, 'artdeco-button__text') and text()='Connect']"))
            )
            
            # Get the parent button element
            parent_button = connect_span.find_element(By.XPATH, "./..")
            
            # Verify parent has required classes
            parent_classes = parent_button.get_attribute("class").split()
            required_classes = {"artdeco-button", "artdeco-button--2", "artdeco-button--primary", "ember-view"}
            
            if not all(cls in parent_classes for cls in required_classes):
                print("⚠️ Connect button parent doesn't have required classes - skipping")
                return False
                
            connect_button = parent_button
                
        except TimeoutException:
            print("⚠️ No connect button found")
            return False
        except NoSuchElementException:
            print("⚠️ Couldn't verify parent element - skipping")
            return False

    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", connect_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", connect_button)
        print("🔘 Connect button clicked")
        
        # Handle Send without note if appears
        try:
            send_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//span[text()='Send without a note']/ancestor::button[contains(@class, 'artdeco-button')]"))
            )
            driver.execute_script("arguments[0].click();", send_button)
            print("✅ Connection sent (without note)")
            return True
        except TimeoutException:
            print("ℹ️ No 'Send without note' dialog appeared")
            return True
            
    except Exception as e:
        print(f"❌ Error sending connection: {str(e)}")
        return False


def process_profiles():
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

if __name__ == "__main__":
    process_profiles()
