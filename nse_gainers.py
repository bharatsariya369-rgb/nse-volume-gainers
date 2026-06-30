import requests

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

print("Status:", response.status_code)
print(response.text[:1000])
