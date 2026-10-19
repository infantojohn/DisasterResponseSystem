from database.connection import db

rescue_teams = db["rescue_teams"]

result = rescue_teams.update_one(
    {"name": "Water Rescue Team Alpha"},
    {"$set": {"status": "Available"}}
)

if result.modified_count == 1:
    print("Water Rescue Team Alpha reset to Available.")
else:
    print("Water Rescue Team was not changed.")