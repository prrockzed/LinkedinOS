import time
import logging
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from web_driver import setup_driver

logger = logging.getLogger(__name__)

def scroll_and_load_all_companies(driver, max_scrolls=50, scroll_pause_time=3):
    """
    Scroll down the page multiple times to load all companies via infinite scroll
    
    Args:
        driver: Selenium WebDriver instance
        max_scrolls: Maximum number of scroll attempts to prevent infinite loops
        scroll_pause_time: Time to wait between scrolls for content to load
    
    Returns:
        bool: True if scrolling completed successfully
    """
    logger.info("Starting infinite scroll to load all companies...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    companies_count = 0
    scroll_count = 0
    no_change_count = 0  # Track consecutive scrolls with no new content
    
    while scroll_count < max_scrolls:
        # Get current number of company links before scrolling
        current_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/companies/']")
        current_count = len(current_links)
        
        logger.info(f"Scroll {scroll_count + 1}: Found {current_count} companies so far")
        
        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new content to load
        time.sleep(scroll_pause_time)
        
        # Check if new content was loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        new_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/companies/']")
        new_count = len(new_links)
        
        # Check for progress
        if new_count > current_count:
            logger.info(f"Loaded {new_count - current_count} more companies")
            no_change_count = 0  # Reset counter
            companies_count = new_count
        else:
            no_change_count += 1
            logger.info(f"No new companies loaded (attempt {no_change_count})")
        
        # If no new content for several attempts, we might be done
        if no_change_count >= 3:
            logger.info("No new content loading after multiple attempts")
            
            # Try one more aggressive scroll approach
            logger.info("Trying alternative scroll method...")
            driver.execute_script("window.scrollTo(0, 0);")  # Go to top
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Go to bottom
            time.sleep(scroll_pause_time * 2)  # Wait longer
            
            # Check one more time
            final_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/companies/']")
            final_count = len(final_links)
            
            if final_count > companies_count:
                logger.info(f"Found {final_count - companies_count} more companies with alternative method")
                companies_count = final_count
                no_change_count = 0  # Reset and continue
            else:
                logger.info(f"Finished loading. Total companies found: {companies_count}")
                break
        
        # If page height hasn't changed and no new links, we're likely done
        if new_height == last_height and new_count == current_count:
            # Try waiting a bit more in case content is still loading
            logger.info("Page height unchanged, waiting longer...")
            time.sleep(scroll_pause_time * 2)
            
            # Check one more time
            newer_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/companies/']")
            if len(newer_links) == new_count:
                logger.info(f"Finished loading. Total companies found: {len(newer_links)}")
                break
        
        last_height = new_height
        scroll_count += 1
        
        # Progressive pause - wait longer as we scroll more
        if scroll_count % 10 == 0:
            logger.info(f"Completed {scroll_count} scrolls, taking a longer break...")
            time.sleep(scroll_pause_time * 2)
    
    if scroll_count >= max_scrolls:
        logger.warning(f"Reached maximum scroll limit ({max_scrolls}). Some companies might be missed.")
    
    # Final count
    final_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/companies/']")
    logger.info(f"Scrolling completed! Total companies found: {len(final_links)}")
    
    return True

def is_valid_company_link(href, base_url):
    """
    Check if the href is a valid company link that should be processed
    
    Args:
        href: The href attribute from the link
        base_url: The base Y Combinator URL
        
    Returns:
        bool: True if it's a valid company link, False otherwise
    """
    if not href.startswith("/companies/"):
        return False
        
    if href == "/companies/":  # Root companies page
        return False
        
    # Extract company identifier from href
    company_identifier = href.replace("/companies/", "")
    
    # List of non-company pages that should be excluded
    excluded_pages = {
        "founders",  # Generic founders page
        "search",    # Search page
        "filter",    # Filter page
        "batch",     # Batch listing page
        "directory", # Directory page
        "about",     # About page
        "jobs",      # Jobs page
        "news",      # News page
        "blog",      # Blog page
        "apply",     # Apply page
    }
    
    # Check if it's in the excluded list
    if company_identifier.lower() in excluded_pages:
        return False
        
    # Additional checks for patterns that aren't companies
    if "/" in company_identifier:  # URLs with additional path segments are likely not companies
        return False
        
    if company_identifier.startswith("?"):  # Query parameters
        return False
        
    if len(company_identifier) < 2:  # Very short identifiers are suspicious
        return False
        
    # If all checks pass, it's likely a valid company
    return True

def get_yc_2025_links(y_combinator_url, y_combinator_batch):
    """Get all company links from Y Combinator batch page with infinite scroll support"""
    logger.info(f"Fetching companies from: {y_combinator_batch}")
    
    driver = setup_driver()
    try:
        # Navigate to the batch page
        driver.get(y_combinator_batch)
        logger.info("Page loaded, waiting for initial content...")
        time.sleep(5)  # Wait for initial page load
        
        # Wait for the page to load properly
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/companies/']"))
            )
            logger.info("Initial company links detected")
        except TimeoutException:
            logger.error("No company links found on the page. Check if the URL is correct.")
            return []
        
        # Get initial count
        initial_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/companies/']")
        logger.info(f"Initial companies loaded: {len(initial_links)}")
        
        # Scroll and load all companies
        scroll_success = scroll_and_load_all_companies(driver)
        
        if not scroll_success:
            logger.warning("Scrolling encountered issues, but continuing with available data...")
        
        # Get the final page source and parse
        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.find_all("a", href=True)
        
        # Filter company links and build full URLs
        company_links = []
        excluded_count = 0
        
        for link in links:
            href = link.get("href", "")
            
            # Check if it's a valid company link
            if is_valid_company_link(href, y_combinator_url):
                full_url = y_combinator_url + href
                company_links.append(full_url)
            elif href.startswith("/companies/") and href != "/companies/":
                # Log excluded links for debugging
                company_identifier = href.replace("/companies/", "")
                if excluded_count == 0:  # Only log the first few exclusions to avoid spam
                    logger.info(f"Excluded non-company link: {company_identifier}")
                excluded_count += 1
        
        if excluded_count > 0:
            logger.info(f"Excluded {excluded_count} non-company links (like 'founders', search pages, etc.)")
        
        # Remove duplicates while preserving order
        unique_links = []
        seen = set()
        for link in company_links:
            if link not in seen:
                unique_links.append(link)
                seen.add(link)
        
        logger.info(f"Final unique company links extracted: {len(unique_links)}")
        
        # Log some example links for verification
        if unique_links:
            logger.info("Sample company links:")
            for i, link in enumerate(unique_links[:5], 1):
                company_name = link.split('/')[-1]
                logger.info(f"  {i}. {company_name}")
            if len(unique_links) > 5:
                logger.info(f"  ... and {len(unique_links) - 5} more")
        
        return unique_links
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return []
    finally:
        driver.quit()
        logger.info("Browser closed")