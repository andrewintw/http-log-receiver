#!/usr/bin/env python3
from flask import Flask, request, render_template_string, request as flask_request
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Disable Flask/Werkzeug access log (GET /logs won't print)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Log directory
LOG_DIR = "/home/browan/logs"

def ensure_log_dir():
    """Ensure the log directory exists. Create it if missing."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Log directory '{LOG_DIR}' created.")

# Ensure log directory exists at startup
ensure_log_dir()

@app.route('/mfg', methods=['POST'])
def mfg_log():
    """Receive POST log and append to today's log file."""
    data = request.data.decode('utf-8', errors='replace')

    # Ensure log directory exists
    ensure_log_dir()

    # Daily log file
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}.log"
    filepath = os.path.join(LOG_DIR, filename)

    # Simplified timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {data}"

    # Append to log file
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

    # Print same line to console
    print(log_line)

    return "Log received\n", 200

@app.route('/logs')
def show_logs():
    """Display logs with auto-refresh, selectable files, and explanation."""
    ensure_log_dir()

    # List all .log files in LOG_DIR, sorted descending
    log_files = sorted(
        [f for f in os.listdir(LOG_DIR) if f.endswith(".log")],
        reverse=True
    )

    # Default: latest log file
    date_str = flask_request.args.get('file', log_files[0] if log_files else None)
    if date_str and date_str in log_files:
        filepath = os.path.join(LOG_DIR, date_str)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "No logs available."

    # HTML template with auto-refresh and file selection
    html_template = """
    <html>
        <head>
            <title>Logs Viewer</title>
            <!-- Auto-refresh every 5 seconds -->
            <meta http-equiv="refresh" content="5">
        </head>
        <body>
            <h1>Logs Viewer</h1>
            <p style="color:gray;">This page updates automatically every 5 seconds.</p>
            <form method="get" action="/logs">
                <label for="file">Select log file: </label>
                <select id="file" name="file" onchange="this.form.submit()">
                    {% for f in log_files %}
                        <option value="{{ f }}" {% if f == date_str %}selected{% endif %}>{{ f }}</option>
                    {% endfor %}
                </select>
            </form>
            <pre>{{ content }}</pre>
        </body>
    </html>
    """
    return render_template_string(html_template, log_files=log_files, date_str=date_str, content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

