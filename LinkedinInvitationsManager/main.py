import logging
import os
import sys
from tools.blank_logger import log_blank_line
from tools.get_user_choice import get_user_choice
from tools.info_logger import log_info, log_warning, log_error
from invitations_scraper import scrape_received_invitations
from invitations_manager import manage_invitations_interactive

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

def main():
    log_info(1, "=== LinkedIn Invitations Manager ===", 1)
    
    try:
        # Step 1: Scrape received invitations
        log_info("Fetching your received connection invitations...")
        invitations = scrape_received_invitations()
        
        if not invitations:
            log_warning("No pending invitations found or failed to fetch invitations.")
            log_info("This could mean:")
            log_info("• You have no pending connection requests")
            log_info("• LinkedIn login failed")
            log_info("• Page structure has changed")
            return
        
        # Step 2: Show summary
        log_blank_line()
        log_info(f"📨 Found {len(invitations)} pending connection requests!")
        log_blank_line()
        
        # Step 3: Ask if user wants to review them
        log_info("Would you like to review each invitation individually?")
        log_info("1. Yes, review each invitation")
        log_info("2. No, go back to main menu")
        
        choice = get_user_choice(2)
        
        if choice == "1":
            # Step 4: Interactive management
            manage_invitations_interactive(invitations)
        else:
            log_info("Returning to main menu...")
            
    except KeyboardInterrupt:
        log_warning(1, "Operation cancelled by user")
    except Exception as e:
        log_error(f"An error occurred: {e}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    main()