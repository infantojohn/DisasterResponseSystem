import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB")]

incidents = db["incidents"]

# Sample data
sample_incidents = [
    {"disaster_type": "Flood", "severity": "Critical", "affected_people": 15},
    {"disaster_type": "Flood", "severity": "High", "affected_people": 20},
    {"disaster_type": "Landslide", "severity": "High", "affected_people": 8},
    {"disaster_type": "Cyclone", "severity": "Critical", "affected_people": 25},
    {"disaster_type": "Flood", "severity": "Medium", "affected_people": 5}
]

incidents.insert_many(sample_incidents)

# Aggregation: group incidents by disaster type
pipeline = [
    {
        "$group": {
            "_id": "$disaster_type",
            "incident_count": {"$sum": 1},
            "total_affected": {"$sum": "$affected_people"}
        }
    },
    {
        "$sort": {
            "total_affected": -1
        }
    }
]

results = incidents.aggregate(pipeline)

print("\n--- Disaster Statistics ---")

for result in results:
    print(result)

# Delete test data
incidents.delete_many({
    "disaster_type": {
        "$in": ["Flood", "Landslide", "Cyclone"]
    }
})

print("\nTest data deleted.")

client.close()