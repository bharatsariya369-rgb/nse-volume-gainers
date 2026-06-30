import requests
import json
import os

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

url = "https://www.nseindia.com/api/live-analysis-volume-gainers"

response = session.get(
    url,
    headers=headers,
    timeout=30
)

data = response.json()

scan_type = os.getenv("SCAN_TYPE", "morning")

if scan_type == "morning":

    with open("morning_data.json", "w") as f:
        json.dump(data, f)

    print("Morning data saved.")
