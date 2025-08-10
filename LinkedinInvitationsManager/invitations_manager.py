import time
import os
import sys
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from LinkedinConnector.setup_driver import setup_driver
from LinkedinConnector.login_to_linkedin import login_to_linkedin
from tools.info_logger import log_info, log_warning, log_error
from tools.blank_logger import log_blank_line
from tools.get_user_choice import get_user_choice

logger = logging.getLogger(__name__)

def display_invitation_details(invitation, index, total):
    """
    Display detailed information about a single invitation
    
    Args:
        invitation (dict): Invitation data
        index (int): Current invitation number
        total (int): Total number of invitations
    """
    log_blank_line()
    log_info(f"=== Invitation {index}/{total} ===")
    log_info(f"👤 Name: {invitation.get('name', 'Unknown')}")
    
    if invitation.get('headline'):
        log_info(f"💼 Headline: {invitation['headline']}")
    
    if invitation.get('mutual_connections'):
        log_info(f"🤝 {invitation['mutual_connections']}")
    
    if invitation.get('time_sent'):
        log_info(f"📅 Sent: {invitation['time_sent']}")
    
    if invitation.get('is_verified'):
        log_info("✅ Verified Profile")
    
    if invitation.get('follows_you'):
        log_info("👥 Follows you")
    
    if invitation.get('profile_url'):
        log_info(f"🔗 Profile: {invitation['profile_url']}")
    
    log_blank_line()

def accept_invitation(driver, invitation):
    """
    Accept a LinkedIn invitation
    
    Args:
        driver: Selenium WebDriver instance
        invitation (dict): Invitation data containing component_key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        component_key = invitation.get('component_key', '')
        if not component_key:
            log_error("No component key found for this invitation")
            return False
        
        # Find the Accept button using aria-label and component key
        accept_button_xpath = f"//button[@componentkey and contains(@aria-label, 'Accept') and contains(@aria-label, '{invitation.get('name', '')}')]"
        
        # Alternative: Find by button text
        if not component_key:
            accept_button_xpath = "//button[.//span[text()='Accept']]"
        
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, accept_button_xpath))
            )
            
            # Scroll to button and click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", accept_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", accept_button)
            
            log_info(f"✅ Accepted invitation from {invitation.get('name', 'Unknown')}")
            time.sleep(2)  # Wait for action to complete
            return True
            
        except TimeoutException:
            log_error(f"Could not find Accept button for {invitation.get('name', 'Unknown')}")
            return False
            
    except Exception as e:
        log_error(f"Error accepting invitation: {e}")
        return False

def ignore_invitation(driver, invitation):
    """
    Ignore a LinkedIn invitation
    
    Args:
        driver: Selenium WebDriver instance
        invitation (dict): Invitation data containing component_key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        component_key = invitation.get('component_key', '')
        
        # Find the Ignore button using aria-label and component key
        ignore_button_xpath = f"//button[@componentkey and contains(@aria-label, 'Ignore') and contains(@aria-label, '{invitation.get('name', '')}')]"
        
        # Alternative: Find by button text
        if not component_key:
            ignore_button_xpath = "//button[.//span[text()='Ignore']]"
        
        try:
            ignore_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, ignore_button_xpath))
            )
            
            # Scroll to button and click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ignore_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", ignore_button)
            
            log_info(f"❌ Ignored invitation from {invitation.get('name', 'Unknown')}")
            time.sleep(2)  # Wait for action to complete
            return True
            
        except TimeoutException:
            log_error(f"Could not find Ignore button for {invitation.get('name', 'Unknown')}")
            return False
            
    except Exception as e:
        log_error(f"Error ignoring invitation: {e}")
        return False

def manage_invitations_interactive(invitations):
    """
    Interactively manage LinkedIn invitations one by one
    
    Args:
        invitations (list): List of invitation data dictionaries
    """
    if not invitations:
        log_warning("No invitations to manage")
        return
    
    load_dotenv()
    
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    
    if not linkedin_email or not linkedin_password:
        log_error("LinkedIn credentials not found in .env file")
        return
    
    driver = setup_driver()
    
    try:
        # Login to LinkedIn
        if not login_to_linkedin(driver, linkedin_email, linkedin_password):
            log_error("Failed to login to LinkedIn")
            return
        
        # Navigate to invitations page
        invitations_url = "https://www.linkedin.com/mynetwork/invitation-manager/received/"
        driver.get(invitations_url)
        time.sleep(5)  # Wait for page to load
        
        log_info(f"🎯 Starting interactive management of {len(invitations)} invitations")
        log_blank_line()
        
        accepted_count = 0
        ignored_count = 0
        skipped_count = 0
        
        for i, invitation in enumerate(invitations, 1):
            # Display invitation details
            display_invitation_details(invitation, i, len(invitations))
            
            # Ask user what to do
            log_info("What would you like to do?")
            log_info("1. Accept this invitation")
            log_info("2. Ignore this invitation")
            log_info("3. Skip (do nothing)")
            log_info("4. Exit invitation management")
            
            choice = get_user_choice(4)
            log_blank_line()
            
            if choice == "1":
                # Accept invitation
                if accept_invitation(driver, invitation):
                    accepted_count += 1
                else:
                    log_warning("Failed to accept invitation")
                    
            elif choice == "2":
                # Ignore invitation
                if ignore_invitation(driver, invitation):
                    ignored_count += 1
                else:
                    log_warning("Failed to ignore invitation")
                    
            elif choice == "3":
                # Skip
                log_info(f"⏭️ Skipped invitation from {invitation.get('name', 'Unknown')}")
                skipped_count += 1
                
            elif choice == "4":
                # Exit
                log_info("Exiting invitation management...")
                break
            
            # Add delay between actions to avoid rate limiting
            if choice in ["1", "2"]:
                log_info("⏳ Waiting before next action...")
                time.sleep(3)
        
        # Show summary
        log_blank_line(2)
        log_info("🎉 Invitation management completed!")
        log_info(f"📊 Summary:")
        log_info(f"   ✅ Accepted: {accepted_count}")
        log_info(f"   ❌ Ignored: {ignored_count}")
        log_info(f"   ⏭️ Skipped: {skipped_count}")
        log_info(f"   📝 Total processed: {accepted_count + ignored_count + skipped_count}")
        
    except KeyboardInterrupt:
        log_warning(1, "Invitation management interrupted by user")
        
    except Exception as e:
        log_error(f"Error during invitation management: {e}")
        logger.exception("Full error details:")
        
    finally:
        driver.quit()
        log_info("Browser closed")
        log_blank_line()

def batch_accept_all_invitations(invitations):
    """
    Accept all invitations in batch (future enhancement)
    
    Args:
        invitations (list): List of invitation data dictionaries
    """
    log_info("🚀 Batch accept functionality - Coming soon!")
    log_info("This feature will allow you to accept all invitations at once")
    # TODO: Implement batch acceptance logic

def batch_ignore_all_invitations(invitations):
    """
    Ignore all invitations in batch (future enhancement)
    
    Args:
        invitations (list): List of invitation data dictionaries
    """
    log_info("🚀 Batch ignore functionality - Coming soon!")
    log_info("This feature will allow you to ignore all invitations at once")
    # TODO: Implement batch ignore logic