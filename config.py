import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")
DB_TYPE = os.getenv("DB_TYPE")
DB_FILE = os.getenv("DB_FILE")
