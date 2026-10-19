import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB")]

incidents = db["incidents"]

# Insert sample incidents
sample_incidents = [
    {
        "disaster_type": "Flood",
        "location": "Katpadi",
        "severity": "Critical",
        "affected_people": 15,
        "status": "Reported"
    },
    {
        "disaster_type": "Landslide",
        "location": "Wayanad",
        "severity": "High",
        "affected_people": 8,
        "status": "Assigned"
    },
    {
        "disaster_type": "Flood",
        "location": "Chennai",
        "severity": "Medium",
        "affected_people": 5,
        "status": "Reported"
    },
    {
        "disaster_type": "Cyclone",
        "location": "Chennai",
        "severity": "Critical",
        "affected_people": 25,
        "status": "Reported"
    }
]

incidents.insert_many(sample_incidents)

# Query 1: Find Critical incidents
print("\n--- Critical Incidents ---")

for incident in incidents.find({"severity": "Critical"}):
    print(incident)

# Query 2: More than 10 affected people
print("\n--- More Than 10 Affected People ---")

for incident in incidents.find({"affected_people": {"$gt": 10}}):
    print(incident)

# Query 3: Flood incidents that are still Reported
print("\n--- Reported Flood Incidents ---")

for incident in incidents.find({
    "disaster_type": "Flood",
    "status": "Reported"
}):
    print(incident)

# Clean up test data
incidents.delete_many({
    "location": {"$in": ["Katpadi", "Wayanad", "Chennai"]}
})

print("\nTest data deleted.")

client.close()