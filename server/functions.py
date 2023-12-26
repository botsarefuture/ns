import db
import pymongo


def check_and_notify():
    highest_priority_job = db.jobs_collection.find_one({"done": False, "priority": 0})
    
    if highest_priority_job:
        return True
            
    else:
        return False
    
def get_highest_priority():
    highest_priority_job = db.jobs_collection.find_one(
        {"done": False},
        sort=[("priority", pymongo.ASCENDING)]
    )

    if highest_priority_job:
        return highest_priority_job["priority"]
    else:
        return -1  # Return None if no undone jobs are found