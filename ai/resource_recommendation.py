def recommend_resources(
    disaster_type,
    priority,
    affected_people,
    trapped_people,
    injured_people
):
    recommendations = []

    # Disaster-specific resources
    if disaster_type == "Flood":
        recommendations.extend([
            "Rescue Boat",
            "Life Jackets",
            "Water Rescue Team"
        ])

    elif disaster_type == "Cyclone":
        recommendations.extend([
            "Search and Rescue Team",
            "Emergency Medical Team",
            "Debris Clearance Team"
        ])

    elif disaster_type == "Landslide":
        recommendations.extend([
            "Search and Rescue Team",
            "Excavator",
            "Heavy Rescue Equipment"
        ])

    elif disaster_type == "Building Collapse":
        recommendations.extend([
            "Urban Search and Rescue Team",
            "Heavy Rescue Equipment",
            "Ambulance"
        ])

    # Priority-based resources
    if priority in ["High", "Critical"]:
        recommendations.append("Emergency Medical Team")

    if trapped_people > 0:
        recommendations.append("Search and Rescue Team")

    if injured_people > 0:
        recommendations.append("Ambulance")

    if affected_people >= 20:
        recommendations.append("Additional Rescue Personnel")

    if priority == "Critical":
        recommendations.append("Emergency Command Unit")

    # Remove duplicates while preserving order
    recommendations = list(dict.fromkeys(recommendations))

    return recommendations


if __name__ == "__main__":
    print("AI Resource Recommendation")
    print("--------------------------")

    disaster_type = input("Disaster type: ")
    priority = input("Priority: ")

    affected_people = int(input("Affected people: "))
    trapped_people = int(input("Trapped people: "))
    injured_people = int(input("Injured people: "))

    resources = recommend_resources(
        disaster_type,
        priority,
        affected_people,
        trapped_people,
        injured_people
    )

    print("\n--- Recommended Resources ---")

    for resource in resources:
        print("-", resource)