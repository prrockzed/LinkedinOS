import logging
import subprocess
import sys
import os

from tools.blank_logger import log_blank_line
from tools.get_user_choice import get_user_choice

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

def run_linkedin_connector():
    # Run the LinkedinConnector/main.py script
    logger.info("Calling LinkedinConnector")
    try:
        # Set PYTHONPATH to include current directory
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        subprocess.run([sys.executable, "LinkedinConnector/main.py"], 
                        check=True, env=env, cwd=os.getcwd())
    except subprocess.CalledProcessError as e:
        logger.error(f"LinkedinConnector failed: {e}")
    log_blank_line()

def run_ycombinator_scraper():
    # Run the YCombinator scraper script
    logger.info("Calling YCombinator Scraper method")
    try:
        # Set PYTHONPATH to include current directory and change working directory
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        subprocess.run([sys.executable, "GetCompanies/Scraper_Scripts/YCombinator_Scraper/main.py"], 
                        check=True, env=env, cwd=os.getcwd())
    except subprocess.CalledProcessError as e:
        logger.error(f"YCombinator scraper failed: {e}")
    log_blank_line()

def show_menu():
    # Display the menu options
    log_blank_line()
    logger.info("===== LinkedinOS Menu =====")
    log_blank_line()
    logger.info("1. Run LinkedinConnector")
    logger.info("2. Run YCombinator Scraper")
    logger.info("3. Exit (and set the code free)")
    log_blank_line()

def main():
    log_blank_line()
    logger.info("========== LinkedinOS ==========")
    log_blank_line()
    
    while True:
        show_menu()
        choice = get_user_choice()
        log_blank_line()
        
        if choice == "1":
            run_linkedin_connector()
        elif choice == "2":
            run_ycombinator_scraper()
        else:
            logger.info("Exiting LinkedinOS...")
            logger.info("Goodbye! 👋")
            log_blank_line()
            break


if __name__ == "__main__":
    main()