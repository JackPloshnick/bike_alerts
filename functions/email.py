import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_notification(alert_df, sender_email, sender_password, recipient_email):
    """
    Send an email notification summarizing maintenance alerts.

    Parameters:
    - alert_df: DataFrame from maintenance_alert()
    - sender_email: str, your Gmail address
    - sender_password: str, Gmail App Password
    - recipient_email: str, who to send to
    """

    if alert_df is None or alert_df.empty:
        print("No maintenance alerts to send.")
        return

    # -------- Build the email content --------
    subject = "Bike Maintenance Needed!"

    # Build plain text body
    lines = []
    for _, alert in alert_df.iterrows():
        action = alert.get("action_type", "Unknown action")
        miles_thresh = alert.get("miles_threshold", "")
        days_thresh = alert.get("days_threshold", "")
        miles_since = alert.get("miles_since_last_action", 0)
        days_since = alert.get("days_since_last_action", 0)

        lines.append(
            f"• {action}: \n"
            f"  Miles since last: {miles_since:.1f} (threshold: {miles_thresh or 'N/A'})\n"
            f"  Days since last: {days_since} (threshold: {days_thresh or 'N/A'})\n"
        )

    body = (
        "The following maintenance actions are due:\n\n"
        + "\n".join(lines)
    )

    # -------- Compose email --------
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # -------- Send email --------
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Maintenance email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

