import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGODB_DB")

client = MongoClient(uri)

# Select the database
db = client[db_name]

try:
    client.admin.command("ping")
    print("MongoDB connection successful!")
    print("Database:", db_name)

except Exception as e:
    print("MongoDB connection failed!")
    print(e)