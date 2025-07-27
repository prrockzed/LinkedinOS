from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Setup Chrome WebDriver with headless options"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver