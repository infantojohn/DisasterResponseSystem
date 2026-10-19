from database.connection import db

incidents = db["incidents"]

print("Stored Disaster Incidents")
print("------------------------")

for incident in incidents.find().sort("created_at", -1):

    print("\nIncident ID:", incident["_id"])
    print("Disaster Type:", incident["disaster_type"])
    print("Priority:", incident["priority"])
    print("Location:", incident["location"])
    print("Affected:", incident["affected_people"])
    print("Trapped:", incident["trapped_people"])
    print("Injured:", incident["injured_people"])
    print("Status:", incident["status"])