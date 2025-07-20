import time
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
    ElementClickInterceptedException
)

# Google Sheet setup
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1LarZd_WShGMbrNk2znA9ZjTKksp8nE6223Vudo9p0Qw/edit?gid=5128251#gid=5128251'
SPREADSHEET_ID = SPREADSHEET_URL.split('/')[5]

def setup_gsheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
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

def is_already_connected(driver, profile_url):
    """Check if already connected or request pending"""
    driver.get(profile_url)
    time.sleep(3)  # Wait for page to load
    
    try:
        # Check for "Pending" button (request already sent)
        pending_button = driver.find_element(By.XPATH, "//span[text()='Pending']")
        if pending_button:
            print("Connection request already pending")
            return True
    except NoSuchElementException:
        pass
    
    try:
        # Check for "Message" button (already connected)
        message_button = driver.find_element(By.XPATH, "//span[text()='Message']")
        if message_button:
            print("Already connected")
            return True
    except NoSuchElementException:
        pass
    
    return False

def send_connection_request(driver, profile_url):
    """Send LinkedIn connection request"""
    driver.get(profile_url)
    time.sleep(3)  # Wait for page to load
    
    try:
        # Find and click the "Connect" button
        connect_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Connect']"))
        )
        connect_button.click()
        
        # Handle possible "Add a note" modal
        try:
            # Wait for the modal to appear (timeout quickly if it doesn't)
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "artdeco-modal"))
            )
            
            # Click "Send without a note" if available
            try:
                send_without_note = driver.find_element(By.XPATH, "//span[text()='Send without a note']")
                send_without_note.click()
                print("Sent connection request without note")
            except NoSuchElementException:
                # If no "Send without note" option, just click Send
                send_button = driver.find_element(By.XPATH, "//span[text()='Send']")
                send_button.click()
                print("Sent connection request with note")
        except TimeoutException:
            # No modal appeared, request sent directly
            print("Sent connection request directly")
        
        return True
        
    except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
        # Check if connection requires email (protected profile)
        try:
            email_required = driver.find_element(By.XPATH, "//h2[contains(text(), 'Enter their email address')]")
            if email_required:
                print("Cannot send request - email required")
                return False
        except NoSuchElementException:
            pass
        
        print(f"Failed to send connection request: {e}")
        return False

def process_profiles():
    # Load LinkedIn credentials from environment or input
    import getpass
    linkedin_email = input("Enter your LinkedIn email: ")
    linkedin_password = getpass.getpass("Enter your LinkedIn password: ")
    
    # Setup browser and login
    driver = setup_driver()
    if not login_to_linkedin(driver, linkedin_email, linkedin_password):
        print("Failed to login to LinkedIn")
        driver.quit()
        return
    
    # Get profiles from Google Sheet
    sheet = setup_gsheet()
    records = sheet.get_all_records()
    
    # Process each profile
    for i, record in enumerate(records, 1):
        linkedin_url = record.get("Founders' LinkedIn URL", "").strip()
        if not linkedin_url:
            print(f"Skipping row {i} - no LinkedIn URL")
            continue
            
        print(f"\nProcessing {i}/{len(records)}: {linkedin_url}")
        
        try:
            # Check if already connected
            if is_already_connected(driver, linkedin_url):
                continue
                
            # Send connection request
            if send_connection_request(driver, linkedin_url):
                # Mark as sent in the sheet (add a new column if needed)
                # You can implement this if you want to track sent requests
                pass
                
            # Add delay to avoid rate limiting
            time.sleep(10 + i % 5)  # Randomize delay between 10-15 seconds
            
        except Exception as e:
            print(f"Error processing {linkedin_url}: {e}")
            time.sleep(30)  # Longer delay if error occurs
    
    driver.quit()
    print("Processing completed!")

if __name__ == "__main__":
    process_profiles()
