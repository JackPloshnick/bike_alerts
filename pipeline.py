# imports
import logging
from functions import alert_logic, gsheets, pushover, strava_api
import pandas as pd
from dotenv import load_dotenv
import os

# ------------------- Setup Logging -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# ------------------- Load Environment -------------------
load_dotenv()
GOOGLE_SHEETS_URL_KEY = os.environ["GOOGLE_SHEETS_URL_KEY"]
PUSHOVER_USER_KEY = os.environ["PUSHOVER_USER_KEY"]
PUSHOVER_APP_TOKEN = os.environ["PUSHOVER_APP_TOKEN"]


logger.info("Environment variables loaded.")

# ------------------- Get Activities -------------------
try:
    logger.info("Reading existing activities from Google Sheets...")
    sheets_df = gsheets.read_from_gsheets("Activities", GOOGLE_SHEETS_URL_KEY)
    sheets_df["start_date_local"] = pd.to_datetime(sheets_df["start_date_local"])
    logger.info(f"Loaded {len(sheets_df)} existing activities.")

    last_date = sheets_df["start_date_local"].max()
    logger.info(f"Getting new activities since {last_date}...")
    new_activities = strava_api.get_activities_since_date(last_date)
    new_activities_df = strava_api.build_activities_dataframe(new_activities)
    logger.info(f"Retrieved {len(new_activities_df)} new activities.")

    # Combine and deduplicate
    combined_df = pd.concat([sheets_df, new_activities_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset="upload_id", keep="last")
    combined_df = combined_df.sort_values(by="upload_id").reset_index(drop=True)
    logger.info(
        f"Combined dataframe now has {len(combined_df)} rows after deduplication."
    )

    # Write back to Google Sheets
    gsheets.write_to_gsheets(combined_df, "Activities", GOOGLE_SHEETS_URL_KEY)
    logger.info("Updated Activities sheet successfully.")

except Exception as e:
    logger.exception(f"Error fetching or updating activities: {e}")

# ------------------- Get Form Responses -------------------
try:
    logger.info("Reading form responses from Google Sheets...")
    form_responses_df = gsheets.read_from_gsheets(
        "Form Responses", GOOGLE_SHEETS_URL_KEY
    )
    form_responses_df["datetime"] = pd.to_datetime(
        form_responses_df["Date of Action"] + " " + form_responses_df["Time of Action"],
        format="%m/%d/%Y %I:%M:%S %p",
    )
    logger.info(f"Loaded {len(form_responses_df)} form responses.")
except Exception as e:
    logger.exception(f"Error reading form responses: {e}")

# ------------------- Create Alert -------------------
try:
    logger.info("Checking for chain wax alert...")
    alert = alert_logic.wax_chain_alert(combined_df, form_responses_df, threshold=200)

    gsheets.append_alert_row(alert, GOOGLE_SHEETS_URL_KEY)
    logger.info(f"Alert row appended: {alert}")

    if alert["issue_alert"]:
        logger.info("Alert needed! Sending Pushover notification...")
        pushover.send_pushover_notification(
            "Chain Wax Alert",
            f"Wax Chain! Last chain wax: {alert['miles_since_last_action']:.1f} miles ago",
            PUSHOVER_APP_TOKEN,
            PUSHOVER_USER_KEY,
        )
        logger.info("Pushover notification sent.")
    else:
        logger.info("No issue alert. Only logging alert row.")

except Exception as e:
    logger.exception(f"Error creating or sending alert: {e}")

logger.info("Script finished.")
