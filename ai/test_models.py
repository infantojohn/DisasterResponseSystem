import joblib

# Load trained models
priority_model = joblib.load("ai/priority_model.pkl")
disaster_model = joblib.load("ai/disaster_type_model.pkl")

print("AI Disaster Report Analysis")
print("---------------------------")

report = input("Enter emergency report: ")

# Predictions
priority = priority_model.predict([report])[0]
disaster_type = disaster_model.predict([report])[0]

print("\n--- AI Analysis Result ---")
print("Disaster Type:", disaster_type)
print("Priority:", priority)