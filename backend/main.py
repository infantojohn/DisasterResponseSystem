
import json
import math
import re
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database.connection import db
from ai.analyze_report import analyze_report


# --------------------------------------------------
# JSON SAFETY
# --------------------------------------------------

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

    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    return value


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

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


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "AI Disaster Response System API is running"
    }


# --------------------------------------------------
# CREATE INCIDENT WITH AI ANALYSIS
# --------------------------------------------------

@app.post("/incidents")
def create_incident(request: IncidentRequest):

    result = analyze_report(request.report)

    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(ZoneInfo("Asia/Kolkata"))

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
        "created_at": now_utc,
        "created_at_ist": now_ist.strftime("%Y-%m-%d %H:%M:%S")
    }

    insert_result = incidents.insert_one(incident)

    db["incident_status_history"].insert_one({
        "incident_id": insert_result.inserted_id,
        "old_status": None,
        "new_status": "Reported",
        "updated_at": now_utc
    })

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


# --------------------------------------------------
# GET INCIDENTS WITH SEARCH AND FILTERS
# --------------------------------------------------

@app.get("/incidents")
def get_incidents(
    search: str = "",
    disaster_type: str = "",
    priority: str = "",
    status: str = "",
    date_from: date | None = None,
    date_to: date | None = None
):
    query = {}
    ist = ZoneInfo("Asia/Kolkata")

    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=400,
            detail="date_from must be on or before date_to"
        )

    date_conditions = {}

    if date_from:
        start_ist = datetime.combine(
            date_from,
            time.min,
            tzinfo=ist
        )
        date_conditions["$gte"] = start_ist.astimezone(timezone.utc)

    if date_to:
        end_exclusive_ist = datetime.combine(
            date_to + timedelta(days=1),
            time.min,
            tzinfo=ist
        )
        date_conditions["$lt"] = (
            end_exclusive_ist.astimezone(timezone.utc)
        )

    if date_conditions:
        query["created_at"] = date_conditions

    search = search.strip()

    if search:
        safe_search = re.escape(search)

        disaster_categories = [
            "Flood",
            "Fire",
            "Cyclone",
            "Building Collapse",
            "Landslide"
        ]

        matched_category = next(
            (
                category
                for category in disaster_categories
                if category.lower() == search.lower()
            ),
            None
        )

        if matched_category:
            query["disaster_type"] = {
                "$regex": f"^{re.escape(matched_category)}$",
                "$options": "i"
            }
        else:
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
                },
                {
                    "disaster_type": {
                        "$regex": safe_search,
                        "$options": "i"
                    }
                },
                {
                    "priority": {
                        "$regex": safe_search,
                        "$options": "i"
                    }
                },
                {
                    "status": {
                        "$regex": safe_search,
                        "$options": "i"
                    }
                }
            ]

    if disaster_type.strip() and disaster_type.strip().lower() != "all":
        query["disaster_type"] = {
            "$regex": f"^{re.escape(disaster_type.strip())}$",
            "$options": "i"
        }

    if priority.strip() and priority.strip().lower() != "all":
        query["priority"] = {
            "$regex": f"^{re.escape(priority.strip())}$",
            "$options": "i"
        }

    if status.strip() and status.strip().lower() != "all":
        query["status"] = {
            "$regex": f"^{re.escape(status.strip())}$",
            "$options": "i"
        }

    matching_incidents = list(
        incidents.find(query).sort("created_at", -1)
    )

    return make_json_safe(matching_incidents)


# --------------------------------------------------
# DASHBOARD STATISTICS
# --------------------------------------------------

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
        priority_value = result["_id"]

        if priority_value in stats:
            stats[priority_value] = result["count"]

    stats["total"] = sum(stats.values())

    return stats


# --------------------------------------------------
# ASSIGN RESCUE TEAM
# --------------------------------------------------

@app.post("/incidents/{incident_id}/assign/{team_id}")
def assign_team(incident_id: str, team_id: str):

    try:
        incident_object_id = ObjectId(incident_id)
        team_object_id = ObjectId(team_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid incident ID or team ID"
        )

    incident = incidents.find_one({
        "_id": incident_object_id
    })

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    if incident.get("status") == "Completed":
        raise HTTPException(
            status_code=409,
            detail=(
                "A completed incident cannot be reassigned. "
                "Create a new incident if further help is needed."
            )
        )

    rescue_teams = db["rescue_teams"]

    team = rescue_teams.find_one({
        "_id": team_object_id
    })

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Rescue team not found"
        )

    if team.get("status") != "Available":
        raise HTTPException(
            status_code=409,
            detail="Rescue team is not available"
        )

    assigned_at = datetime.now(timezone.utc)

    with db.client.start_session() as session:
        with session.start_transaction():

            incidents.update_one(
                {"_id": incident_object_id},
                {
                    "$set": {
                        "assigned_team_id": team_object_id,
                        "status": "Assigned",
                        "assigned_at": assigned_at
                    }
                },
                session=session
            )

            rescue_teams.update_one(
                {"_id": team_object_id},
                {
                    "$set": {
                        "status": "Unavailable"
                    }
                },
                session=session
            )

            db["incident_status_history"].insert_one(
                {
                    "incident_id": incident_object_id,
                    "old_status": incident.get("status", "Reported"),
                    "new_status": "Assigned",
                    "updated_at": assigned_at
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


# --------------------------------------------------
# RECOMMEND AVAILABLE RESCUE TEAMS
# --------------------------------------------------

@app.get("/incidents/{incident_id}/recommended-teams")
def recommend_teams(incident_id: str):

    try:
        object_id = ObjectId(incident_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid incident ID"
        )

    incident = incidents.find_one({"_id": object_id})

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    available_teams = list(
        db["rescue_teams"].find({"status": "Available"})
    )

    disaster_type_value = incident.get("disaster_type", "")
    priority_value = incident.get("priority", "")
    injured_people = incident.get("injured_people", 0) or 0
    trapped_people = incident.get("trapped_people", 0) or 0

    recommendations = []

    for team in available_teams:
        score = 0
        reason = []

        team_name = team.get("name", "")
        team_type = team.get("type", "")

        if disaster_type_value == "Flood":
            if (
                "water" in team_name.lower()
                or "water" in team_type.lower()
            ):
                score += 100
                reason.append("Suitable for flood/water rescue")

        if injured_people > 0:
            if (
                "medical" in team_name.lower()
                or "medical" in team_type.lower()
            ):
                score += 100
                reason.append("Medical assistance required")

        if trapped_people > 0:
            if (
                "search" in team_name.lower()
                or "search" in team_type.lower()
            ):
                score += 100
                reason.append("People reported trapped")

        if priority_value == "Critical":
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
        key=lambda item: item["score"],
        reverse=True
    )

    return {
        "incident_id": incident_id,
        "recommendations": recommendations
    }


# --------------------------------------------------
# GET RESCUE TEAMS
# --------------------------------------------------

@app.get("/rescue-teams")
def get_rescue_teams():

    teams = []

    for team in db["rescue_teams"].find():
        teams.append({
            "id": str(team["_id"]),
            "name": team["name"],
            "type": team["type"],
            "status": team["status"]
        })

    return teams


# --------------------------------------------------
# GET INCIDENTS ASSIGNED TO A TEAM
# --------------------------------------------------

@app.get("/teams/{team_id}/incidents")
def get_team_incidents(team_id: str):

    try:
        team_object_id = ObjectId(team_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid team ID"
        )

    team = db["rescue_teams"].find_one({
        "_id": team_object_id
    })

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Rescue team not found"
        )

    team_incidents = []

    for incident in incidents.find({
        "assigned_team_id": team_object_id
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
            "created_at": make_json_safe(incident.get("created_at")),
            "created_at_ist": incident.get("created_at_ist")
        })

    return team_incidents


# --------------------------------------------------
# UPDATE INCIDENT STATUS AND RELEASE TEAM ON COMPLETION
# --------------------------------------------------

@app.put("/incidents/{incident_id}/status")
def update_incident_status(incident_id: str, new_status: str):

    try:
        incident_object_id = ObjectId(incident_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid incident ID"
        )

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
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    incident = incidents.find_one({
        "_id": incident_object_id
    })

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    current_status = incident.get("status")

    allowed_transitions = {
        "Assigned": ["Accepted"],
        "Accepted": ["On the Way"],
        "On the Way": ["Rescuing"],
        "Rescuing": ["Completed"]
    }

    if new_status not in allowed_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change status from "
                f"{current_status} to {new_status}"
            )
        )

    now_utc = datetime.now(timezone.utc)

    incidents.update_one(
        {"_id": incident_object_id},
        {
            "$set": {
                "status": new_status
            }
        }
    )

    if new_status == "Completed":
        assigned_team_id = incident.get("assigned_team_id")

        if assigned_team_id:
            db["rescue_teams"].update_one(
                {"_id": assigned_team_id},
                {
                    "$set": {
                        "status": "Available"
                    }
                }
            )

    db["incident_status_history"].insert_one({
        "incident_id": incident_object_id,
        "old_status": current_status,
        "new_status": new_status,
        "updated_at": now_utc
    })

    return {
        "message": "Incident status updated successfully",
        "incident_id": incident_id,
        "old_status": current_status,
        "new_status": new_status
    }


# --------------------------------------------------
# GET INCIDENT STATUS HISTORY
# --------------------------------------------------

@app.get("/incidents/{incident_id}/history")
def get_incident_history(incident_id: str):

    try:
        object_id = ObjectId(incident_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid incident ID"
        )

    incident = incidents.find_one({"_id": object_id})

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    history = list(
        db["incident_status_history"].find({
            "incident_id": object_id
        })
    )

    status_names = {
        "reported": "Reported",
        "assigned": "Assigned",
        "accepted": "Accepted",
        "on the way": "On the Way",
        "on_the_way": "On the Way",
        "rescuing": "Rescuing",
        "completed": "Completed"
    }

    def get_timestamp(record):
        value = (
            record.get("updated_at")
            or record.get("timestamp")
            or record.get("created_at")
        )

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
            except ValueError:
                return None

        return None

    result = []

    for record in history:
        raw_status = record.get("new_status", "")
        status_name = status_names.get(
            str(raw_status).strip().lower(),
            raw_status
        )

        timestamp = get_timestamp(record)

        result.append({
            "old_status": record.get("old_status"),
            "new_status": status_name,
            "updated_at": (
                make_json_safe(timestamp)
                if timestamp else None
            )
        })

    # Recover Reported and Assigned only from genuine saved timestamps.
    fallback_events = [
        ("Reported", None, incident.get("created_at")),
        ("Assigned", "Reported", incident.get("assigned_at"))
    ]

    for status_name, old_status, timestamp in fallback_events:
        has_timestamped_event = any(
            item["new_status"] == status_name
            and item["updated_at"]
            for item in result
        )

        if not has_timestamped_event and timestamp:
            result.append({
                "old_status": old_status,
                "new_status": status_name,
                "updated_at": make_json_safe(timestamp)
            })

    # Sort by actual time, not by status name or insertion order.
    def sort_key(item):
        value = item.get("updated_at")

        if not value:
            return (1, "")

        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return (
                0,
                parsed.astimezone(timezone.utc).isoformat()
            )

        except (ValueError, AttributeError):
            return (1, "")

    result.sort(key=sort_key)

    # The timeline UI shows one milestone per status.
    # Keep the earliest genuine timestamp for each status.
    deduplicated = []
    seen = set()

    for item in result:
        status_name = item.get("new_status")

        if status_name in seen:
            continue

        seen.add(status_name)
        deduplicated.append(item)

    return deduplicated


# --------------------------------------------------
# LIVE UPDATES USING MONGODB CHANGE STREAMS
# --------------------------------------------------

@app.get("/incidents/stream")
def incident_stream():

    def event_generator():
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

                yield (
                    f"data: {json.dumps(safe_event, allow_nan=False)}\n\n"
                )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
