import logging
from tools.blank_logger import log_blank_line
from process_profiles import process_profiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("The party is just getting started. Enjoy!")
    log_blank_line()

    process_profiles()
    log_blank_line()