def is_valid_linkedin_profile(url):
    """Check if LinkedIn URL is a valid personal profile"""
    if not url or "linkedin.com" not in url:
        return False
    
    # Exclude school, company, and Y Combinator URLs
    excluded_patterns = [
        "linkedin.com/school/",
        "linkedin.com/company/",
        "linkedin.com/school/y-combinator",
        "linkedin.com/company/y-combinator"
    ]
    
    for pattern in excluded_patterns:
        if pattern in url.lower():
            return False
    
    # Only include personal profiles (linkedin.com/in/)
    if "linkedin.com/in/" in url:
        return True
    
    return False