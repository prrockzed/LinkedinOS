import re
import requests
import logging
from bs4 import BeautifulSoup
from validation import is_valid_linkedin_profile

logger = logging.getLogger(__name__)

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
    # Main function to extract all founder and company information
    logger.info(f"Extracting from: {company_url}")
    
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