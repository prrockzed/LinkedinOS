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
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1LarZd_WShGMbrNk2znA9ZjTKksp8nE6223Vudo9p0Qw/edit?gid=5128251#gid=5128251'
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

def extract_founders_info(soup):
    """Extract founders information from the company page"""
    founders = []
    
    # Find all founder sections (divs with min-w-0 flex-1 class)
    founder_sections = soup.find_all('div', class_='min-w-0 flex-1')
    
    for section in founder_sections:
        # Extract founder name from text-xl font-bold div
        name_element = section.find('div', class_='text-xl font-bold')
        if not name_element:
            continue
            
        founder_name = name_element.get_text(strip=True)
        
        # Find LinkedIn URL in this section
        linkedin_url = None
        social_links = section.find_all('a', href=True)
        for link in social_links:
            href = link.get('href', '')
            if is_valid_linkedin_profile(href):
                linkedin_url = href
                break
        
        if founder_name and linkedin_url:
            founders.append({
                'name': founder_name,
                'linkedin_url': linkedin_url
            })
    
    return founders

def extract_company_details(soup):
    """Extract additional company details from YC website"""
    details = {
        'name': '',
        'about': '',
        'website': '',
        'team_size': '',
        'founding_year': ''
    }
    
    # Extract company name
    name_element = soup.find('h1')
    if name_element:
        details['name'] = name_element.get_text(strip=True).replace(" | Y Combinator", "")
    
    # Extract company description/about
    about_selectors = [
        'div.prose div.text-xl',
        'div[class*="prose"] div[class*="text-xl"]',
        'div.description',
        'p.description',
        '.company-description',
        'div[class*="description"]'
    ]
    
    for selector in about_selectors:
        about_element = soup.select_one(selector)
        if about_element:
            details['about'] = about_element.get_text().strip()
            break
    
    # If no specific about section found, try meta description
    if not details['about']:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            details['about'] = meta_desc.get('content', '').strip()
    
    # Extract website - look for specific pattern with link icon
    website_element = soup.find('a', class_='mb-2 whitespace-nowrap md:mb-0')
    if website_element and website_element.find('svg') and 'href' in website_element.attrs:
        details['website'] = website_element['href']
    
    # If not found with specific class, try alternative approach
    if not details['website']:
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '').lower()
            if (href.startswith('http') and 
                'ycombinator.com' not in href and 
                'linkedin.com' not in href and
                'twitter.com' not in href and
                'github.com' not in href and
                'facebook.com' not in href and
                'startupschool.org' not in href):
                # This is likely the company website
                details['website'] = link.get('href')
                break
    
    # Extract team size - look for patterns like "Team size: X" or "X employees"
    page_text = soup.get_text()
    team_patterns = [
        r'team size[:\s]*(\d+)',
        r'(\d+)\s*(?:employee|people|team member)',
        r'founded.*?(\d+)\s*(?:employee|people)',
        r'team[:\s]*(\d+)',
    ]
    
    for pattern in team_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            details['team_size'] = match.group(1)
            break
    
    # Extract founding year - look for patterns like "Founded in YYYY" or "YYYY"
    year_patterns = [
        r'founded.*?(\d{4})',
        r'since\s*(\d{4})',
        r'established.*?(\d{4})',
        r'\b(20\d{2})\b'  # Years from 2000-2099
    ]
    
    for pattern in year_patterns:
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        if matches:
            # Get the most recent reasonable year
            years = [int(year) for year in matches if 2000 <= int(year) <= 2025]
            if years:
                details['founding_year'] = str(min(years))  # Usually the founding year is the earliest
                break
    
    return details

def extract_company_linkedin(soup):
    """Extract company LinkedIn URL"""
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '').lower()
        if 'linkedin.com/company/' in href:
            return link.get('href')
    return ''

def extract_founders(company_url):
    print(f"Extracting from: {company_url}")
    
    try:
        response = requests.get(company_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {company_url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract company details
    company_details = extract_company_details(soup)
    company_linkedin = extract_company_linkedin(soup)
    
    # Extract founders information
    founders_info = extract_founders_info(soup)
    
    if not founders_info:
        return None
    
    # Prepare founders data
    founders_data = []
    for founder in founders_info:
        founders_data.append({
            'company_name': company_details['name'],
            'founder_name': founder['name'],
            'linkedin_url': founder['linkedin_url'],
            'company_linkedin': company_linkedin,
            'company_url': company_url,
            'about': company_details['about'],
            'website': company_details['website'],
            'team_size': company_details['team_size'],
            'founding_year': company_details['founding_year']
        })
    
    return founders_data

def format_data_for_sheet(all_founders_data):
    """Format data according to requirements: group by company, show company info only once"""
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
                    founder['company_url'],
                    founder['about'],
                    founder['website'],
                    founder['team_size'],
                    founder['founding_year']
                ]
            else:  # Subsequent founders
                row = [
                    "",  # Empty company name
                    founder['founder_name'],
                    founder['linkedin_url'],
                    "",  # Empty company LinkedIn
                    "",  # Empty company URL
                    "",  # Empty about
                    "",  # Empty website
                    "",  # Empty team size
                    ""   # Empty founding year
                ]
            formatted_rows.append(row)
    
    return formatted_rows

def main():
    print("Starting YC company scraping...")
    
    sheet = setup_gsheet()
    sheet.clear()
    
    # Updated headers with new columns
    headers = ["Company Name", "Founders' Name", "Founders' LinkedIn URL", "Company's LinkedIn URL", 
               "Company's YC URL", "About Company", "Company's Website", "Team Size", "Founding Year"]
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
