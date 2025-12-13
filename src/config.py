from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
env_path = ROOT / ".env" # it gets the root folder of the src like here it is the data_engineering so the env_path will be 
# data_engineering/.env

load_dotenv(dotenv_path=env_path) # defines the variable in the dotenv 

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST","localhost") # the 2nd param is the default
DB_PORT = int(os.getenv("DB_PORT",5432)) # here also the same
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
