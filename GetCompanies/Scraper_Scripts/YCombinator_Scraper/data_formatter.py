def format_data_for_sheet(all_founders_data):
    """Format data according to requirements: group by company, show company info only once"""
    # Group by company
    companies = {}
    for founder in all_founders_data:
        company_name = founder['company_name']
        if company_name not in companies:
            companies[company_name] = []
        companies[company_name].append(founder)
    
    # Sort companies alphabetically
    sorted_companies = sorted(companies.items())
    
    formatted_rows = []
    for company_name, founders in sorted_companies:
        for i, founder in enumerate(founders):
            if i == 0:  # First founder of the company
                row = [
                    company_name,
                    founder['founder_name'],
                    founder['linkedin_url'],
                    founder['company_linkedin'],
                    founder['company_url'],
                    founder['about'],
                    founder['website'],
                    founder['team_size'],
                    founder['founding_year']
                ]
            else:  # Subsequent founders
                row = [
                    "",  # Empty company name
                    founder['founder_name'],
                    founder['linkedin_url'],
                    "",  # Empty company LinkedIn
                    "",  # Empty company URL
                    "",  # Empty about
                    "",  # Empty website
                    "",  # Empty team size
                    ""   # Empty founding year
                ]
            formatted_rows.append(row)
    
    return formatted_rows