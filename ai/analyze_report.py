import joblib

from .extract_information import extract_information
from .duplicate_detection import find_related_reports
from .resource_recommendation import recommend_resources


# Load trained AI models
priority_model = joblib.load("ai/priority_model.pkl")
disaster_model = joblib.load("ai/disaster_type_model.pkl")




def refine_priority(priority, affected_people, trapped_people, injured_people):
    """
    Refine ML priority using extracted emergency information.
    Explicit emergency indicators take precedence over ML predictions.
    """

    affected_people = max(0, affected_people or 0)
    trapped_people = max(0, trapped_people or 0)
    injured_people = max(0, injured_people or 0)

    valid_priorities = {"Low", "Medium", "High", "Critical"}

    if priority not in valid_priorities:
        priority = "Medium"

    # CRITICAL: substantial immediate danger
    if (
        trapped_people >= 10
        or injured_people >= 5
        or affected_people >= 20
    ):
        return "Critical"

    # HIGH: significant impact or people needing rescue
    if (
        trapped_people > 0
        or affected_people >= 8
        or injured_people >= 4
    ):
        return "High"

    # MEDIUM: smaller incidents with reported injuries or impact
    if injured_people > 0 or affected_people >= 3:
        return "Medium"

    # No extracted human impact: don't blindly trust an extreme
    # ML prediction for an apparently contained, low-impact report.
    if affected_people == 0 and trapped_people == 0 and injured_people == 0:
        return priority if priority in {"Low", "Medium"} else "Low"

    return priority

def analyze_report(report):

    # --------------------------------------------------
    # 1. Predict disaster type using AI model
    # --------------------------------------------------

    disaster_type = disaster_model.predict([report])[0]


    # --------------------------------------------------
    # 2. Predict priority using AI model
    # --------------------------------------------------

    priority = priority_model.predict([report])[0]


    # --------------------------------------------------
    # 3. Extract structured information from report
    # --------------------------------------------------

    information = extract_information(report)

    affected_people = information["affected_people"]
    trapped_people = information["trapped_people"]
    injured_people = information["injured_people"]


    # --------------------------------------------------
    # 4. Refine priority using extracted information
    # --------------------------------------------------

    priority = refine_priority(
        priority,
        affected_people,
        trapped_people,
        injured_people
    )


    # --------------------------------------------------
    # 5. Find related / duplicate incidents
    # --------------------------------------------------

    _, related_incidents = find_related_reports(report)


    # --------------------------------------------------
    # 6. Recommend emergency resources
    # --------------------------------------------------

    resources = recommend_resources(
        disaster_type,
        priority,
        affected_people,
        trapped_people,
        injured_people
    )


    # --------------------------------------------------
    # 7. Create complete AI result
    # --------------------------------------------------

    result = {
        "report": report,
        "disaster_type": disaster_type,
        "priority": priority,
        "affected_people": affected_people,
        "trapped_people": trapped_people,
        "injured_people": injured_people,
        "related_incidents": related_incidents[:5],
        "recommended_resources": resources
    }


    return result


# ======================================================
# Test complete AI pipeline
# ======================================================

if __name__ == "__main__":

    print("Complete AI Disaster Report Analyzer")
    print("------------------------------------")

    report = input("Enter emergency report: ")


    # Run complete AI analysis
    result = analyze_report(report)


    # --------------------------------------------------
    # Display AI analysis
    # --------------------------------------------------

    print("\n--- AI Analysis ---")

    print("Disaster Type:", result["disaster_type"])
    print("Priority:", result["priority"])


    # --------------------------------------------------
    # Display extracted information
    # --------------------------------------------------

    print("\n--- Extracted Information ---")

    print(
        "Affected people:",
        result["affected_people"]
    )

    print(
        "Trapped people:",
        result["trapped_people"]
    )

    print(
        "Injured people:",
        result["injured_people"]
    )


    # --------------------------------------------------
    # Display related incidents
    # --------------------------------------------------

    print("\n--- Related Incidents ---")

    if result["related_incidents"]:

        for incident in result["related_incidents"]:

            print(
                "Similarity:",
                incident["similarity"],
                "|",
                incident["report"]
            )

    else:

        print("No closely related incidents found.")


    # --------------------------------------------------
    # Display recommended resources
    # --------------------------------------------------

    print("\n--- Recommended Resources ---")

    if result["recommended_resources"]:

        for resource in result["recommended_resources"]:

            print("-", resource)

    else:

        print("No specific resources recommended.")