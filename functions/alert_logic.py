import pandas as pd
from datetime import datetime

def miles_since_date_check(combined_df, date, threshold=100):
    """
    Check if total distance since a given date exceeds a threshold.

    Parameters:
    - combined_df: DataFrame with 'start_date_local' and 'distance_miles' columns
    - date: str or datetime, the date from which to sum distances
    - threshold: float, the number of miles to check against (default 100)

    Returns:
    - dict with:
        'exceeds_threshold': True/False
        'total_miles': float, total miles since given date
    """
    
    # Convert input date to UTC
    date_utc = pd.to_datetime(date)
    if date_utc.tzinfo is None:
        date_utc = date_utc.tz_localize('UTC')
    
    # Filter rows after the given date
    filtered_df = combined_df[combined_df['start_date_local'] > date_utc]
    
    # Sum distances
    total_miles = filtered_df['distance_miles'].sum()
    
    # Return dictionary
    return {
        'exceeds_threshold': total_miles >= threshold,
        'total_miles': total_miles
    }


def wax_chain_alert(combined_df, form_responses_df, gear_id='b14816258', threshold=5):
    """
    Check if miles since last 'Wax chain' action exceed a threshold and create an alert DataFrame.

    Parameters:
    - combined_df: DataFrame with bike activities, must have 'type', 'gear_id', 'start_date_local', 'distance_miles'
    - form_responses_df: DataFrame with previous actions, must have 'Action' and 'Date of Action'
    - gear_id: str, bike gear_id to filter rides
    - threshold: float, number of miles since last action to trigger alert

    Returns:
    - alert_df: DataFrame with alert info if threshold exceeded, else None
    """
    # Make a copy to avoid SettingWithCopyWarning
    combined_df = combined_df.copy()
    
    # Filter for rides on the specific bike
    rides_df = combined_df[(combined_df["type"].isin(["Ride", "VirtualRide"])) & (combined_df['gear_id'] == gear_id)]
    
    if rides_df.empty or form_responses_df.empty:
        return None
    
    # Get the date of the last 'Wax chain' action
    last_wax_date = form_responses_df.loc[form_responses_df['Action'] == 'Wax chain', 'datetime'].max()
    
    if pd.isna(last_wax_date):
        return None  # No previous wax action to compare
    
    # Check miles since last wax
    rides_since_last_wax = rides_df[rides_df['start_date_local'] > pd.to_datetime(last_wax_date, utc=True)]
    total_miles = rides_since_last_wax['distance_miles'].sum()

    return {
        'issue_alert': total_miles >= threshold,
        'date': datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
        'action_type': 'Wax chain',
        'threshold': threshold,
        'miles_since_last_action': total_miles
    }

