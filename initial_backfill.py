# only run this if a full backfill is needed for some reason

from functions import gsheets, strava_api
import os

GOOGLE_SHEETS_URL_KEY = os.getenv("GOOGLE_SHEETS_URL_KEY")


all_activities = strava_api.get_activities_since_date("2024-01-01")
all_activities_df = strava_api.build_activities_dataframe(all_activities)
gsheets.write_to_gsheets(all_activities_df, "Activities", GOOGLE_SHEETS_URL_KEY)
