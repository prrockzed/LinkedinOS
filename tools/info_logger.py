import logging
from tools.blank_logger import log_blank_line

# Get the standard logger
logger = logging.getLogger(__name__)

def log_info(message, blank_lines_after=0):
    """Log an info message and optionally add blank line(s) after it.
    
    Args:
        message (str): The message to log
        blank_lines_after (int): Number of blank lines to add after the message (default: 0)
                                - 0: Just log the message (equivalent to logger.info())
                                - 1: Log message + 1 blank line (equivalent to logger.info() + log_blank_line())
                                - 2: Log message + 2 blank lines (equivalent to logger.info() + 2x log_blank_line())
    """
    if not isinstance(message, str):
        raise ValueError("Message must be a string")
    
    if not isinstance(blank_lines_after, int) or blank_lines_after < 0:
        raise ValueError("blank_lines_after must be a non-negative integer")
    
    # Log the info message
    logger.info(message)
    
    # Add blank line(s) after the message
    if blank_lines_after > 0:
        log_blank_line(blank_lines_after)

def log_warning(message, blank_lines_after=0):
    """Log a warning message and optionally add blank line(s) after it.
    
    Args:
        message (str): The message to log
        blank_lines_after (int): Number of blank lines to add after the message (default: 0)
                                - 0: Just log the message (equivalent to logger.warning())
                                - 1: Log message + 1 blank line (equivalent to logger.warning() + log_blank_line())
                                - 2: Log message + 2 blank lines (equivalent to logger.warning() + 2x log_blank_line())
    """
    if not isinstance(message, str):
        raise ValueError("Message must be a string")
    
    if not isinstance(blank_lines_after, int) or blank_lines_after < 0:
        raise ValueError("blank_lines_after must be a non-negative integer")
    
    # Log the warning message
    logger.warning(message)
    
    # Add blank line(s) after the message
    if blank_lines_after > 0:
        log_blank_line(blank_lines_after)

def log_error(message, blank_lines_after=0):
    """Log an error message and optionally add blank line(s) after it.
    
    Args:
        message (str): The message to log
        blank_lines_after (int): Number of blank lines to add after the message (default: 0)
                               - 0: Just log the message (equivalent to logger.error())
                               - 1: Log message + 1 blank line (equivalent to logger.error() + log_blank_line())
                               - 2: Log message + 2 blank lines (equivalent to logger.error() + 2x log_blank_line())
    """
    if not isinstance(message, str):
        raise ValueError("Message must be a string")
    
    if not isinstance(blank_lines_after, int) or blank_lines_after < 0:
        raise ValueError("blank_lines_after must be a non-negative integer")
    
    # Log the error message
    logger.error(message)
    
    # Add blank line(s) after the message
    if blank_lines_after > 0:
        log_blank_line(blank_lines_after)