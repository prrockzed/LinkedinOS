import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re


# Google Sheet setup
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1LarZd_WShGMbrNk2znA9ZjTKksp8nE6223Vudo9p0Qw/edit#gid=0'
SPREADSHEET_ID = SPREADSHEET_URL.split('/')[5]

def setup_gsheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def get_yc_2025_links():
    url = "https://www.ycombinator.com/companies?batch=Summer%202025"
    driver = setup_driver()
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = soup.find_all("a", href=True)
    company_links = ["https://www.ycombinator.com" + l["href"] for l in links if l["href"].startswith("/companies/")]
    driver.quit()
    return list(set(company_links))

def is_valid_linkedin_profile(url):
    """Check if LinkedIn URL is a valid personal profile"""
    if not url or "linkedin.com" not in url:
        return False
    
    # Exclude school, company, and Y Combinator URLs
    excluded_patterns = [
        "linkedin.com/school/",
        "linkedin.com/company/",
        "linkedin.com/school/y-combinator",
        "linkedin.com/company/y-combinator"
    ]
    
    for pattern in excluded_patterns:
        if pattern in url.lower():
            return False
    
    # Only include personal profiles (linkedin.com/in/)
    if "linkedin.com/in/" in url:
        return True
    
    return False

def extract_company_linkedin(soup, company_name):
    """Extract company LinkedIn URL"""
    links = soup.find_all("a", href=True)
    for link in links:
        href = link.get("href", "").lower()
        if "linkedin.com/company/" in href:
            return link.get("href")
    return ""

def extract_founder_name_from_link(link):
    """Extract founder name from the link text or surrounding elements"""
    # Try to get name from link text
    name = link.text.strip()
    if name and len(name) > 1 and not name.lower() in ['linkedin', 'profile', 'view']:
        return name
    
    # Try to get name from parent elements
    parent = link.parent
    if parent:
        parent_text = parent.text.strip()
        # Clean up common patterns
        parent_text = re.sub(r'LinkedIn.*', '', parent_text, flags=re.IGNORECASE)
        parent_text = parent_text.strip()
        if parent_text and len(parent_text) > 1:
            return parent_text
    
    return "Unknown"

def extract_founders(company_url):
    print(f"Extracting from: {company_url}")
    
    try:
        response = requests.get(company_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {company_url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    try:
        # Try multiple selectors for company name
        name_element = soup.find("h1")
        if not name_element:
            name_element = soup.find("title")
        
        company_name = name_element.text.strip() if name_element else "Unknown"
        # Clean up company name
        company_name = company_name.replace(" | Y Combinator", "").strip()
    except:
        company_name = "Unknown"

    # Extract company LinkedIn URL
    company_linkedin = extract_company_linkedin(soup, company_name)

    # Find all LinkedIn profile links
    people_section = soup.find_all("a", href=True)
    founders_data = []

    for link in people_section:
        href = link.get("href")
        if href and is_valid_linkedin_profile(href):
            # Extract founder name
            founder_name = extract_founder_name_from_link(link)
            founders_data.append({
                'company_name': company_name,
                'founder_name': founder_name,
                'linkedin_url': href,
                'company_linkedin': company_linkedin,
                'company_url': company_url
            })

    # Remove duplicates based on LinkedIn URL
    unique_founders = []
    seen_urls = set()
    
    for founder in founders_data:
        if founder['linkedin_url'] not in seen_urls:
            unique_founders.append(founder)
            seen_urls.add(founder['linkedin_url'])

    return unique_founders if unique_founders else None

def format_data_for_sheet(all_founders_data):
    """Format data according to requirements: group by company, show company name and URL only once"""
    # Group by company
    companies = {}
    for founder in all_founders_data:
        company_name = founder['company_name']
        if company_name not in companies:
            companies[company_name] = []
        companies[company_name].append(founder)
    
    # Sort companies alphabetically
    sorted_companies = sorted(companies.items())
    
    formatted_rows = []
    for company_name, founders in sorted_companies:
        for i, founder in enumerate(founders):
            if i == 0:  # First founder of the company
                row = [
                    company_name,
                    founder['founder_name'],
                    founder['linkedin_url'],
                    founder['company_linkedin'],
                    founder['company_url']
                ]
            else:  # Subsequent founders
                row = [
                    "",  # Empty company name
                    founder['founder_name'],
                    founder['linkedin_url'],
                    "",  # Empty company LinkedIn
                    ""   # Empty company URL
                ]
            formatted_rows.append(row)
    
    return formatted_rows

def main():
    print("Starting YC company scraping...")
    
    sheet = setup_gsheet()
    sheet.clear()
    
    # Updated headers
    headers = ["Company Name", "Founder Name", "LinkedIn URL", "Company LinkedIn", "Company URL"]
    sheet.append_row(headers)
    
    yc_links = get_yc_2025_links()
    print(f"Found {len(yc_links)} company links")
    
    all_founders_data = []

    for i, link in enumerate(yc_links, 1):
        print(f"Processing {i}/{len(yc_links)}: {link}")
        try:
            founders = extract_founders(link)
            if founders:
                all_founders_data.extend(founders)
                print(f"  Found {len(founders)} founders")
            else:
                print(f"  No founders found")
        except Exception as e:
            print(f"  Error processing {link}: {e}")
        
        # Add delay to avoid rate limiting
        time.sleep(2)

    print(f"\nTotal founders found: {len(all_founders_data)}")
    
    # Format data for sheet
    formatted_rows = format_data_for_sheet(all_founders_data)
    
    # Write to sheet
    print("Writing to Google Sheet...")
    for i, row in enumerate(formatted_rows, 1):
        try:
            sheet.append_row(row)
            if i % 10 == 0:
                print(f"  Written {i}/{len(formatted_rows)} rows")
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"Error writing row {i}: {e}")

    print("Scraping completed!")

if __name__ == "__main__":
    main()
