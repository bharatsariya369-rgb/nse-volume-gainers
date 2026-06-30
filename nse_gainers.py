import yfinance as yf
import smtplib
import pytz
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SENDER    = "bharatsariya369@gmail.com"
EMAIL_PASSWORD  = os.environ["EMAIL_PASSWORD"]
EMAIL_RECIPIENT = "bharatsariya369@gmail.com"

IST = pytz.timezone("Asia/Kolkata")

STOCKS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","KOTAKBANK.NS",
    "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","TITAN.NS",
    "SUNPHARMA.NS","WIPRO.NS","BAJFINANCE.NS","TATASTEEL.NS","TATAMOTORS.NS",
    "ADANIENT.NS","ONGC.NS","POWERGRID.NS","NTPC.NS","JSWSTEEL.NS",
    "TECHM.NS","HCLTECH.NS","DRREDDY.NS","CIPLA.NS","INDUSINDBK.NS",
    "COALINDIA.NS","BPCL.NS","IOC.NS","GAIL.NS","BAJAJFINSV.NS",
    "EICHERMOT.NS","HEROMOTOCO.NS","BRITANNIA.NS","NESTLEIND.NS","DIVISLAB.NS"
]

def get_volume_gainers():
    results = {}
    data = yf.download(
        " ".join(STOCKS),
        period="2d",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False
    )
    for sym in STOCKS:
        try:
            df = data[sym].dropna()
            if len(df) < 2:
                continue
            today = df.iloc[-1]
            prev  = df.iloc[-2]
            vol_ratio = today["Volume"] / prev["Volume"] if prev["Volume"] > 0 else 0
            pchange   = ((today["Close"] - prev["Close"]) / prev["Close"]) * 100
            if vol_ratio >= 1.5 and pchange > 0:
                results[sym.replace(".NS","")] = round(float(pchange), 2)
        except:
            pass
    print(f"Volume gainers found: {len(results)}")
    return results

def send_email(results):
    today = datetime.now(IST).strftime("%d %b %Y")
    rows = ""
    for r in results:
        rows += f"""<tr>
            <td style="padding:10px;font-weight:600">{r['symbol']}</td>
            <td style="padding:10px;text-align:center">{r['morning']:+.2f}%</td>
            <td style="padding:10px;text-align:center">{r['evening']:+.2f}%</td>
            <td style="padding:10px;text-align:center;color:#00c853;font-weight:700">{r['diff']:+.2f}%</td>
        </tr>"""
    html = f"""<html><body style="font-family:Arial;padding:20px">
    <div style="max-width:620px;margin:auto;background:#fff;border-radius:10px;
                box-shadow:0 2px 12px rgba(0,0,0,0.08);overflow:hidden">
        <div style="background:#1a1a2e;padding:24px">
            <h2 style="color:#fff;margin:0">📈 NSE Volume Gainers</h2>
            <p style="color:#8892b0;margin:6px 0 0">Positive Momentum — {today}</p>
        </div>
        <div style="padding:20px">
            <table style="width:100%;border-collapse:collapse;font-size:14px">
                <thead>
                    <tr style="background:#f0f4ff">
                        <th style="padding:10px;text-align:left">Symbol</th>
                        <th style="padding:10px">Morning %</th>
                        <th style="padding:10px">Evening %</th>
                        <th style="padding:10px">Difference</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            <p style="color:#999;font-size:12px;margin-top:20px">
                Total: <b>{len(results)}</b> stocks | 3:15 PM IST
            </p>
        </div>
    </div>
    </body></html>"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📈 NSE Volume Gainers | {today}"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECIPIENT
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(EMAIL_SENDER, EMAIL_PASSWORD)
        s.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
    print("Email sent!")

# Load saved morning data
import json

SCAN_TYPE = os.environ.get("SCAN_TYPE", "morning")
DATA_FILE = "morning_data.json"

if SCAN_TYPE == "morning":
    print("Running MORNING scan...")
    data = get_volume_gainers()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
    print("Morning data saved.")

elif SCAN_TYPE == "evening":
    print("Running EVENING scan...")
    with open(DATA_FILE, "r") as f:
        morning_data = json.load(f)
    evening_data = get_volume_gainers()
    common = set(morning_data.keys()) & set(evening_data.keys())
    results = []
    for sym in common:
        diff = evening_data[sym] - morning_data[sym]
        if diff > 0:
            results.append({
                "symbol":  sym,
                "morning": morning_data[sym],
                "evening": evening_data[sym],
                "diff":    round(diff, 2)
            })
    results.sort(key=lambda x: x["diff"], reverse=True)
    print(f"Positive momentum stocks: {len(results)}")
    if results:
        send_email(results)
    else:
        print("No qualifying stocks today.")
