import requests
import json
import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SENDER = "bharatsariya369@gmail.com"
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_RECIPIENT = "bharatsariya369@gmail.com"

SCAN_TYPE = os.environ.get("SCAN_TYPE", "morning")
DATA_FILE = "morning_data_v2.json"

NSE_URL = "https://www.nseindia.com/api/live-analysis-volume-gainers"


def get_nse_data():
def get_stock_quote(symbol):

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

    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"

    response = session.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return {
        "symbol": symbol,
        "volume": data["securityWiseDP"]["quantityTraded"],
        "price": data["priceInfo"]["lastPrice"]
    }

def send_email(df):

    html = f"""
    <html>
    <body>
        <h2>NSE Volume Gainers Report</h2>
        {df.to_html(index=False)}
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")

    msg["Subject"] = "NSE Volume Difference Report"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:

        server.login(
            EMAIL_SENDER,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_SENDER,
            EMAIL_RECIPIENT,
            msg.as_string()
        )

    print("Email sent successfully")


# ---------------- MORNING ---------------- #

if SCAN_TYPE == "morning":

    print("Running MORNING scan...")

    stocks = get_nse_data()

    morning_data = {}

    for stock in stocks:

        morning_data[stock["symbol"]] = {
            "volume": stock["volume"],
            "price": stock["price"]
        }

    with open(DATA_FILE, "w") as f:
        json.dump(morning_data, f)

    print(f"Morning data saved ({len(morning_data)} stocks)")


# ---------------- EVENING ---------------- #

else:

    print("Running EVENING scan...")

    try:

        with open(DATA_FILE, "r") as f:
            morning_data = json.load(f)

        print("Morning symbols:")
        print(list(morning_data.keys()))

    except Exception as e:

        print("Morning data not found")
        print(e)
        exit()

    evening_lookup = {}

    for symbol in morning_data.keys():

    try:
        evening_lookup[symbol] = get_stock_quote(symbol)

    except Exception as e:
        print(f"Failed: {symbol}")
        print(e)

    evening_lookup = {}

    for stock in evening_stocks:
        evening_lookup[stock["symbol"]] = stock

    print("Evening symbols:")
    print(list(evening_lookup.keys()))

    print("Morning count:", len(morning_data))
    print("Evening count:", len(evening_lookup))

    rows = []

    for symbol, morning in morning_data.items():

        if symbol not in evening_lookup:
            continue

        evening = evening_lookup[symbol]

        morning_volume = morning["volume"]
        evening_volume = evening["volume"]

        morning_price = morning["price"]
        evening_price = evening["price"]

        volume_difference = (
            evening_volume - morning_volume
        )

        if morning_price > 0:

            price_change = (
                (evening_price - morning_price)
                / morning_price
            ) * 100

        else:

            price_change = 0

        rows.append({

            "Stock": symbol,

            "Morning Volume":
                int(morning_volume),

            "Evening Volume":
                int(evening_volume),

            "Volume Difference":
                int(volume_difference),

            "Price Change %":
                round(price_change, 2)

        })

    print("Rows found:", len(rows))

    if len(rows) == 0:

        print("No matching stocks found")
        exit()

    df = pd.DataFrame(rows)

    df = df.sort_values(
        "Volume Difference",
        ascending=False
    )

    df.to_excel(
        "volume_report.xlsx",
        index=False
    )

    print(df)

    send_email(df)
