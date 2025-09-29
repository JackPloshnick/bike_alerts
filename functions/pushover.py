import requests


def send_pushover_notification(title, message, PUSHOVER_APP_TOKEN, PUSHOVER_USER_KEY):
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message,
    }
    response = requests.post("https://api.pushover.net/1/messages.json", data=data)
    if response.status_code == 200:
        print("Notification sent!")
    else:
        print("Failed to send notification:", response.text)
