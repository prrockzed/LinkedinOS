import time
from bs4 import BeautifulSoup
from web_driver import setup_driver

def get_yc_2025_links(y_combinator_url, y_combinator_batch):
    """Get all company links from Y Combinator batch page"""
    driver = setup_driver()
    try:
        driver.get(y_combinator_batch)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.find_all("a", href=True)
        company_links = [y_combinator_url + l["href"] for l in links if l["href"].startswith("/companies/")]
        return list(set(company_links))
    finally:
        driver.quit()