import json


global config
with open("config.json") as f:
    config = json.load(f)

def get_config():
    return config