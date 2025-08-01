import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

def setup_driver():
    # Setup and return Chrome WebDriver with appropriate options
    logger.info("setting up webdriver")
    options = webdriver.ChromeOptions()
    
    # To persist session and avoid frequent logins
    options.add_argument("--user-data-dir=./chrome_profile")
    
    # Recommended options for stability
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver