import logging

def setup_blank_logger():
    # Create a dedicated logger for blank lines
    blank_logger = logging.getLogger('blank_lines')
    blank_logger.propagate = False
    blank_logger.setLevel(logging.INFO)  # Set to INFO to ensure it passes
    
    # Add handler with empty formatter
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt=''))
    blank_logger.addHandler(handler)
    
    return blank_logger

blank_logger = setup_blank_logger()

def log_blank_line(count=1):
    """Log one or more blank lines.
    
    Args:
        count (int): Number of blank lines to log (default: 1)
    """
    if not isinstance(count, int) or count < 1:
        raise ValueError("Count must be a positive integer")
    
    for _ in range(count):
        blank_logger.info('')