import requests
import json
import os
import smtplib
import pandas as pd
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SENDER = "bharatsariya369@gmail.com"
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_RECIPIENT = "bharatsariya369@gmail.com"

SCAN_TYPE = os.environ.get("SCAN_TYPE", "morning")
DATA_FILE = "morning_data.json"

def get_nse_volume_data():

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    }

    session.get(
        "https://www.nseindia.com/",
        headers=headers,
        timeout=30
    )

    response = session.get(
        "https://www.nseindia.com/api/live-analysis-volume-gainers",
        headers=headers,
        timeout=30
    )

    data = response.json()

    results = {}

    for stock in data["data"]:

        symbol = stock.get("symbol")

        volume = (
            stock.get("todayVolume")
            or stock.get("volume")
            or 0
        )

        if symbol and volume:
            results[symbol] = volume

    return results


def send_email(df):

    html = df.to_html(index=False)

    msg = MIMEMultipart("alternative")

    msg["Subject"] = "NSE Volume Growth Report"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    body = f"""
    <html>
    <body>
    <h2>NSE Volume Growth Report</h2>
    {html}
    </body>
    </html>
    """

    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(
            EMAIL_SENDER,
            EMAIL_RECIPIENT,
            msg.as_string()
        )

    print("Email sent")


if SCAN_TYPE == "morning":

    morning_data = get_nse_volume_data()

    with open(DATA_FILE, "w") as f:
        json.dump(morning_data, f)

    print("Morning data saved")


else:

    try:
        with open(DATA_FILE, "r") as f:
            morning_data = json.load(f)

    except Exception:
        print("Morning data not found")
        exit()

    evening_data = get_nse_volume_data()

    rows = []

    common = (
        set(morning_data.keys())
        & set(evening_data.keys())
    )

    for symbol in common:

        morning_volume = morning_data[symbol]
        evening_volume = evening_data[symbol]

        if morning_volume <= 0:
            continue

        growth = (
            (evening_volume - morning_volume)
            / morning_volume
        ) * 100

        if growth > 0:

            rows.append({
                "Symbol": symbol,
                "10AM Volume": morning_volume,
                "3PM Volume": evening_volume,
                "Growth %": round(growth, 2)
            })

    df = pd.DataFrame(rows)

    if len(df) == 0:
        print("No stocks found")
        exit()

    df = df.sort_values(
        "Growth %",
        ascending=False
    )

    df.to_excel(
        "volume_growth_report.xlsx",
        index=False
    )

    send_email(df)

    print(df.head(20))
