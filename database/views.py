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
    # 1. Insert test incidents
    # --------------------------------

    incidents = [
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
            "status": "Reported"
        },
        {
            "disaster_type": "Cyclone",
            "location": "Chennai",
            "severity": "Medium",
            "affected_people": 5,
            "status": "Reported"
        }
    ]

    result = incidents_collection.insert_many(incidents)
    test_ids = result.inserted_ids

    print("\nTest incidents inserted.")

    # --------------------------------
    # 2. Create MongoDB View
    # --------------------------------

    view_name = "incident_summary"

    # Remove old view if it already exists
    if view_name in db.list_collection_names():
        db.drop_collection(view_name)

    pipeline = [
        {
            "$project": {
                "_id": 0,
                "disaster_type": 1,
                "location": 1,
                "severity": 1,
                "affected_people": 1,
                "status": 1
            }
        }
    ]

    db.command(
        "create",
        view_name,
        viewOn="incidents",
        pipeline=pipeline
    )

    print("MongoDB View created successfully!")

    # --------------------------------
    # 3. Read from the View
    # --------------------------------

    print("\n--- Incident Summary View ---")

    view_collection = db[view_name]

    for incident in view_collection.find():
        print(incident)

    print("\nViews working successfully!")

except Exception as e:

    print("\nViews failed!")
    print(e)

finally:

    # --------------------------------
    # Delete test data
    # --------------------------------

    if test_ids:
        incidents_collection.delete_many(
            {"_id": {"$in": test_ids}}
        )

    # Remove test view
    if "incident_summary" in db.list_collection_names():
        db.drop_collection("incident_summary")

    print("\nTest data deleted.")

    client.close()