import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB")]

# Select the incidents collection
incidents = db["incidents"]

# CREATE - Insert an incident
incident = {
    "disaster_type": "Flood",
    "location": "Katpadi",
    "severity": "Critical",
    "affected_people": 15,
    "status": "Reported"
}

result = incidents.insert_one(incident)

print("Incident inserted successfully!")
print("Incident ID:", result.inserted_id)

# READ - Find the incident
found_incident = incidents.find_one({"_id": result.inserted_id})

print("\nIncident retrieved:")
print(found_incident)

# UPDATE - Change the status
incidents.update_one(
    {"_id": result.inserted_id},
    {"$set": {"status": "Assigned"}}
)

print("\nIncident status updated!")

# READ again to verify update
updated_incident = incidents.find_one({"_id": result.inserted_id})

print(updated_incident)

# DELETE - Delete the test incident
incidents.delete_one({"_id": result.inserted_id})

print("\nTest incident deleted successfully!")

client.close()