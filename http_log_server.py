#!/usr/bin/env python3
from flask import Flask, request, render_template_string, request as flask_request, send_from_directory, redirect, url_for
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Disable Flask/Werkzeug access log (GET /logs won't print)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

LOG_DIR = "/home/pi/logs"

def ensure_log_dir():
    """Ensure the log directory exists. Create it if missing."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Log directory '{LOG_DIR}' created.")

ensure_log_dir()

@app.route('/testlog', methods=['POST'])
def mfg_log():
    """Receive POST log and append to today's log file."""
    data = request.data.decode('utf-8', errors='replace')
    ensure_log_dir()

    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}.log"
    filepath = os.path.join(LOG_DIR, filename)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {data}"

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

    print(log_line)
    return "Log received\n", 200

@app.route('/logs')
def show_logs():
    """Display logs with selectable files, download, delete, and refresh."""
    ensure_log_dir()

    # List all .log files in LOG_DIR, sorted descending
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".log")], reverse=True)

    # Default: latest log file
    selected_file = flask_request.args.get('file')
    if selected_file not in log_files:
        selected_file = log_files[0] if log_files else None

    content = "No logs available."
    if selected_file:
        filepath = os.path.join(LOG_DIR, selected_file)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

    # HTML template
    html_template = """
    <html>
        <head>
            <title>Logs Viewer</title>
        </head>
        <body>
            <h1>Logs Viewer</h1>
            <p style="color:gray;">Use the buttons to refresh, download, or delete the selected log file.</p>

            <!-- File selection and refresh -->
            <form method="get" action="/logs" style="display:inline-block;">
                <label for="file">Select log file: </label>
                <select id="file" name="file" onchange="this.form.submit()">
                    {% for f in log_files %}
                        <option value="{{ f }}" {% if f == selected_file %}selected{% endif %}>{{ f }}</option>
                    {% endfor %}
                </select>
                <button type="submit">Refresh</button>
            </form>

            <!-- Download button -->
            <form method="get" action="/logs/download" style="display:inline-block; margin-left:10px;">
                <input type="hidden" name="file" value="{{ selected_file }}">
                <button type="submit">Download</button>
            </form>

            <!-- Delete button -->
            <form method="post" action="/logs/delete" style="display:inline-block; margin-left:10px;">
                <input type="hidden" name="file" value="{{ selected_file }}">
                <button type="submit" onclick="return confirm('Are you sure you want to delete this log?');">Delete</button>
            </form>

            <pre>{{ content }}</pre>
        </body>
    </html>
    """
    return render_template_string(html_template, log_files=log_files, selected_file=selected_file, content=content)

@app.route('/logs/download')
def download_log():
    """Download the selected log file."""
    ensure_log_dir()
    file_name = flask_request.args.get('file')
    if not file_name or not file_name.endswith(".log"):
        return "Invalid file.", 400
    file_path = os.path.join(LOG_DIR, file_name)
    if not os.path.exists(file_path):
        return "File not found.", 404
    return send_from_directory(LOG_DIR, file_name, as_attachment=True)

@app.route('/logs/delete', methods=['POST'])
def delete_log():
    """Delete the selected log file and refresh to latest existing log."""
    ensure_log_dir()
    file_name = flask_request.form.get('file')
    if not file_name or not file_name.endswith(".log"):
        return "Invalid file.", 400
    file_path = os.path.join(LOG_DIR, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Redirect to latest existing log
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".log")], reverse=True)
    latest_file = log_files[0] if log_files else None
    if latest_file:
        return redirect(url_for('show_logs', file=latest_file))
    else:
        return redirect(url_for('show_logs'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

