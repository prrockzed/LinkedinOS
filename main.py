import subprocess
import sys
import os
import logging
from tools.blank_logger import log_blank_line
from tools.get_user_choice import get_user_choice
from tools.info_logger import log_info, log_error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

def run_linkedin_connector():
    # Run the LinkedinConnector/main.py script
    log_info("Calling LinkedinConnector")
    try:
        # Set PYTHONPATH to include current directory
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        subprocess.run([sys.executable, "LinkedinConnector/main.py"], 
                        check=True, env=env, cwd=os.getcwd())
    except subprocess.CalledProcessError as e:
        log_error(f"LinkedinConnector failed: {e}")
    log_blank_line()

def run_ycombinator_scraper():
    # Run the YCombinator scraper script
    log_info("Calling YCombinator Scraper method")
    try:
        # Set PYTHONPATH to include current directory and change working directory
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        subprocess.run([sys.executable, "GetCompanies/Scraper_Scripts/YCombinator_Scraper/main.py"], 
                        check=True, env=env, cwd=os.getcwd())
    except subprocess.CalledProcessError as e:
        log_error(f"YCombinator scraper failed: {e}")
    log_blank_line()

def show_menu():
    # Display the menu options
    log_info(1, "===== LinkedinOS Menu =====", 1)
    log_info("1. Run YCombinator Scraper")
    log_info("2. Run LinkedinConnector")
    log_info("3. Exit (and set the code free)", 1)

def main():
    log_info(1, "========== LinkedinOS ==========", 1)
    
    while True:
        show_menu()
        choice = get_user_choice()
        log_blank_line()
        
        if choice == "1":
            run_ycombinator_scraper()
        elif choice == "2":
            run_linkedin_connector()
        else:
            log_info("Exiting LinkedinOS...")
            log_info("Goodbye! 👋", 1)
            break


if __name__ == "__main__":
    main()