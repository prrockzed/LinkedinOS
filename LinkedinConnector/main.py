import logging
from process_profiles import process_profiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

if __name__ == "__main__":
    process_profiles()