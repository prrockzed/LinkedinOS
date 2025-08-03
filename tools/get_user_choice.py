import logging
from tools.blank_logger import log_blank_line

def get_user_choice(total_choice_number: int):
    """Get user input on the same line as the logger.info message"""
    # Get the current time for consistent formatting
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Print the log-style message without newline
    print(f"{timestamp} | INFO | Enter your choice (1-{total_choice_number}): ", end="", flush=True)
    
    # Get user input
    choice = input().strip()
    
    log_blank_line()
    return choice