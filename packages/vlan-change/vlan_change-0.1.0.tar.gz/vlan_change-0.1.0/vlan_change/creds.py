import os
from dotenv import load_dotenv,find_dotenv
from pathlib import Path  # Python 3.6+ only

env_file = find_dotenv()
try:
    load_dotenv(env_file)
except:
    print("Please create a local .env file with local credentials")
    exit()

ROUTER_USERNAME = os.getenv("ROUTER_USERNAME")
ROUTER_PASSWORD = os.getenv("ROUTER_PASSWORD")
SECRET = os.getenv("SECRET")

