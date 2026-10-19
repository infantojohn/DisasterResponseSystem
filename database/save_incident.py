from datetime import datetime

from database.connection import db
from ai.analyze_report import analyze_report


# MongoDB collection
incidents = db["incidents"]


def save_incident():
    print("AI + MongoDB Incident System")
    print("----------------------------")

    # Get citizen report
    report = input("Enter emergency report: ")

    # Get location
    location = input("Enter location: ")

    # Run AI analysis
    result = analyze_report(report)

    # Create incident document
    incident = {
        "raw_report": report,
        "disaster_type": result["disaster_type"],
        "severity": result["priority"],
        "priority": result["priority"],
        "location": location,
        "affected_people": result["affected_people"],
        "trapped_people": result["trapped_people"],
        "injured_people": result["injured_people"],
        "status": "Reported",
        "recommended_resources": result["recommended_resources"],
        "related_incidents": result["related_incidents"],
        "created_at": datetime.utcnow()
    }

    # Save to MongoDB
    insert_result = incidents.insert_one(incident)

    print("\n--- Incident Created Successfully ---")
    print("Incident ID:", insert_result.inserted_id)
    print("Disaster Type:", result["disaster_type"])
    print("Priority:", result["priority"])
    print("Affected People:", result["affected_people"])
    print("Trapped People:", result["trapped_people"])
    print("Injured People:", result["injured_people"])
    print("Status: Reported")

    print("\nRecommended Resources:")
    for resource in result["recommended_resources"]:
        print("-", resource)


if __name__ == "__main__":
    save_incident()