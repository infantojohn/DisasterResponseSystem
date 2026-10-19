import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGODB_DB")

client = MongoClient(uri)

team_id = None
incident_id = None

try:
    client.admin.command("ping")
    print("MongoDB connection successful!")

    db = client[db_name]

    teams_collection = db["rescue_teams"]
    incidents_collection = db["incidents"]

    # -----------------------------
    # 1. Create Rescue Team
    # -----------------------------

    team = {
    "team_name": "Rescue Team A",
    "team_type": "Flood Rescue",
    "location": {
        "type": "Point",
        "coordinates": [78.1548, 12.9692]
    },
    "status": "Available"
}

    team_result = teams_collection.insert_one(team)
    team_id = team_result.inserted_id

    print("\nRescue Team Created:")
    print(team)

    # -----------------------------
    # 2. Create Incident
    #    Store team reference
    # -----------------------------

    incident = {
        "disaster_type": "Flood",
        "location": "Katpadi",
        "severity": "Critical",
        "affected_people": 15,
        "assigned_team_id": team_id,
        "status": "Assigned"
    }

    incident_result = incidents_collection.insert_one(incident)
    incident_id = incident_result.inserted_id

    print("\nIncident Created:")
    print(incident)

    # -----------------------------
    # 3. $lookup
    # -----------------------------

    pipeline = [
        {
            "$lookup": {
                "from": "rescue_teams",
                "localField": "assigned_team_id",
                "foreignField": "_id",
                "as": "assigned_team"
            }
        },
        {
            "$unwind": "$assigned_team"
        },
        {
            "$project": {
                "_id": 0,
                "disaster_type": 1,
                "location": 1,
                "severity": 1,
                "affected_people": 1,
                "status": 1,
                "team_name": "$assigned_team.team_name",
                "team_type": "$assigned_team.team_type",
                "team_status": "$assigned_team.status"
            }
        }
    ]

    results = incidents_collection.aggregate(pipeline)

    print("\n--- Incident with Assigned Rescue Team ---")

    for result in results:
        print(result)

    print("\nReferences + $lookup working successfully!")

except Exception as e:
    print("\nError occurred:")
    print(e)

finally:

    # Delete incident only if it was created
    if incident_id is not None:
        incidents_collection.delete_one(
            {"_id": incident_id}
        )

    # Delete team only if it was created
    if team_id is not None:
        teams_collection.delete_one(
            {"_id": team_id}
        )

    print("\nTest data deleted.")

    client.close()