from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import qrcode
import os
import csv
from datetime import datetime
from collections import deque, Counter

app = Flask(__name__)
QR_FOLDER = os.path.join('static', 'qr_codes')
LOG_FILE = 'qr_log.csv'
os.makedirs(QR_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_code = None
    short_link = None

    if request.method == 'POST':
        label = request.form['label']
        url = request.form['url']
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        qr_filename = f"{label}_{timestamp}.png"
        qr_path = os.path.join(QR_FOLDER, qr_filename)

        img = qrcode.make(url)
        img.save(qr_path)

        qr_code = qr_filename
        short_id = timestamp
        short_link = request.host_url + 'qr/' + short_id

        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['CREATED', short_id, label, url, request.remote_addr, timestamp])

    recent_qrs = deque(maxlen=3)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reversed(list(reader)):
                if row[0] == 'CREATED':
                    recent_qrs.appendleft({
                        'qr_id': row[1],
                        'label': row[2],
                        'filename': f"{row[2]}_{row[1]}.png"
                    })
                    if len(recent_qrs) == 3:
                        break

    return render_template('index.html', qr_code=qr_code, short_link=short_link, recent_qrs=recent_qrs)

@app.route('/qr/<qr_id>')
def redirect_qr(qr_id):
    url = None
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == 'CREATED' and row[1] == qr_id:
                    url = row[3]
                    label = row[2]
                    break
    if url:
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['SCANNED', qr_id, label, url, request.remote_addr, datetime.now().strftime('%Y%m%d%H%M%S')])
        return redirect(url)
    return 'Invalid QR code.'

@app.route('/stats')
def stats():
    logs = []
    scan_counter = Counter()

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            reader = csv.reader(f)
            logs = list(reader)
            for row in logs:
                if row[0] == 'SCANNED':
                    scan_counter[row[2]] += 1 # row [2] is the label

                    # Sorted by highest scans
    scan_summary = scan_counter.most_common()
    return render_template('stats.html', logs=logs, scan_summary=scan_summary)