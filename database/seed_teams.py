from database.connection import db

rescue_teams = db["rescue_teams"]

teams = [
    {
        "name": "Water Rescue Team Alpha",
        "type": "Water Rescue Team",
        "status": "Available",
        "location": {
            "type": "Point",
            "coordinates": [78.1548, 12.9692]
        },
        "contact": {
            "phone": "9000000001",
            "email": "alpha@rescue.local"
        },
        "equipment": [
            {"name": "Rescue Boat", "quantity": 2},
            {"name": "Life Jacket", "quantity": 15}
        ]
    },
    {
        "name": "Emergency Medical Team",
        "type": "Medical Team",
        "status": "Available",
        "location": {
            "type": "Point",
            "coordinates": [78.1600, 12.9750]
        },
        "contact": {
            "phone": "9000000002",
            "email": "medical@rescue.local"
        },
        "equipment": [
            {"name": "First Aid Kit", "quantity": 10},
            {"name": "Stretcher", "quantity": 3}
        ]
    },
    {
        "name": "Search Rescue Team Bravo",
        "type": "Search and Rescue Team",
        "status": "Available",
        "location": {
            "type": "Point",
            "coordinates": [78.1500, 12.9650]
        },
        "contact": {
            "phone": "9000000003",
            "email": "bravo@rescue.local"
        },
        "equipment": [
            {"name": "Rescue Equipment", "quantity": 8},
            {"name": "Emergency Kit", "quantity": 10}
        ]
    }
]

# Avoid inserting duplicates when running the script again
for team in teams:

    existing = rescue_teams.find_one({
        "name": team["name"]
    })

    if existing:
        print("Already exists:", team["name"])
    else:
        result = rescue_teams.insert_one(team)
        print("Created:", team["name"], result.inserted_id)

print("\nRescue team setup complete!")