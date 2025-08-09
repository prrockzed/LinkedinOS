import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException,
)

from tools.info_logger import log_error, log_info, log_warning

def check_already_connected(driver):
    """Check if already connected via More button dropdown"""
    try:
        # First check if there's a "More" button
        more_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(@class, 'artdeco-dropdown__trigger') and .//span[text()='More']]"))
        )
        
        # Click the More button to expand dropdown
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", more_button)
        log_info("🔘 More button clicked to expand menu")
        time.sleep(1)  # Wait for dropdown to appear
        
        # Look for "Remove connection" option in dropdown
        try:
            remove_connection_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH,
                    "//span[contains(@class, 'display-flex') and contains(@class, 't-normal') and contains(@class, 'flex-1') and (@aria-hidden='true' or not(@aria-hidden)) and (text()='Remove connection' or contains(text(), 'Remove'))]"))
            )
            
            # Check if aria-hidden is True (as mentioned in requirements)
            aria_hidden = remove_connection_element.get_attribute('aria-hidden')
            if aria_hidden == 'true' or remove_connection_element.is_displayed():
                log_info("✅ Already connected to this person")
                # Click somewhere else to close the dropdown
                driver.execute_script("document.body.click();")
                time.sleep(0.5)
                return True
                
        except TimeoutException:
            # Not connected, dropdown should still be open
            pass
            
    except TimeoutException:
        # No More button found
        pass
    except Exception as e:
        log_error(f"Error checking connection status via More button: {e}")
    
    return False

def check_pending_connection(driver):
    """Check if connection is in pending state"""
    try:
        # Look for pending button - not in More dropdown, directly on page
        pending_span = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH,
                "//span[contains(@class, 'artdeco-button__text') and (text()='Pending' or contains(text(), 'Pending'))]"))
        )
        
        # Get the parent button element and check its classes
        parent_button = pending_span.find_element(By.XPATH, "./..")
        parent_classes = set(parent_button.get_attribute("class").split())
        
        # Check for required parent classes
        required_classes = {"artdeco-button", "artdeco-button--2", "artdeco-button--secondary", "ember-view"}
        
        if required_classes.issubset(parent_classes):
            log_info("⏳ Connection is in Pending state")
            return True
            
    except TimeoutException:
        # No pending button found
        pass
    except Exception as e:
        log_error(f"Error checking pending connection: {e}")
    
    return False

def check_email_required_dialog(driver):
    """Check if email verification dialog appeared after clicking connect"""
    try:
        # Look for the email verification dialog
        email_label = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH,
                "//label[@for='email' or contains(text(), 'To verify this member knows you') or contains(text(), 'please enter their email')]"))
        )
        
        # Additional check for the specific text content
        label_text = email_label.get_attribute('textContent') or email_label.text
        if "To verify this member knows you" in label_text and "please enter their email" in label_text:
            log_info("📧 Email verification required for connection")
            
            # Close the dialog by clicking cancel or outside
            try:
                # Try to find and click cancel/close button
                cancel_button = driver.find_element(By.XPATH, 
                    "//button[contains(@class, 'artdeco-button') and (.//span[text()='Cancel' or text()='Close'] or @aria-label='Dismiss')]")
                driver.execute_script("arguments[0].click();", cancel_button)
                time.sleep(1)
            except:
                # If no cancel button, click outside the modal
                driver.execute_script("document.body.click();")
                time.sleep(1)
                
            return True
            
    except TimeoutException:
        # No email dialog found
        pass
    except Exception as e:
        log_error(f"Error checking email requirement: {e}")
    
    return False

def find_connect_button(driver):
    """Find and return the Connect button if available"""
    connect_button = None
    
    # First try to find Connect button in More dropdown (if dropdown is open)
    try:
        # Check if dropdown is open and has Connect button
        connect_button = driver.find_element(By.XPATH,
            "//div[contains(@class, 'artdeco-dropdown__content')]//span[contains(@class, 'display-flex') and contains(@class, 't-normal') and contains(@class, 'flex-1') and text()='Connect']")
        log_info("Found Connect button in More dropdown (content container)")
        return connect_button.find_element(By.XPATH, "./ancestor::*[contains(@class, 'artdeco-dropdown__item')]")
    except NoSuchElementException:
        try:
            connect_button = driver.find_element(By.XPATH,
                "//div[contains(@class, 'artdeco-dropdown__item') and contains(@class, 'artdeco-dropdown__item--is-dropdown')]//span[contains(@class, 'display-flex') and contains(@class, 't-normal') and contains(@class, 'flex-1') and text()='Connect']")
            log_info("Found Connect button in More dropdown (item container)")
            return connect_button.find_element(By.XPATH, "./ancestor::button")
        except NoSuchElementException:
            pass
    
    # If not in dropdown, look for direct Connect button
    try:
        connect_span = driver.find_element(By.XPATH,
            "//span[contains(@class, 'artdeco-button__text') and text()='Connect']")
        
        # Get the parent button element
        parent_button = connect_span.find_element(By.XPATH, "./..")
        
        # Get parent classes as a set for easier checking
        parent_classes = set(parent_button.get_attribute("class").split())
        
        # Required base classes that must be present
        required_base_classes = {"artdeco-button", "artdeco-button--2", "ember-view"}
        
        # Must have either primary OR secondary (but not both typically)
        button_style_classes = {"artdeco-button--primary", "artdeco-button--secondary"}
        
        # Classes that should NOT be present
        excluded_classes = {"artdeco-button--muted"}
        
        # Check if all required base classes are present
        if not all(cls in parent_classes for cls in required_base_classes):
            log_info("⚠️ Connect button parent missing required base classes - skipping")
            return None
        
        # Check if at least one of the button style classes is present
        if not any(cls in parent_classes for cls in button_style_classes):
            log_info("⚠️ Connect button parent missing primary/secondary style class - skipping")
            return None
            
        # Check if any excluded classes are present
        if any(cls in parent_classes for cls in excluded_classes):
            log_info("⚠️ Connect button parent has excluded class (muted) - skipping")
            return None
            
        log_info(f"✅ Valid Connect button found with classes: {parent_classes}")
        return parent_button
            
    except NoSuchElementException:
        pass
    
    return None

def send_connection_request(driver):
    """
    Enhanced function to send connection request with comprehensive status detection
    Returns tuple: (success: bool, status: str)
    Status can be: 'Connection Sent', 'Already Connected', 'Pending state', 'Email wanted', 'Doesn\'t want to connect'
    """
    
    # Step 1: Check if already connected
    if check_already_connected(driver):
        return False, "Already Connected"
    
    # Step 2: Check if connection is pending
    if check_pending_connection(driver):
        return False, "Pending state"
    
    # Step 3: Look for Connect button
    connect_button = find_connect_button(driver)
    
    if not connect_button:
        log_warning("⚠️ No connect button found and not connected/pending")
        return False, "Doesn't want to connect"
    
    # Step 4: Click the Connect button
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", connect_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", connect_button)
        log_info("🔘 Connect button clicked")
        
        # Step 5: Check if email is required
        if check_email_required_dialog(driver):
            return False, "Email wanted"
        
        # Step 6: Handle "Send without note" dialog if it appears
        try:
            send_button = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//span[text()='Send without a note']/ancestor::button[contains(@class, 'artdeco-button')]"))
            )
            driver.execute_script("arguments[0].click();", send_button)
            log_info("✅ Connection sent (without note)")
            return True, "Connection Sent"
            
        except TimeoutException:
            # No "Send without note" dialog appeared, connection might have been sent directly
            log_info("✅ Connection sent (no confirmation dialog)")
            return True, "Connection Sent"
            
    except Exception as e:
        log_error(f"❌ Error clicking connect button: {str(e)}")
        return False, "Failed to connect"

# Legacy function for backward compatibility
def send_connection_request_legacy(driver):
    """Legacy function that returns only boolean for backward compatibility"""
    success, status = send_connection_request(driver)
    return success