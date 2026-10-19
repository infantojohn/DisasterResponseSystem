from connection import db
from pymongo.errors import WriteError

incidents_collection = db["incidents"]


def setup_validation():
    print("\n--- Setting Up Schema Validation ---")

    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "disaster_type",
                "location",
                "severity",
                "affected_people",
                "status"
            ],
            "properties": {
                "disaster_type": {
                    "bsonType": "string",
                    "description": "Disaster type must be a string"
                },
                "location": {
                    "bsonType": "string",
                    "description": "Location must be a string"
                },
                "severity": {
                    "enum": ["Low", "Medium", "High", "Critical"],
                    "description": "Severity must be Low, Medium, High or Critical"
                },
                "affected_people": {
                    "bsonType": "int",
                    "minimum": 0,
                    "description": "Affected people must be a non-negative integer"
                },
                "status": {
                    "enum": [
                        "Reported",
                        "Assigned",
                        "Accepted",
                        "On the Way",
                        "Rescuing",
                        "Completed"
                    ],
                    "description": "Invalid incident status"
                }
            }
        }
    }

    # Apply validation to the incidents collection
    db.command(
        "collMod",
        "incidents",
        validator=validator,
        validationLevel="strict",
        validationAction="error"
    )

    print("Schema validation applied successfully!")


def test_validation():
    print("\n--- Testing Valid Incident ---")

    valid_incident = {
        "disaster_type": "Flood",
        "location": "Katpadi",
        "severity": "Critical",
        "affected_people": 15,
        "status": "Reported"
    }

    try:
        result = incidents_collection.insert_one(valid_incident)
        print("Valid incident inserted successfully!")
        incidents_collection.delete_one({"_id": result.inserted_id})

    except Exception as e:
        print("Unexpected error:", e)

    print("\n--- Testing Invalid Incident ---")

    invalid_incident = {
        "disaster_type": "Flood",
        "location": "Katpadi",
        "severity": "Extremely Critical",
        "affected_people": 15,
        "status": "Reported"
    }

    try:
        incidents_collection.insert_one(invalid_incident)
        print("ERROR: Invalid incident was accepted!")

    except WriteError:
        print("Invalid incident rejected successfully by MongoDB!")


if __name__ == "__main__":
    setup_validation()
    test_validation()