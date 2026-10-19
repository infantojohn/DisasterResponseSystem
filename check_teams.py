import sys
sys.path.append(".")
from database.connection import db

rescue_teams = db["rescue_teams"]

print("\n--- Rescue Team Status ---")

for team in rescue_teams.find({}, {"name": 1, "type": 1, "status": 1}):
    print(
        f"{team['name']} | "
        f"{team.get('type', '')} | "
        f"{team.get('status', '')}"
    )