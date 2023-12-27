import pymongo

from pymongo import MongoClient

import config

config = config.get_config()

client = MongoClient(config.get("MongoDB").get("url"))


# SLAVES

slaves_db = client["slaves"]

pings_collection = slaves_db["ping"]

# JOBS

jobs_db = client["jobs"]

jobs_collection = jobs_db["jobs"]

# CLIENTS

clients_db = client["jobs"]

hi_collection = clients_db["hi"]