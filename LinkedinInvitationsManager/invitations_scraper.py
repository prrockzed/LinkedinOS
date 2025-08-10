import time
import os
import sys
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from LinkedinConnector.setup_driver import setup_driver
from LinkedinConnector.login_to_linkedin import login_to_linkedin
from tools.info_logger import log_info, log_warning, log_error
from tools.blank_logger import log_blank_line

logger = logging.getLogger(__name__)

def scroll_to_load_all_invitations(driver, max_scrolls=20):
    """
    Scroll down the invitations page to load all pending invitations
    
    Args:
        driver: Selenium WebDriver instance
        max_scrolls: Maximum number of scroll attempts
    
    Returns:
        bool: True if scrolling completed successfully
    """
    log_info("Loading all invitations by scrolling...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    invitations_count = 0
    scroll_count = 0
    no_change_count = 0
    
    while scroll_count < max_scrolls:
        # Get current number of invitation elements
        current_invitations = driver.find_elements(By.CSS_SELECTOR, "[data-view-name='pending-invitation']")
        current_count = len(current_invitations)
        
        log_info(f"Scroll {scroll_count + 1}: Found {current_count} invitations so far")
        
        # Scroll down to load more
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for content to load
        
        # Check if new content was loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        new_invitations = driver.find_elements(By.CSS_SELECTOR, "[data-view-name='pending-invitation']")
        new_count = len(new_invitations)
        
        # Check for progress
        if new_count > current_count:
            log_info(f"Loaded {new_count - current_count} more invitations")
            no_change_count = 0
            invitations_count = new_count
        else:
            no_change_count += 1
        
        # If no new content for several attempts, we're likely done
        if no_change_count >= 3:
            log_info(f"No new invitations loading. Total found: {invitations_count}")
            break
        
        # If page height hasn't changed, we might be done
        if new_height == last_height and new_count == current_count:
            log_info(f"Page fully loaded. Total invitations: {new_count}")
            break
            
        last_height = new_height
        scroll_count += 1
    
    if scroll_count >= max_scrolls:
        log_warning(f"Reached maximum scroll limit ({max_scrolls}). Some invitations might be missed.")
    
    return True

def extract_invitation_details(invitation_element):
    """
    Extract details from a single invitation element
    
    Args:
        invitation_element: BeautifulSoup element containing invitation data
        
    Returns:
        dict: Extracted invitation details
    """
    invitation_data = {
        'name': '',
        'headline': '',
        'profile_url': '',
        'mutual_connections': '',
        'time_sent': '',
        'profile_image_url': '',
        'is_verified': False,
        'follows_you': False,
        'component_key': ''
    }
    
    try:
        # Extract component key for actions
        invitation_data['component_key'] = invitation_element.get('componentkey', '')
        
        # Extract name and profile URL
        profile_link = invitation_element.find('a', href=True)
        if profile_link:
            invitation_data['profile_url'] = profile_link.get('href', '')
            # Name is usually in a strong tag within the profile link area
            name_element = invitation_element.find('strong')
            if name_element:
                invitation_data['name'] = name_element.get_text(strip=True)
        
        # Extract headline (usually in a p tag with specific classes)
        headline_selectors = [
            'p._10bda8b2._7abcc18e._4ab35ee0',  # Based on the HTML structure
            'p[class*="_7abcc18e"]',
            'p[class*="_4ab35ee0"]'
        ]
        
        for selector in headline_selectors:
            headline_element = invitation_element.select_one(selector)
            if headline_element and headline_element.get_text(strip=True):
                # Skip if it contains "mutual connections" or time indicators
                text = headline_element.get_text(strip=True)
                if ('mutual connection' not in text.lower() and 
                    'today' not in text.lower() and 
                    'yesterday' not in text.lower() and 
                    'hour' not in text.lower() and
                    'day' not in text.lower()):
                    invitation_data['headline'] = text
                    break
        
        # Extract mutual connections info
        mutual_conn_element = invitation_element.find('p', string=lambda text: text and 'mutual connection' in text.lower())
        if mutual_conn_element:
            invitation_data['mutual_connections'] = mutual_conn_element.get_text(strip=True)
        
        # Extract time sent
        time_selectors = [
            'p._10bda8b2._390230a6._4ab35ee0',  # Time paragraph
            lambda tag: tag.name == 'p' and any(word in tag.get_text().lower() 
                                               for word in ['today', 'yesterday', 'hour', 'day', 'week'])
        ]
        
        for selector in time_selectors:
            if callable(selector):
                time_element = invitation_element.find(selector)
            else:
                time_element = invitation_element.select_one(selector)
            
            if time_element:
                time_text = time_element.get_text(strip=True)
                # Verify it's actually a time indicator
                if any(word in time_text.lower() for word in ['today', 'yesterday', 'hour', 'day', 'week']):
                    invitation_data['time_sent'] = time_text
                    break
        
        # Extract profile image URL
        img_element = invitation_element.find('img')
        if img_element:
            invitation_data['profile_image_url'] = img_element.get('src', '')
        
        # Check for verification badge
        verified_svg = invitation_element.find('svg', {'id': 'verified-small'})
        invitation_data['is_verified'] = verified_svg is not None
        
        # Check if they follow you (from aria-label or text content)
        main_text = invitation_element.get_text()
        invitation_data['follows_you'] = 'follows you' in main_text.lower()
        
        # Clean up name if it wasn't found in strong tag
        if not invitation_data['name'] and profile_link:
            # Try to extract from aria-label
            aria_label = profile_link.get('aria-label', '')
            if 'profile picture' in aria_label:
                # Extract name from "John Doe's profile picture"
                name_part = aria_label.replace("'s profile picture", "").replace(" profile picture", "")
                invitation_data['name'] = name_part
        
    except Exception as e:
        logger.warning(f"Error extracting invitation details: {e}")
    
    return invitation_data

def scrape_received_invitations():
    """
    Main function to scrape all received LinkedIn invitations
    
    Returns:
        list: List of invitation data dictionaries
    """
    load_dotenv()
    
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    
    if not linkedin_email or not linkedin_password:
        log_error("LinkedIn credentials not found in .env file")
        log_info("Please ensure LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set")
        return []
    
    driver = setup_driver()
    invitations = []
    
    try:
        # Login to LinkedIn
        if not login_to_linkedin(driver, linkedin_email, linkedin_password):
            log_error("Failed to login to LinkedIn")
            return []
        
        log_info("Successfully logged in to LinkedIn")
        log_blank_line()
        
        # Navigate to invitations page
        invitations_url = "https://www.linkedin.com/mynetwork/invitation-manager/received/"
        log_info(f"Navigating to: {invitations_url}")
        driver.get(invitations_url)
        
        # Wait for page to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-view-name='pending-invitation']"))
            )
            log_info("Invitations page loaded successfully")
        except TimeoutException:
            log_warning("No pending invitations found or page didn't load properly")
            return []
        
        # Scroll to load all invitations
        scroll_to_load_all_invitations(driver)
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all invitation elements
        invitation_elements = soup.find_all('div', {'data-view-name': 'pending-invitation'})
        
        log_info(f"Found {len(invitation_elements)} invitation elements to process")
        log_blank_line()
        
        # Extract details from each invitation
        for i, element in enumerate(invitation_elements, 1):
            log_info(f"Processing invitation {i}/{len(invitation_elements)}")
            
            invitation_data = extract_invitation_details(element)
            
            if invitation_data['name']:  # Only add if we got at least a name
                invitations.append(invitation_data)
                log_info(f"✅ Extracted: {invitation_data['name']}")
            else:
                log_warning(f"⚠️ Failed to extract name from invitation {i}")
        
        log_blank_line()
        log_info(f"Successfully extracted {len(invitations)} complete invitations")
        
    except Exception as e:
        log_error(f"Error during scraping: {e}")
        logger.exception("Full error details:")
        
    finally:
        driver.quit()
        log_info("Browser closed")
    
    return invitations