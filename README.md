# Dynamic QR Code Generator with Tracking

Simple Flask app that generates QR codes linking to a redirect endpoint and tracks how many times they've been scanned.

## Features
- Dynamic QR codes (server-based redirects)
- Scan logging (time, IP address)
- Scan stats dashboard

## Setup
```bash
git clone https://github.com/Amuam1er/qr-tracker.git
cd qr-tracker
pip install -r requirements.txt
python app.py