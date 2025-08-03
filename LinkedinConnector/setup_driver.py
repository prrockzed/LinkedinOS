import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

def setup_driver():
    # Setup and return Chrome WebDriver with appropriate options
    options = webdriver.ChromeOptions()
    
    # Get absolute path for chrome profile
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chrome_profile_path = os.path.join(project_root, "chrome_profile")
    
    # Create chrome profile directory if it doesn't exist
    if not os.path.exists(chrome_profile_path):
        os.makedirs(chrome_profile_path)
        logger.info(f"Created chrome profile directory: {chrome_profile_path}")
    
    # To persist session and avoid frequent logins
    options.add_argument(f"--user-data-dir={chrome_profile_path}")
    
    # Recommended options for stability
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver