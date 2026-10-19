import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGODB_DB")

client = MongoClient(uri)
db = client[db_name]

incidents_collection = db["incidents"]
teams_collection = db["rescue_teams"]

incident_id = None
team_id = None


try:
    client.admin.command("ping")
    print("MongoDB connection successful!")

    # --------------------------------
    # 1. Create test rescue team
    # --------------------------------

    team = {
        "team_name": "Transaction Rescue Team",
        "team_type": "Flood Rescue",
        "location": {
            "type": "Point",
            "coordinates": [78.1548, 12.9692]
        },
        "status": "Available"
    }

    team_result = teams_collection.insert_one(team)
    team_id = team_result.inserted_id

    # --------------------------------
    # 2. Create test incident
    # --------------------------------

    incident = {
        "disaster_type": "Flood",
        "location": "Katpadi",
        "severity": "Critical",
        "affected_people": 15,
        "status": "Reported"
    }

    incident_result = incidents_collection.insert_one(incident)
    incident_id = incident_result.inserted_id

    print("\nInitial Data Created")
    print("Incident status: Reported")
    print("Team status: Available")

    # --------------------------------
    # 3. Transaction
    # --------------------------------

    with client.start_session() as session:

        with session.start_transaction():

            # Assign team to incident
            incidents_collection.update_one(
                {"_id": incident_id},
                {
                    "$set": {
                        "assigned_team_id": team_id,
                        "status": "Assigned"
                    }
                },
                session=session
            )

            # Make team unavailable
            teams_collection.update_one(
                {"_id": team_id},
                {
                    "$set": {
                        "status": "Unavailable"
                    }
                },
                session=session
            )

    print("\nTransaction completed successfully!")

    # --------------------------------
    # 4. Verify changes
    # --------------------------------

    updated_incident = incidents_collection.find_one(
        {"_id": incident_id}
    )

    updated_team = teams_collection.find_one(
        {"_id": team_id}
    )

    print("\n--- Updated Incident ---")
    print({
        "status": updated_incident["status"],
        "assigned_team_id": updated_incident["assigned_team_id"]
    })

    print("\n--- Updated Rescue Team ---")
    print({
        "team_name": updated_team["team_name"],
        "status": updated_team["status"]
    })

    print("\nTransaction working successfully!")


except Exception as e:

    print("\nTransaction failed!")
    print(e)


finally:

    # --------------------------------
    # Delete test data
    # --------------------------------

    if incident_id is not None:
        incidents_collection.delete_one(
            {"_id": incident_id}
        )

    if team_id is not None:
        teams_collection.delete_one(
            {"_id": team_id}
        )

    print("\nTest data deleted.")

    client.close()