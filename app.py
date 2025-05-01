import os
import csv
import uuid
import qrcode
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Ensure folders exist
os.makedirs(os.path.join("static", "qr_codes"), exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/', methods=['POST'])
def generate_qr():
    url = request.form['url']
    label = request.form['label']

    # Generate unique QR code ID and short link
    qr_id = str(uuid.uuid4())[:8]
    short_path = f"/qr/{qr_id}"
    full_link = request.host_url.rstrip('/') + short_path

    # Save QR code to static/qr_codes/
    filename = f"{qr_id}.png"
    qr_folder = os.path.join("static", "qr_codes")
    qr_path = os.path.join(qr_folder, filename)
    img = qrcode.make(full_link)
    img.save(qr_path)

    # Log creation
    with open('scan_logs.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), request.remote_addr, label, url, qr_id, 'created'])

    return render_template("index.html", qr_image=filename, short_link=full_link)

@app.route('/qr/<qr_id>')
def redirect_qr(qr_id):
    # Find the matching QR code from the log
    with open('scan_logs.csv', 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    destination_url = None
    label = None
    for row in reversed(rows):
        if row[4] == qr_id and row[5] == 'created':
            destination_url = row[3]
            label = row[2]
            break

    if destination_url:
        # Log the scan
        with open('scan_logs.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now(), request.remote_addr, label, destination_url, qr_id, 'scanned'])
        return redirect(destination_url)
    else:
        return "QR code not found", 404

@app.route('/stats')
def stats():
    logs = []
    if os.path.exists("scan_logs.csv"):
        with open("scan_logs.csv", newline='') as file:
            reader = csv.reader(file)
            logs = list(reader)
    return render_template("stats.html", logs=logs)

if __name__ == '__main__':
    app.run(debug=True)