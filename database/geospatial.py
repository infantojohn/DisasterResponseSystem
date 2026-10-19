import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB")]

teams = db["rescue_teams"]

# Sample rescue teams
sample_teams = [
    {
        "name": "Rescue Team A",
        "available": True,
        "location": {
            "type": "Point",
            "coordinates": [80.2707, 13.0827]
        }
    },
    {
        "name": "Rescue Team B",
        "available": True,
        "location": {
            "type": "Point",
            "coordinates": [76.9558, 11.0168]
        }
    },
    {
        "name": "Rescue Team C",
        "available": False,
        "location": {
            "type": "Point",
            "coordinates": [76.2673, 9.9312]
        }
    }
]

teams.insert_many(sample_teams)

# Create a geospatial index
teams.create_index([("location", "2dsphere")])

# Find nearest available rescue teams
incident_location = {
    "type": "Point",
    "coordinates": [80.2707, 13.0827]
}

nearest_teams = teams.find({
    "available": True,
    "location": {
        "$near": {
            "$geometry": incident_location
        }
    }
})

print("\n--- Nearest Available Rescue Teams ---")

for team in nearest_teams:
    print(team["name"])

# Delete test data
teams.delete_many({
    "name": {
        "$in": ["Rescue Team A", "Rescue Team B", "Rescue Team C"]
    }
})

print("\nTest data deleted.")

client.close()