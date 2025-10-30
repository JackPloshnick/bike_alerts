# imports
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import json
import os
from dotenv import load_dotenv

load_dotenv()

service_string = os.environ["GOOGLE_SHEETS_SERVICE_ACCOUNT"]
service_dict = json.loads(service_string)
service_dict["private_key"] = service_dict["private_key"].replace("\\n", "\n")


def write_to_gsheets(df, tab_name, GOOGLE_SHEETS_URL_KEY):
    gc = gspread.service_account_from_dict(service_dict)
    spreadsheet = gc.open_by_key(GOOGLE_SHEETS_URL_KEY)
    activities_worksheet = spreadsheet.worksheet(tab_name)
    set_with_dataframe(activities_worksheet, df)


def read_from_gsheets(tab_name, GOOGLE_SHEETS_URL_KEY):
    gc = gspread.service_account_from_dict(service_dict)
    spreadsheet = gc.open_by_key(GOOGLE_SHEETS_URL_KEY)
    activities_worksheet = spreadsheet.worksheet(tab_name)
    df = get_as_dataframe(activities_worksheet)
    return df


def append_alerts_to_sheet(alert_df, GOOGLE_SHEETS_URL_KEY):
    """
    Append one row per maintenance alert to the 'Alerts' sheet.

    Parameters:
    - alert_df: DataFrame returned from maintenance_alert()
    - GOOGLE_SHEETS_URL_KEY: str, Google Sheets key (not full URL)
    """
    if alert_df is None or alert_df.empty:
        print("No alerts to append.")
        return

    gc = gspread.service_account_from_dict(service_dict)
    spreadsheet = gc.open_by_key(GOOGLE_SHEETS_URL_KEY)
    worksheet = spreadsheet.worksheet("Alerts")

    rows_to_append = []
    for _, alert in alert_df.iterrows():
        row = [
            bool(alert.get("issue_alert", False)),
            str(alert.get("date", "")),
            str(alert.get("action_type", "")),
            str(alert.get("miles_threshold", "")),   # can be None
            float(alert.get("miles_since_last_action", 0.0)),
            str(alert.get("days_threshold", "")),    # can be None
            int(alert.get("days_since_last_action", 0)),
        ]
        rows_to_append.append(row)

    # Append all rows at once for efficiency
    worksheet.append_rows(rows_to_append, value_input_option="USER_ENTERED")
    print(f"Appended {len(rows_to_append)} alert(s) to Google Sheet.")

