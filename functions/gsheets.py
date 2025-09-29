# imports
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe


def write_to_gsheets(df, tab_name, GOOGLE_SHEETS_URL_KEY):
    gc = gspread.service_account("sheets_service_account.json")
    spreadsheet = gc.open_by_key(GOOGLE_SHEETS_URL_KEY)
    activities_worksheet = spreadsheet.worksheet(tab_name)
    set_with_dataframe(activities_worksheet, df)


def read_from_gsheets(tab_name, GOOGLE_SHEETS_URL_KEY):
    gc = gspread.service_account("sheets_service_account.json")
    spreadsheet = gc.open_by_key(GOOGLE_SHEETS_URL_KEY)
    activities_worksheet = spreadsheet.worksheet(tab_name)
    df = get_as_dataframe(activities_worksheet)
    return df


def append_alert_row(alert, GOOGLE_SHEETS_URL_KEY):
    gc = gspread.service_account("sheets_service_account.json")
    spreadsheet = gc.open_by_key(GOOGLE_SHEETS_URL_KEY)
    alerts_worksheet = spreadsheet.worksheet("Alerts")
    row = [
        bool(alert["issue_alert"]),
        str(alert["date"]),
        str(alert["action_type"]),
        int(alert["threshold"]),
        float(alert["miles_since_last_action"]),
    ]
    alerts_worksheet.append_row(row)
