import logging
from tools.blank_logger import log_blank_line

# Get the standard logger
logger = logging.getLogger(__name__)

def log_info(*args, **kwargs):
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
            blank_lines_before = args[0]
            message = args[1]
        elif isinstance(args[0], str) and isinstance(args[1], int):
            message = args[0]
            blank_lines_after = args[1]
        else:
            raise ValueError("For 2 arguments, expected (int, str) or (str, int)")
    elif len(args) == 3:
        if isinstance(args[0], int) and isinstance(args[1], str) and isinstance(args[2], int):
            blank_lines_before = args[0]
            message = args[1]
            blank_lines_after = args[2]
        else:
            raise ValueError("For 3 arguments, expected (int, str, int)")
    elif len(args) > 3:
        raise ValueError("Maximum 3 positional arguments allowed")
    
    # Override with kwargs if provided
    if "blank_lines_before" in kwargs:
        blank_lines_before = kwargs["blank_lines_before"]
    if "message" in kwargs:
        message = kwargs["message"]
    if "blank_lines_after" in kwargs:
        blank_lines_after = kwargs["blank_lines_after"]
    
    # Validate
    if not isinstance(message, str):
        raise ValueError("Message must be a string")
    if not isinstance(blank_lines_before, int) or blank_lines_before < 0:
        raise ValueError("blank_lines_before must be a non-negative integer")
    if not isinstance(blank_lines_after, int) or blank_lines_after < 0:
        raise ValueError("blank_lines_after must be a non-negative integer")
    
    # Log blank lines before (if any)
    if blank_lines_before > 0:
        log_blank_line(blank_lines_before)
    
    # Log the message (without any automatic formatting)
    logger.info(message)
    
    # Log blank lines after (if any)
    if blank_lines_after > 0:
        log_blank_line(blank_lines_after)

def log_warning(*args, **kwargs):
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
            blank_lines_before = args[0]
            message = args[1]
        elif isinstance(args[0], str) and isinstance(args[1], int):
            message = args[0]
            blank_lines_after = args[1]
        else:
            raise ValueError("For 2 arguments, expected (int, str) or (str, int)")
    elif len(args) == 3:
        if isinstance(args[0], int) and isinstance(args[1], str) and isinstance(args[2], int):
            blank_lines_before = args[0]
            message = args[1]
            blank_lines_after = args[2]
        else:
            raise ValueError("For 3 arguments, expected (int, str, int)")
    elif len(args) > 3:
        raise ValueError("Maximum 3 positional arguments allowed")
    
    # Override with kwargs if provided
    if "blank_lines_before" in kwargs:
        blank_lines_before = kwargs["blank_lines_before"]
    if "message" in kwargs:
        message = kwargs["message"]
    if "blank_lines_after" in kwargs:
        blank_lines_after = kwargs["blank_lines_after"]
    
    # Validate
    if not isinstance(message, str):
        raise ValueError("Message must be a string")
    if not isinstance(blank_lines_before, int) or blank_lines_before < 0:
        raise ValueError("blank_lines_before must be a non-negative integer")
    if not isinstance(blank_lines_after, int) or blank_lines_after < 0:
        raise ValueError("blank_lines_after must be a non-negative integer")
    
    # Log blank lines before (if any)
    if blank_lines_before > 0:
        log_blank_line(blank_lines_before)
    
    # Log the message (without any automatic formatting)
    logger.warning(message)
    
    # Log blank lines after (if any)
    if blank_lines_after > 0:
        log_blank_line(blank_lines_after)

def log_error(*args, **kwargs):
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
            blank_lines_before = args[0]
            message = args[1]
        elif isinstance(args[0], str) and isinstance(args[1], int):
            message = args[0]
            blank_lines_after = args[1]
        else:
            raise ValueError("For 2 arguments, expected (int, str) or (str, int)")
    elif len(args) == 3:
        if isinstance(args[0], int) and isinstance(args[1], str) and isinstance(args[2], int):
            blank_lines_before = args[0]
            message = args[1]
            blank_lines_after = args[2]
        else:
            raise ValueError("For 3 arguments, expected (int, str, int)")
    elif len(args) > 3:
        raise ValueError("Maximum 3 positional arguments allowed")
    
    # Override with kwargs if provided
    if "blank_lines_before" in kwargs:
        blank_lines_before = kwargs["blank_lines_before"]
    if "message" in kwargs:
        message = kwargs["message"]
    if "blank_lines_after" in kwargs:
        blank_lines_after = kwargs["blank_lines_after"]
    
    # Validate
    if not isinstance(message, str):
        raise ValueError("Message must be a string")
    if not isinstance(blank_lines_before, int) or blank_lines_before < 0:
        raise ValueError("blank_lines_before must be a non-negative integer")
    if not isinstance(blank_lines_after, int) or blank_lines_after < 0:
        raise ValueError("blank_lines_after must be a non-negative integer")
    
    # Log blank lines before (if any)
    if blank_lines_before > 0:
        log_blank_line(blank_lines_before)
    
    # Log the message (without any automatic formatting)
    logger.error(message)
    
    # Log blank lines after (if any)
    if blank_lines_after > 0:
        log_blank_line(blank_lines_after)
        