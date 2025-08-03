import logging
from tools.blank_logger import log_blank_line

# Get the standard logger
logger = logging.getLogger(__name__)

def _parse_log_args(*args, **kwargs):
    """Helper function to parse logging arguments"""
    # Default values
    blank_lines_before = 0
    message = ""
    blank_lines_after = 0
    
    # Handle positional arguments
    if len(args) == 1:
        if isinstance(args[0], str):
            message = args[0]
        else:
            raise ValueError("Single argument must be a string message")
    elif len(args) == 2:
        if isinstance(args[0], int) and isinstance(args[1], str):
            blank_lines_before, message = args[0], args[1]
        elif isinstance(args[0], str) and isinstance(args[1], int):
            message, blank_lines_after = args[0], args[1]
        else:
            raise ValueError("For 2 arguments, expected (int, str) or (str, int)")
    elif len(args) == 3:
        if isinstance(args[0], int) and isinstance(args[1], str) and isinstance(args[2], int):
            blank_lines_before, message, blank_lines_after = args
        else:
            raise ValueError("For 3 arguments, expected (int, str, int)")
    elif len(args) > 3:
        raise ValueError("Maximum 3 positional arguments allowed")
    
    # Override with kwargs if provided
    blank_lines_before = kwargs.get("blank_lines_before", blank_lines_before)
    message = kwargs.get("message", message)
    blank_lines_after = kwargs.get("blank_lines_after", blank_lines_after)
    
    return blank_lines_before, message, blank_lines_after

def _log_message(log_func, *args, **kwargs):
    """Core logging function that handles all log types"""
    blank_lines_before, message, blank_lines_after = _parse_log_args(*args, **kwargs)
    
    if blank_lines_before > 0:
        log_blank_line(blank_lines_before)
    
    log_func(message)
    
    if blank_lines_after > 0:
        log_blank_line(blank_lines_after)

# Public logging functions
def log_info(*args, **kwargs):
    _log_message(logger.info, *args, **kwargs)

def log_warning(*args, **kwargs):
    _log_message(logger.warning, *args, **kwargs)

def log_error(*args, **kwargs):
    _log_message(logger.error, *args, **kwargs)