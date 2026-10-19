import joblib

# Load trained model
model = joblib.load("ai/priority_model.pkl")

print("AI Priority Prediction")
print("-----------------------")

report = input("Enter emergency report: ")

prediction = model.predict([report])[0]

print("\nPredicted Priority:", prediction)