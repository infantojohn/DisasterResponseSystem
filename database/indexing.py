from connection import db


# Get incidents collection
incidents_collection = db["incidents"]


def create_indexes():
    print("\n--- Creating MongoDB Indexes ---")

    # Index for severity
    severity_index = incidents_collection.create_index("severity")
    print("Severity index:", severity_index)

    # Index for status
    status_index = incidents_collection.create_index("status")
    print("Status index:", status_index)

    # Index for disaster type
    disaster_index = incidents_collection.create_index("disaster_type")
    print("Disaster type index:", disaster_index)

    # Index for creation time
    created_index = incidents_collection.create_index("created_at")
    print("Created-at index:", created_index)

    print("\nAll indexes created successfully!")

    print("\n--- Current Indexes ---")
    for index in incidents_collection.list_indexes():
        print(index)


if __name__ == "__main__":
    create_indexes()