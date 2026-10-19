
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import re

from fastapi import FastAPI
from pydantic import BaseModel

from database.connection import db
from ai.analyze_report import analyze_report
from fastapi.responses import StreamingResponse
import json

import math
from datetime import date, datetime
from bson import ObjectId


def make_json_safe(value):
    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    if isinstance(value, float) and not math.isfinite(value):
        return None

    if isinstance(value, (ObjectId, datetime, date)):
        return str(value)

    return value
app = FastAPI(
    title="AI Disaster Response System",
    description="AI-powered disaster analysis and response backend",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

incidents = db["incidents"]


class IncidentRequest(BaseModel):
    report: str
    location: str


@app.get("/")
def home():
    return {
        "message": "AI Disaster Response System API is running"
    }


@app.post("/incidents")
def create_incident(request: IncidentRequest):

    # Run complete AI analysis
    result = analyze_report(request.report)

    # Create MongoDB document
    incident = {
        "raw_report": request.report,
        "disaster_type": result["disaster_type"],
        "severity": result["priority"],
        "priority": result["priority"],
        "location": request.location,
        "affected_people": result["affected_people"],
        "trapped_people": result["trapped_people"],
        "injured_people": result["injured_people"],
        "status": "Reported",
        "recommended_resources": result["recommended_resources"],
        "related_incidents": result["related_incidents"],
        "created_at": datetime.now(timezone.utc)
    }

    # Store in MongoDB
    insert_result = incidents.insert_one(incident)

    return {
        "message": "Incident created successfully",
        "incident_id": str(insert_result.inserted_id),
        "analysis": {
            "disaster_type": result["disaster_type"],
            "priority": result["priority"],
            "affected_people": result["affected_people"],
            "trapped_people": result["trapped_people"],
            "injured_people": result["injured_people"]
        },
        "recommended_resources": result["recommended_resources"]
    }


# Search and filter incidents
@app.get("/incidents")
def get_incidents(
    search: str = "",
    disaster_type: str = "",
    priority: str = "",
    status: str = ""
):
    # Build a MongoDB query from the selected filters.
    query = {}

    search = search.strip()

    if search:
        safe_search = re.escape(search)

        query["$or"] = [
            {
                "raw_report": {
                    "$regex": safe_search,
                    "$options": "i"
                }
            },
            {
                "location": {
                    "$regex": safe_search,
                    "$options": "i"
                }
            }
        ]

    if disaster_type.strip():
        query["disaster_type"] = disaster_type.strip()

    if priority.strip():
        query["priority"] = priority.strip()

    if status.strip():
        query["status"] = status.strip()

    incidents_list = []

    for incident in incidents.find(query).sort("created_at", -1):
        incidents_list.append({
            "id": str(incident["_id"]),
            "disaster_type": incident.get("disaster_type"),
            "priority": incident.get("priority"),
            "location": incident.get("location"),
            "affected_people": incident.get("affected_people", 0),
            "trapped_people": incident.get("trapped_people", 0),
            "injured_people": incident.get("injured_people", 0),
            "status": incident.get("status"),
            "assigned_team_id": (
                str(incident["assigned_team_id"])
                if incident.get("assigned_team_id")
                else None
            ),
            "created_at": str(incident.get("created_at"))
        })

    return incidents_list


@app.get("/dashboard/stats")
def get_dashboard_stats():

    pipeline = [
        {
            "$group": {
                "_id": "$priority",
                "count": {"$sum": 1}
            }
        }
    ]

    results = list(incidents.aggregate(pipeline))

    stats = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    for result in results:
        priority = result["_id"]

        if priority in stats:
            stats[priority] = result["count"]

    stats["total"] = sum(stats.values())

    return stats


@app.post("/incidents/{incident_id}/assign/{team_id}")
def assign_team(incident_id: str, team_id: str):

    incident = incidents.find_one({
        "_id": ObjectId(incident_id)
    })

    if not incident:
        return {
            "error": "Incident not found"
        }

    rescue_teams = db["rescue_teams"]

    team = rescue_teams.find_one({
        "_id": ObjectId(team_id)
    })

    if not team:
        return {
            "error": "Rescue team not found"
        }

    if team.get("status") != "Available":
        return {
            "error": "Rescue team is not available"
        }

    # MongoDB transaction
    with db.client.start_session() as session:

        with session.start_transaction():

            # Assign team to incident
            incidents.update_one(
                {"_id": ObjectId(incident_id)},
                {
                    "$set": {
                        "assigned_team_id": ObjectId(team_id),
                        "status": "Assigned"
                    }
                },
                session=session
            )

            # Mark team unavailable
            rescue_teams.update_one(
                {"_id": ObjectId(team_id)},
                {
                    "$set": {
                        "status": "Unavailable"
                    }
                },
                session=session
            )

    return {
        "message": "Rescue team assigned successfully",
        "incident_id": incident_id,
        "team_id": team_id,
        "team_name": team["name"],
        "status": "Assigned"
    }


@app.get("/incidents/{incident_id}/recommended-teams")
def recommend_teams(incident_id: str):

    incident = incidents.find_one({
        "_id": ObjectId(incident_id)
    })

    if not incident:
        return {"error": "Incident not found"}

    available_teams = list(
        db["rescue_teams"].find({"status": "Available"})
    )

    disaster_type = incident.get("disaster_type", "")
    priority = incident.get("priority", "")
    injured_people = incident.get("injured_people", 0)
    trapped_people = incident.get("trapped_people", 0)

    recommendations = []

    for team in available_teams:

        score = 0
        reason = []

        team_name = team.get("name", "")
        team_type = team.get("type", "")

        # Flood-related incidents
        if disaster_type == "Flood":
            if "Water" in team_name or "Water" in team_type:
                score += 100
                reason.append("Suitable for flood/water rescue")

        # Medical emergencies
        if injured_people > 0:
            if "Medical" in team_name or "Medical" in team_type:
                score += 100
                reason.append("Medical assistance required")

        # Trapped people / structural disasters
        if trapped_people > 0:
            if "Search" in team_name or "Search" in team_type:
                score += 100
                reason.append("People reported trapped")

        # Critical incidents get additional priority
        if priority == "Critical":
            score += 20
            reason.append("Critical priority incident")

        recommendations.append({
            "id": str(team["_id"]),
            "name": team_name,
            "type": team_type,
            "score": score,
            "reason": reason
        })

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "incident_id": incident_id,
        "recommendations": recommendations
    }


@app.get("/rescue-teams")
def get_rescue_teams():

    rescue_teams = db["rescue_teams"]

    teams = []

    for team in rescue_teams.find():
        teams.append({
            "id": str(team["_id"]),
            "name": team["name"],
            "type": team["type"],
            "status": team["status"]
        })

    return teams


@app.get("/teams/{team_id}/incidents")
def get_team_incidents(team_id: str):

    rescue_teams = db["rescue_teams"]

    # Check whether team exists
    team = rescue_teams.find_one({
        "_id": ObjectId(team_id)
    })

    if not team:
        return {
            "error": "Rescue team not found"
        }

    team_incidents = []

    for incident in incidents.find({
        "assigned_team_id": ObjectId(team_id)
    }).sort("created_at", -1):

        team_incidents.append({
            "id": str(incident["_id"]),
            "disaster_type": incident.get("disaster_type"),
            "priority": incident.get("priority"),
            "location": incident.get("location"),
            "affected_people": incident.get("affected_people", 0),
            "trapped_people": incident.get("trapped_people", 0),
            "injured_people": incident.get("injured_people", 0),
            "status": incident.get("status"),
            "created_at": str(incident.get("created_at"))
        })

    return team_incidents


@app.put("/incidents/{incident_id}/status")
def update_incident_status(incident_id: str, new_status: str):

    new_status = new_status.strip()

    status_map = {
        "assigned": "Assigned",
        "accepted": "Accepted",
        "on the way": "On the Way",
        "rescuing": "Rescuing",
        "completed": "Completed"
    }

    new_status = status_map.get(new_status.lower())

    if new_status is None:
        return {
            "error": "Invalid status"
        }

    incident = incidents.find_one({
        "_id": ObjectId(incident_id)
    })

    if not incident:
        return {
            "error": "Incident not found"
        }

    current_status = incident.get("status")

    allowed_transitions = {
        "Assigned": ["Accepted"],
        "Accepted": ["On the Way"],
        "On the Way": ["Rescuing"],
        "Rescuing": ["Completed"]
    }

    if new_status not in allowed_transitions.get(current_status, []):
        return {
            "error": (
                f"Cannot change status from "
                f"{current_status} to {new_status}"
            )
        }

    # Update incident status
    incidents.update_one(
        {"_id": ObjectId(incident_id)},
        {
            "$set": {
                "status": new_status
            }
        }
    )

    # If rescue is completed, make the assigned team available again
    if new_status == "Completed":

        assigned_team_id = incident.get("assigned_team_id")

        if assigned_team_id:
            rescue_teams = db["rescue_teams"]

            rescue_teams.update_one(
                {"_id": assigned_team_id},
                {
                    "$set": {
                        "status": "Available"
                    }
                }
            )

    status_history = db["incident_status_history"]

    status_history.insert_one({
        "incident_id": ObjectId(incident_id),
        "old_status": current_status,
        "new_status": new_status,
        "updated_at": datetime.now(timezone.utc)
    })

    return {
        "message": "Incident status updated successfully",
        "incident_id": incident_id,
        "old_status": current_status,
        "new_status": new_status
    }


@app.get("/incidents/{incident_id}/history")
def get_incident_history(incident_id: str):

    status_history = db["incident_status_history"]

    history = status_history.find(
        {"incident_id": ObjectId(incident_id)}
    ).sort("updated_at", 1)

    result = []

    for record in history:
        result.append({
            "old_status": record["old_status"],
            "new_status": record["new_status"],
            "updated_at": record["updated_at"]
        })

    return result


from fastapi.responses import StreamingResponse
import json


@app.get("/incidents/stream")
def incident_stream():

    def event_generator():
        # Watch changes across all collections in the database.
        with db.watch(
            [
                {
                    "$match": {
                        "operationType": {
                            "$in": [
                                "insert",
                                "update",
                                "replace",
                                "delete"
                            ]
                        }
                    }
                }
            ],
            max_await_time_ms=1000
        ) as stream:

            for change in stream:
                event = {
                    "collection": change.get("ns", {}).get("coll"),
                    "operation": change.get("operationType"),
                    "document": change.get("fullDocument")
                }

                safe_event = make_json_safe(event)
                yield f"data: {json.dumps(safe_event, allow_nan=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )