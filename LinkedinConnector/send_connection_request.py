import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException,
)

def send_connection_request(driver):
    """Send connection request to LinkedIn profile"""
    # Try both variants of Connect button
    connect_button = None
    
    # Variant 1: Handle potential "More" button dropdown first
    try:
        # First check if there's a "More" button
        more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(@class, 'artdeco-dropdown__trigger') and .//span[text()='More']]"))
        )
        print("Found the more button")
        
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
            
    except TimeoutException:
        print("More Section could not be found")
    
    # Variant 2: <span class="artdeco-button__text">Connect</span> (with parent class check)
    if not connect_button:
        try:
            connect_span = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                    "//span[contains(@class, 'artdeco-button__text') and text()='Connect']"))
            )
            
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
                print("⚠️ Connect button parent missing required base classes - skipping")
                return False
            
            # Check if at least one of the button style classes is present
            if not any(cls in parent_classes for cls in button_style_classes):
                print("⚠️ Connect button parent missing primary/secondary style class - skipping")
                return False
                
            # Check if any excluded classes are present
            if any(cls in parent_classes for cls in excluded_classes):
                print("⚠️ Connect button parent has excluded class (muted) - skipping")
                return False
                
            connect_button = parent_button
            print(f"✅ Valid Connect button found with classes: {parent_classes}")
                
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