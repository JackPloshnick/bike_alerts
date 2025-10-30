import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.thresholds import thresholds


def maintenance_alert(combined_df, form_responses_df, gear_id="b14816258"):
    """
    Check all maintenance thresholds (miles/days) for a given bike and create alerts if due.

    Parameters:
    - combined_df: DataFrame with bike activities ('type', 'gear_id', 'start_date_local', 'distance_miles')
    - form_responses_df: DataFrame with maintenance actions ('Action', 'datetime')
    - gear_id: str, the gear_id for the bike

    Returns:
    - alert_df: DataFrame with one row per maintenance type, including `issue_alert` flag.
    """
    if combined_df.empty or form_responses_df.empty:
        return pd.DataFrame()  # Return empty DF for consistent type

    # Ensure timezones are consistent
    combined_df = combined_df.copy()
    combined_df["start_date_local"] = combined_df["start_date_local"].dt.tz_convert("America/New_York")

    eastern_time = datetime.now(ZoneInfo("America/New_York"))
    alerts = []

    for key, cfg in thresholds.items():
        response_label = cfg["response_test"]
        miles_thresh = cfg.get("miles")
        days_thresh = cfg.get("days")

        # Get most recent maintenance date
        last_action_date = form_responses_df.loc[
            form_responses_df["Action"] == response_label, "datetime"
        ].max()

        if pd.isna(last_action_date):
            # No previous record — assume never done
            last_action_dt = pd.Timestamp.min.tz_localize("America/New_York")
        else:
            last_action_dt = pd.to_datetime(last_action_date).tz_localize("America/New_York")

        # Filter rides since last action
        rides_df = combined_df[
            (combined_df["type"].isin(["Ride", "VirtualRide"]))
            & (combined_df["gear_id"] == gear_id)
            & (combined_df["start_date_local"] > last_action_dt)
        ]

        total_miles = rides_df["distance_miles"].sum()
        days_since = (eastern_time - last_action_dt).days

        # Check thresholds
        miles_due = miles_thresh is not None and total_miles >= miles_thresh
        days_due = days_thresh is not None and days_since >= days_thresh
        issue_alert = miles_due or days_due

        alerts.append({
            "issue_alert": issue_alert,
            "date": eastern_time.strftime("%Y-%m-%d %H:%M:%S"),
            "action_type": response_label,
            "miles_threshold": miles_thresh,
            "days_threshold": days_thresh,
            "miles_since_last_action": total_miles,
            "days_since_last_action": days_since,
        })

    return pd.DataFrame(alerts)

