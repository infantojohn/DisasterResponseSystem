import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGODB_DB")

client = MongoClient(uri)
db = client[db_name]

incidents_collection = db["incidents"]

test_ids = []

try:
    client.admin.command("ping")
    print("MongoDB connection successful!")

    # --------------------------------
    # 1. Insert test incident reports
    # --------------------------------

    incidents = [
        {
            "disaster_type": "Flood",
            "location": "Katpadi",
            "description": "15 people are trapped inside a flooded house.",
            "severity": "Critical",
            "affected_people": 15,
            "status": "Reported"
        },
        {
            "disaster_type": "Landslide",
            "location": "Wayanad",
            "description": "Road has collapsed and several people are injured.",
            "severity": "High",
            "affected_people": 8,
            "status": "Reported"
        },
        {
            "disaster_type": "Cyclone",
            "location": "Chennai",
            "description": "Heavy rain and strong winds reported.",
            "severity": "Medium",
            "affected_people": 5,
            "status": "Reported"
        }
    ]

    result = incidents_collection.insert_many(incidents)
    test_ids = result.inserted_ids

    print("\nTest incidents inserted.")

    # --------------------------------
    # 2. Create text index
    # --------------------------------

    incidents_collection.create_index(
        [("description", "text")]
    )

    print("Text index created successfully!")

    # --------------------------------
    # 3. Search for "trapped"
    # --------------------------------

    print("\n--- Search: trapped ---")

    results = incidents_collection.find(
        {"$text": {"$search": "trapped"}}
    )

    for incident in results:
        print({
            "disaster_type": incident["disaster_type"],
            "location": incident["location"],
            "description": incident["description"],
            "severity": incident["severity"],
            "affected_people": incident["affected_people"]
        })

    # --------------------------------
    # 4. Search for "injured"
    # --------------------------------

    print("\n--- Search: injured ---")

    results = incidents_collection.find(
        {"$text": {"$search": "injured"}}
    )

    for incident in results:
        print({
            "disaster_type": incident["disaster_type"],
            "location": incident["location"],
            "description": incident["description"],
            "severity": incident["severity"],
            "affected_people": incident["affected_people"]
        })

    print("\nText Search working successfully!")

except Exception as e:

    print("\nText Search failed!")
    print(e)

finally:

    # --------------------------------
    # Delete test data
    # --------------------------------

    if test_ids:
        incidents_collection.delete_many(
            {"_id": {"$in": test_ids}}
        )

    print("\nTest data deleted.")

    client.close()