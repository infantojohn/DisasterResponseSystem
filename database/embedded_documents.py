from connection import db

teams_collection = db["rescue_teams"]


def create_embedded_document():
    print("\n--- Embedded Document ---")

    team = {
        "team_name": "Rescue Team A",
        "team_type": "Flood Rescue",
        "location": {
    "type": "Point",
    "coordinates": [78.1548, 12.9692]
},

        "contact": {
            "phone": "9876543210",
            "email": "teamA@rescue.org"
        },

        "equipment": [
            {
                "name": "Rescue Boat",
                "quantity": 2
            },
            {
                "name": "Life Jacket",
                "quantity": 15
            }
        ]
    }

    result = teams_collection.insert_one(team)

    print("Embedded document inserted successfully!")

    saved_team = teams_collection.find_one(
        {"_id": result.inserted_id}
    )

    print("\nSaved Rescue Team:")
    print(saved_team)

    teams_collection.delete_one({"_id": result.inserted_id})

    print("\nTest data deleted.")


if __name__ == "__main__":
    create_embedded_document()