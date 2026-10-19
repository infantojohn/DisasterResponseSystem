import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGODB_DB")

client = MongoClient(uri)
db = client[db_name]

incidents_collection = db["incidents"]

print("MongoDB connection successful!")
print("\n--- Watching for MongoDB Changes ---")
print("Create or update an incident through the application...")
print("Press Ctrl+C to stop.\n")

try:
    with incidents_collection.watch(
        full_document="updateLookup"
    ) as stream:

        for change in stream:

            print("\n==============================")
            print("Change detected!")
            print("Operation:", change["operationType"])

            if change["operationType"] == "insert":

                print("New incident detected:")
                print(change["fullDocument"])

            elif change["operationType"] == "update":

                print("Incident updated:")
                print(change["documentKey"])

                if "fullDocument" in change:
                    print("Updated document:")
                    print(change["fullDocument"])

            print("==============================")

except KeyboardInterrupt:
    print("\nChange Stream stopped.")

finally:
    client.close()