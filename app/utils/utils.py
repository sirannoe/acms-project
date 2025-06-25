def generate_key_stats(total_patients=0, completion_rate=0, monthly_visits=0, sms_engagement=0):
    """
    Helper function to build the key statistics dictionary for dashboard display.
    
    Args:
        total_patients (int): Total number of registered patients.
        completion_rate (float): Completion rate percentage (0-100).
        monthly_visits (int): Number of patient visits in the current month.
        sms_engagement (int): Number of SMS messages sent or responded to.
    
    Returns:
        dict: Dictionary with keys for template rendering.
    """
    return {
        "total_patients": total_patients,
        "completion_rate": round(completion_rate, 1),  # rounded to 1 decimal place
        "monthly_visits": monthly_visits,
        "sms_engagement": sms_engagement,
    }
