# imports 
import requests
import pandas as pd
import time
from datetime import datetime
from dotenv import load_dotenv
import os

#get secrets from .env
load_dotenv(".env")
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

# Get access token. Must be done every session
def get_strava_access_token():
    resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "refresh_token": STRAVA_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_activities_since_date(start_date_local):
    """
    Fetch all Strava activities since a given date.
    
    Parameters:
        start_date_local (str or datetime): The start date. Can be a string in 'YYYY-MM-DD' format or a datetime object.
        
    Returns:
        List of activity dictionaries.
    """
    access_token = get_strava_access_token()
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}

    # Convert start_date_local to datetime if string
    if isinstance(start_date_local, str):
        start_date_local = datetime.strptime(start_date_local, "%Y-%m-%d")
    
    # Convert to epoch seconds
    after_timestamp = int(start_date_local.timestamp())

    page = 1
    all_activities = []

    while True:
        params = {
            "after": after_timestamp,  # only activities after this timestamp
            "per_page": 200,           # max allowed
            "page": page
        }
        r = requests.get(activities_url, headers=headers, params=params)
        r.raise_for_status()
        activities = r.json()

        if not activities:  # stop when no more results
            break

        all_activities.extend(activities)
        page += 1
        time.sleep(0.2)  # avoid hitting API too fast

    return all_activities

# turn activties strava api activities response into a dataframe
def build_activities_dataframe(activities):
    df = pd.json_normalize(activities)
    
    if df.empty:
        return df  # do nothing if empty
    
    # add human-readable units
    df["distance_miles"] = df["distance"] / 1609.34
    df["moving_time_min"] = df["moving_time"] / 60
    df["elapsed_time_min"] = df["elapsed_time"] / 60
    df["average_speed_mph"] = df["average_speed"] * 2.23694
    df["max_speed_mph"] = df["max_speed"] * 2.23694

    #change types of date fields 
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    
    return df