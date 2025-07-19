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

def extract_founder_name_from_yc_page(soup, linkedin_url):
    """Extract founder name from YC website content"""
    # Try to find name near LinkedIn links
    all_links = soup.find_all("a", href=True)
    for link in all_links:
        if linkedin_url in link.get("href", ""):
            # Look for name in nearby elements
            parent = link.parent
            if parent:
                # Check siblings and parent text
                siblings = parent.find_all(text=True)
                for sibling in siblings:
                    text = sibling.strip()
                    if text and len(text) > 1 and not any(x in text.lower() for x in ['linkedin', 'http', 'www', 'profile']):
                        # Check if it looks like a name (contains letters and possibly spaces)
                        if re.match(r'^[A-Za-z\s\-\.]+$', text) and len(text) < 50:
                            return text
            
            # Check previous and next siblings of the link
            if link.previous_sibling:
                prev_text = str(link.previous_sibling).strip()
                if prev_text and len(prev_text) > 1 and re.match(r'^[A-Za-z\s\-\.]+$', prev_text) and len(prev_text) < 50:
                    return prev_text
            
            if link.next_sibling:
                next_text = str(link.next_sibling).strip()
                if next_text and len(next_text) > 1 and re.match(r'^[A-Za-z\s\-\.]+$', next_text) and len(next_text) < 50:
                    return next_text
    
    # Fallback: try to extract from common patterns around founder sections
    founder_sections = soup.find_all(['h2', 'h3', 'h4', 'div', 'span'], string=re.compile(r'founder|team|people', re.IGNORECASE))
    for section in founder_sections:
        next_elements = section.find_next_siblings()
        for element in next_elements[:3]:  # Check next 3 siblings
            if element and element.find("a", href=lambda x: x and linkedin_url in x):
                text_content = element.get_text().strip()
                # Extract potential names using regex
                names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text_content)
                for name in names:
                    if len(name) > 2 and len(name) < 50:
                        return name
    
    # Final fallback: look for any text that looks like a name near the LinkedIn URL
    page_text = soup.get_text()
    if linkedin_url in page_text:
        # Try to find names in the vicinity of the LinkedIn URL
        linkedin_index = page_text.find(linkedin_url)
        if linkedin_index != -1:
            # Look 200 characters before and after the LinkedIn URL
            context = page_text[max(0, linkedin_index - 200):linkedin_index + 200]
            names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b', context)
            for name in names:
                if len(name) > 2 and len(name) < 50 and not any(x in name.lower() for x in ['linkedin', 'http', 'www', 'profile', 'company']):
                    return name
    
    return "Unknown"

def extract_company_details(soup):
    """Extract additional company details from YC website"""
    details = {
        'about': '',
        'website': '',
        'team_size': '',
        'founding_year': ''
    }
    
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
    
    # Extract website - look for external links
    all_links = soup.find_all('a', href=True)
    for link in all_links:
        href = link.get('href', '').lower()
        if (href.startswith('http') and 
            'ycombinator.com' not in href and 
            'linkedin.com' not in href and
            'twitter.com' not in href and
            'github.com' not in href):
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

    # Extract company details (about, website, team size, founding year)
    company_details = extract_company_details(soup)
    
    # Extract company LinkedIn URL
    company_linkedin = ""
    links = soup.find_all("a", href=True)
    for link in links:
        href = link.get("href", "").lower()
        if "linkedin.com/company/" in href:
            company_linkedin = link.get("href")
            break

    # Find all LinkedIn profile links
    people_section = soup.find_all("a", href=True)
    founders_data = []

    for link in people_section:
        href = link.get("href")
        if href and is_valid_linkedin_profile(href):
            # Extract founder name from YC website content
            founder_name = extract_founder_name_from_yc_page(soup, href)
            founders_data.append({
                'company_name': company_name,
                'founder_name': founder_name,
                'linkedin_url': href,
                'company_linkedin': company_linkedin,
                'company_url': company_url,
                'about': company_details['about'],
                'website': company_details['website'],
                'team_size': company_details['team_size'],
                'founding_year': company_details['founding_year']
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
    headers = ["Company Name", "Founder Name", "LinkedIn URL", "Company LinkedIn", 
               "Company URL", "About Company", "Website", "Team Size", "Founding Year"]
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
