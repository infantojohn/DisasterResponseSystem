import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load dataset
df = pd.read_csv("data/disaster_reports.csv")

# Load disaster type model
disaster_model = joblib.load("ai/disaster_type_model.pkl")


def find_related_reports(new_report, threshold=0.35):

    # Predict disaster type
    predicted_type = disaster_model.predict([new_report])[0]

    # Only compare reports from the same disaster type
    filtered_df = df[
        df["disaster_type"] == predicted_type
    ].reset_index(drop=True)

    reports = filtered_df["report"].tolist()

    if not reports:
        return predicted_type, []

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english"
    )

    report_vectors = vectorizer.fit_transform(reports)

    # Vectorize new report
    new_vector = vectorizer.transform([new_report])

    # Calculate similarity
    similarities = cosine_similarity(
        new_vector,
        report_vectors
    )[0]

    matches = []

    for i, score in enumerate(similarities):

        if score >= threshold:
            matches.append({
                "report": reports[i],
                "similarity": round(float(score), 3),
                "disaster_type": filtered_df.iloc[i]["disaster_type"],
                "priority": filtered_df.iloc[i]["priority"]
            })

    matches.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return predicted_type, matches


if __name__ == "__main__":
    print("Duplicate / Related Incident Detection")
    print("---------------------------------------")

    new_report = input("Enter new emergency report: ")

    predicted_type, matches = find_related_reports(new_report)

    print("\nPredicted Disaster Type:", predicted_type)

    print("\n--- Related Reports ---")

    if matches:
        for match in matches[:5]:
            print("\nSimilarity:", match["similarity"])
            print("Disaster Type:", match["disaster_type"])
            print("Priority:", match["priority"])
            print("Report:", match["report"])
    else:
        print("No closely related reports found.")