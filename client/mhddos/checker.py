import json
import os
import random
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .MHDDoS.start import ProxyManager
from PyRoxy import ProxyChecker
from PyRoxy import ProxyType

def get_conf(filename):
    with open(f'c:\\users\\vuore\\ns\\client\\mhddos\\{filename}') as f:
        config = json.load(f)

    return config

def update_proxies(period, proxy_timeout, threads, targets):
    if os.path.exists('files/proxies/proxies.txt'):
        last_update = os.path.getmtime('files/proxies/proxies.txt')
        if (time.time() - last_update) < period / 2:
            return
    Proxies = []
    filenames, num, CheckedProxies, size = recheck(proxy_timeout, threads, targets, Proxies)

    if len(CheckedProxies) > threads:
        Proxies = get_proxies(filenames, num+1)
        recheck(proxy_timeout, threads, targets, Proxies)

    os.makedirs('files/proxies/', exist_ok=True)
    with open('files/proxies/proxies.txt', "w") as all_wr, \
         open('files/proxies/socks4.txt', "w") as socks4_wr, \
         open('files/proxies/socks5.txt', "w") as socks5_wr:
        for proxy in CheckedProxies:
            proxy_string = str(proxy) + "\n"
            all_wr.write(proxy_string)
            if proxy.type == ProxyType.SOCKS4:
                socks4_wr.write(proxy_string)
            if proxy.type == ProxyType.SOCKS5:
                socks5_wr.write(proxy_string)

    print(f"Checked and saved {len(CheckedProxies)} proxies.")

def recheck(proxy_timeout, threads, targets, Proxies):
    filenames = ["proxies_shorter.json", "proxies_config.json2", "proxies_config.json"]
    num = 0

    while len(Proxies) < threads:
        Proxies = get_proxies(filenames, num)


    print(f"We got {len(Proxies)} proxies!")
    random.shuffle(Proxies)



    CheckedProxies = []
    size = len(targets)

    check_target_prox(proxy_timeout, threads, targets, Proxies, CheckedProxies, size)
    return filenames,num,CheckedProxies,size

def check_target_prox(proxy_timeout, threads, targets, Proxies, CheckedProxies, size):
    for target in targets:
        print(f"Checking proxies for {target}... ", end='', flush=True)
        chunk_size = len(Proxies) // size
        for i in range(0, len(Proxies), chunk_size):
            chunk = Proxies[i:i+chunk_size]
            result = ProxyChecker.checkAll(proxies=chunk, timeout=proxy_timeout, threads=threads // size, url=target)
            CheckedProxies.extend(result)
            print('.', end='', flush=True)
        print()  # Move to the next line after completing the progress

    if not CheckedProxies:
        exit("Proxy Check failed, Your network may be the problem | The target may not be available.")

def get_proxies(filenames, num):
    if num == 3:
        num = 0
    Proxies = list(ProxyManager.DownloadFromConfig(get_conf(filenames[num]), 0))
    print(len(Proxies))
    num +1
    return Proxies

def start(total_threads, period, targets, proxy_timeout):
    no_proxies = all(target.lower().startswith('udp://') for target in targets)
    while True:
        if not no_proxies:
            update_proxies(period, proxy_timeout, total_threads, targets)

        time.sleep(60)

def run(targets):
    start(
        100,  # Adjust the number of threads as needed
        300,
        targets,
        2,   # Adjust the proxy timeout as needed
    )
