import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

def login_to_linkedin(driver, email, password):
    """Log in to LinkedIn if not already logged in"""
    driver.get("https://www.linkedin.com/login")
    logger.info("Trying to log in to linkedin")
    
    # Check if already logged in by looking for feed element
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".scaffold-finite-scroll__content"))
        )
        
        logger.info("Already logged in to LinkedIn")
        return True
    
    except TimeoutException as e:
        logger.error(f"Timed out when trying to log in. Error is: {e}")
        
    except Exception as e:
        logger.error(f"Could not log in directly. Error is: {e}")
    
    
    # Logging via filling up email and password
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
        logging.critical("Login Failed. Error is: ", e)
        return False