import requests
import smtplib
import math
import os
import sys

MASHHAD_LAT = 36.2605
MASHHAD_LON = 59.6168
ALERT_DISTANCE_KM = 500

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
TARGET_EMAIL = os.getenv("TARGET_EMAIL", "shirinshadino.ir@gmail.com")

if not GMAIL_USER or not GMAIL_PASS:
    print("❌ Environment variables GMAIL_USER and GMAIL_PASS are not set!")
    sys.exit(1)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def send_email():
    try:
        subject = "ISS بالای مشهد قرار گرفت"
        body = "ایستگاه فضایی بین‌المللی اکنون نزدیک مشهد است."
        msg = f"Subject: {subject}\n\n{body}"

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, TARGET_EMAIL, msg)

        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def check_iss():
    try:
        response = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=10)
        response.raise_for_status()
        data = response.json()
        iss_lat = data.get("latitude")
        iss_lon = data.get("longitude")

        if iss_lat is None or iss_lon is None:
            print("❌ ISS API response invalid:", data)
            return

        distance = haversine(MASHHAD_LAT, MASHHAD_LON, iss_lat, iss_lon)
        print(f"📍 Distance from Mashhad: {distance:.2f} km")

        if distance < ALERT_DISTANCE_KM:
            print(f"⚡ ISS is within {ALERT_DISTANCE_KM} km of Mashhad! Sending email...")
            send_email()
        else:
            print(f"ISS is too far to send alert (>{ALERT_DISTANCE_KM} km).")

    except Exception as e:
        print(f"❌ Error fetching ISS location: {e}")

if __name__ == "__main__":
    check_iss()
