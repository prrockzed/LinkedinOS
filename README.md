# LinkedinPro

LinkedinPro is a two-part Python automation tool designed to:

1. **Scrape founder and company details** from Y Combinator’s Summer 2025 batch website.
2. **Send LinkedIn connection requests** to scraped founders using Selenium.

It extracts structured data (company name, founder name, LinkedIn profile, website, team size, founding year, etc.) and stores it directly in a Google Sheet. Then, it can log in to LinkedIn and send personalized connection requests to the listed founders.

---

## Features

- Scrape data from [Y Combinator companies list](https://www.ycombinator.com/companies?batch=Summer%202025)
- Extract founder names, personal LinkedIn profiles, and company metadata
- Save all data to Google Sheets
- Automatically send LinkedIn connection requests using your credentials

---

## File Structure

```text
LinkedinPro/
│
├── yc_founders.py             # Scrapes Y Combinator data to Google Sheet
├── linkedin_connector.py      # Sends LinkedIn connection requests
├── credentials.json           # Google Sheets API credentials (DO NOT SHARE)
├── .env                       # Configuration variables (email, password, URLs)
├── requirements.txt           # Python dependencies
└── README.md                  # Project overview and setup instructions
```
