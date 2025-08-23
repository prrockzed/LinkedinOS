import random
import numpy as np

def human_like_delay(base_time=10, variance=5, min_time=3, max_time=30):
    """Generate human-like delays using normal distribution"""
    delay = np.random.normal(base_time, variance)
    return max(min_time, min(max_time, delay))

def variable_delay_between_actions():
    """Different delays for different action types"""
    action_delays = {
        'page_load': lambda: human_like_delay(8, 3, 5, 15),
        'scroll': lambda: human_like_delay(2, 1, 1, 4),
        'click': lambda: human_like_delay(3, 1, 1, 8),
        'between_profiles': lambda: human_like_delay(45, 15, 20, 120),  # Much longer
        'after_connection': lambda: human_like_delay(180, 60, 120, 300)  # 2-5 minutes
    }
    return action_delays