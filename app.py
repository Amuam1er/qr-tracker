from flask import Flask, render_template, request, redirect, url_for, send_file
import qrcode
import os
import csv
import time
from uuid import uuid4

app = Flask(__name__)

# Make sure qr_codes folder exists
os.makedirs('qr_codes', exist_ok=True)

# Log file
LOG_FILE = 'scan_logs.csv'

# Initialize CSV if not exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id", "original_url", "timestamp", "ip"])

# Home page: generate QR
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        unique_id = str(uuid4())

        # Create QR Code that links to /redirect/<id>
        qr_link = request.host_url + 'redirect/' + unique_id
        qr_img = qrcode.make(qr_link)
        qr_path = f'qr_codes/{unique_id}.png'
        qr_img.save(qr_path)

        # Save original URL to a dictionary file
        with open('url_mappings.csv', mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([unique_id, original_url])

        return render_template('index.html', qr_path=qr_path)

    return render_template('index.html', qr_path=None)

# Redirection and logging
@app.route('/redirect/<id>')
def redirect_to_url(id):
    # Find URL
    try:
        with open('url_mappings.csv', mode='r') as f:
            reader = csv.reader(f)
            url_dict = {rows[0]: rows[1] for rows in reader}
        
        if id in url_dict:
            original_url = url_dict[id]

            # Log the scan
            with open(LOG_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([id, original_url, time.strftime("%Y-%m-%d %H:%M:%S"), request.remote_addr])

            return redirect(original_url)
        else:
            return "Invalid QR Code ID.", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

# View scan stats
@app.route('/stats')
def stats():
    scans = []
    try:
        with open(LOG_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                scans.append(row)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('stats.html', scans=scans)

if __name__ == '__main__':
    app.run(debug=True)