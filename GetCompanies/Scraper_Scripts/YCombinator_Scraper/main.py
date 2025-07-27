import time
from settings import Config
from google_sheets import GoogleSheetsManager
from yc_scraper import get_yc_2025_links
from company_extractor import extract_founders
from data_formatter import format_data_for_sheet

def main():
    try:
        # Load configuration
        config = Config()
        print(f"Using Google Sheet URL from .env: {config.spreadsheet_url}\n")
        
        # Setup Google Sheets
        sheets_manager = GoogleSheetsManager(config.credentials_path)
        sheet = sheets_manager.setup_sheet(config.spreadsheet_url)
        sheets_manager.write_headers(sheet)
        
        # Get YC company links
        print("\nStarting YC company scraping...")
        yc_links = get_yc_2025_links(config.y_combinator_url, config.y_combinator_batch)
        print(f"Found {len(yc_links)} company links")
        
        # Extract data from each company
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
        
        # Format and write data to sheet
        formatted_rows = format_data_for_sheet(all_founders_data)
        sheets_manager.write_data_to_sheet(sheet, formatted_rows)
        
        print("Scraping completed!")
        
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
