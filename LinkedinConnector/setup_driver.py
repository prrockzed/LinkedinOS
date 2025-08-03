import logging
import os
from selenium import webdriver

logger = logging.getLogger(__name__)

def setup_driver():
    """Setup and return Chrome WebDriver with appropriate options"""
    options = webdriver.ChromeOptions()
    
    # Get absolute path for chrome profile
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chrome_profile_path = os.path.join(project_root, "chrome_profile")
    
    # Create chrome profile directory if it doesn't exist
    if not os.path.exists(chrome_profile_path):
        os.makedirs(chrome_profile_path)
        logger.info(f"Created chrome profile directory: {chrome_profile_path}")
    
    logger.info(f"Using chrome profile path: {chrome_profile_path}")
    
    # Chrome profile options - use profile-directory for better session persistence
    options.add_argument(f"--user-data-dir={chrome_profile_path}")
    options.add_argument("--profile-directory=Default")
    
    # Additional options for better stability and profile handling
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-extensions-file-access-check")
    options.add_argument("--disable-extensions-http-throttling")
    
    # Recommended options for stability
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    try:
        # Simple approach - let Selenium handle ChromeDriver automatically
        driver = webdriver.Chrome(options=options)
        
        # Execute script to hide automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("WebDriver setup completed successfully")
        return driver
        
    except Exception as e:
        logger.error(f"Error setting up WebDriver: {e}")
        raise