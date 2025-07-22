# How to Run This Project on a New Machine

This guide walks you through setting up the **LinkedinPro** project from scratch on any computer.

---

## 1. Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/yourusername/LinkedinPro.git
cd LinkedinPro
```

---

## 2. Install Python

Make sure Python 3.8+ is installed:

```bash
python3 --version
```

If it's not installed, you can install it from [python.org](https://www.python.org/downloads/) or via your system’s package manager:

* **macOS:** `brew install python`
* **Ubuntu/Debian:** `sudo apt install python3 python3-venv`
* **Windows:** Use the official Python installer.

---

## 3. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: venv\Scripts\activate
```

---

## 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` doesn't exist, create it with the following content:

```txt
requests
beautifulsoup4
selenium
gspread
oauth2client
python-dotenv
webdriver-manager
```

Then run `pip install -r requirements.txt`.

---

## 5. Set Up Google Sheets API

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project.
3. Enable **Google Sheets API**.
4. Go to **"Credentials"** → Click **"Create Credentials"** → Choose **"Service Account"**.
5. Set a name (e.g., `sheets-api-bot`) → Click **Continue**.
6. Assign the role: **Project → Editor** → Click **Continue → Done**.

### Step 2: Download credentials.json

1. Click the created service account.
2. Go to **"Keys"** tab.
3. Click **"Add Key"** → **"Create new key"** → Choose **JSON** → Download it.
4. Save this file as `credentials.json` in the project folder.

### Step 3: Share Google Sheet

1. Open your Google Sheet.
2. Click **"Share"**.
3. Paste the service account email (found inside `credentials.json`).
4. Give **Editor access**.

---

## 6. How to Get `your_spreadsheet_id` for `.env`

1. Open your Google Sheet in the browser.
2. Look at the URL — it will look something like this:

```
https://docs.google.com/spreadsheets/d/**1A2B3C4D5E6F7G8H9I0J**/edit#gid=0
```

3. The part between `/d/` and `/edit` is your **spreadsheet ID**.

4. Use the full URL in your `.env` file like this:

```env
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/1A2B3C4D5E6F7G8H9I0J/edit#gid=0
```

---

## 7. Create a `.env` File

In the project root directory, create a `.env` file and add:

```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/{your_spreadsheet_id}/edit#gid=0
Y_COMBINATOR_URL=https://www.ycombinator.com
Y_COMBINATOR_BATCH=https://www.ycombinator.com/companies?batch=Summer%202025
```

---

## 8. Run the Y Combinator Scraper

This script extracts company and founder data into the Google Sheet.

```bash
python yc_founders.py
```

---

## 9. Run the LinkedIn Connector

This script reads founder LinkedIn URLs from the sheet and sends connection requests.

```bash
python linkedin_connector.py
```

The first time you run it, Chrome will open and ask for login and it will fill out automatically(with the given details in the .env file). The session is saved in `./chrome_profile` for future runs.

---

## Notes

* Be patient; scripts are rate-limited to avoid LinkedIn bans.
* Make sure your `.env` file and `credentials.json` are correct.
* You can stop the script with `Ctrl+C`.

---

## Troubleshooting

* **Sheet not writing?** Make sure the shared email has **editor** access.
* **Chrome crashing?** Update Chrome and ChromeDriver (`pip install --upgrade webdriver-manager`).
* **Too many requests?** LinkedIn may temporarily restrict you. Slow down your runs.

---

## You're Ready 🎉

Once the above steps are done, you’re all set to automate scraping + connection requests using **LinkedinPro**.
