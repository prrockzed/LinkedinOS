import logging
import os
import sys
from tools.blank_logger import log_blank_line
from batch_selector import get_linkedin_batch_selection
from process_profiles import process_profiles_with_file

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
    logger.info("LinkedIn Connection Campaign Starting!")
    log_blank_line()
    
    # Get user's batch selection
    batch_selection = get_linkedin_batch_selection()
    
    if not batch_selection:
        logger.info("Connection campaign cancelled. Exiting...")
        return
    
    # Process profiles with the selected file
    logger.info(f"Starting connections for {batch_selection['season']} {batch_selection['year']}")
    log_blank_line()
    
    process_profiles_with_file(batch_selection['file_path'])
    log_blank_line()

if __name__ == "__main__":
    main()