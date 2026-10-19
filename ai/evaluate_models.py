
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score
)

import matplotlib.pyplot as plt

from .extract_information import extract_information
from .analyze_report import refine_priority


# =====================================================
# CONFIGURATION
# =====================================================

DATA_PATH = "data/disaster_reports.csv"

DISASTER_MODEL_PATH = "ai/disaster_type_model.pkl"
PRIORITY_MODEL_PATH = "ai/priority_model.pkl"

RANDOM_STATE = 42
TEST_SIZE = 0.25


def create_model():
    """Create the same type of TF-IDF + Logistic Regression pipeline."""
    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english"
            )
        ),
        (
            "classifier",
            LogisticRegression(max_iter=1000)
        )
    ])


def evaluate_predictions(
    title,
    y_true,
    y_pred,
    labels,
    save_plot_name
):
    """Print evaluation metrics and display a confusion matrix."""

    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)

    print(f"Test records: {len(y_true)}")
    print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
    print(f"Macro F1-score: {f1_score(y_true, y_pred, average='macro', zero_division=0):.4f}")
    print(f"Weighted F1-score: {f1_score(y_true, y_pred, average='weighted', zero_division=0):.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0
        )
    )

    print("Confusion Matrix:")
    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )
    print(matrix)

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=labels
    )

    fig, ax = plt.subplots(figsize=(9, 7))
    display.plot(
        ax=ax,
        xticks_rotation=45,
        colorbar=False
    )
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(save_plot_name, dpi=150)
    print(f"Confusion matrix saved to: {save_plot_name}")
    plt.show()
    plt.close(fig)


# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv(DATA_PATH)

print("=" * 65)
print("AI DISASTER RESPONSE MODEL EVALUATION")
print("=" * 65)

print("Total dataset records:", len(df))
print("\nDisaster type distribution:")
print(df["disaster_type"].value_counts())

print("\nPriority label distribution, excluding missing labels:")
print(df["priority"].dropna().value_counts())


# =====================================================
# 1. DISASTER-TYPE MODEL
# =====================================================

print("\n\nEVALUATING DISASTER-TYPE CLASSIFICATION")

disaster_df = df.dropna(
    subset=["report", "disaster_type"]
).copy()

X = disaster_df["report"].astype(str)
y = disaster_df["disaster_type"].astype(str)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)

disaster_model = create_model()
disaster_model.fit(X_train, y_train)

disaster_predictions = disaster_model.predict(X_test)

disaster_labels = sorted(y.unique())

evaluate_predictions(
    title="Disaster-Type Model — Held-Out Test Set",
    y_true=y_test,
    y_pred=disaster_predictions,
    labels=disaster_labels,
    save_plot_name="disaster_type_confusion_matrix.png"
)

# Also check the existing saved model without modifying it.
print("\nChecking the existing saved disaster-type model...")

saved_disaster_model = joblib.load(DISASTER_MODEL_PATH)
saved_disaster_predictions = saved_disaster_model.predict(X_test)

evaluate_predictions(
    title="Saved Disaster-Type Model — Same Test Split",
    y_true=y_test,
    y_pred=saved_disaster_predictions,
    labels=disaster_labels,
    save_plot_name="saved_disaster_type_confusion_matrix.png"
)


# =====================================================
# 2. PRIORITY MODEL
# =====================================================

print("\n\nEVALUATING PRIORITY CLASSIFICATION")

# Fire rows currently have missing priority labels.
# Exclude only rows that lack the target label.
priority_df = df.dropna(
    subset=["report", "priority"]
).copy()

X_priority = priority_df["report"].astype(str)
y_priority = priority_df["priority"].astype(str)

priority_labels = ["Low", "Medium", "High", "Critical"]

X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(
    X_priority,
    y_priority,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y_priority
)

# Train a TEMPORARY model for a clean held-out evaluation.
# This model is never saved and does not overwrite the existing .pkl.
priority_model = create_model()
priority_model.fit(X_train_p, y_train_p)

raw_priority_predictions = priority_model.predict(X_test_p)

evaluate_predictions(
    title="Priority Model — Raw Predictions on Held-Out Test Set",
    y_true=y_test_p,
    y_pred=raw_priority_predictions,
    labels=priority_labels,
    save_plot_name="priority_raw_confusion_matrix.png"
)


# =====================================================
# 3. PRIORITY AFTER RULE-BASED REFINEMENT
# =====================================================

print("\n\nEVALUATING REFINED PRIORITY PREDICTIONS")

refined_priority_predictions = []

for report, raw_priority in zip(
    X_test_p,
    raw_priority_predictions
):
    information = extract_information(report)

    refined_priority = refine_priority(
        raw_priority,
        information["affected_people"],
        information["trapped_people"],
        information["injured_people"]
    )

    refined_priority_predictions.append(refined_priority)

# Show reports whose priority changed after refinement
print("\n" + "=" * 80)
print("REPORTS CHANGED BY PRIORITY REFINEMENT")
print("=" * 80)

for report, actual, raw, refined in zip(
    X_test_p,
    y_test_p,
    raw_priority_predictions,
    refined_priority_predictions
):
    if raw != refined:
        info = extract_information(report)

        print("\nReport:", report)
        print("Actual priority:", actual)
        print("Raw ML priority:", raw)
        print("Refined priority:", refined)
        print("Affected:", info["affected_people"])
        print("Trapped:", info["trapped_people"])
        print("Injured:", info["injured_people"])
        print("-" * 80)


evaluate_predictions(
    title="Priority Model — After Rule-Based Refinement",
    y_true=y_test_p,
    y_pred=refined_priority_predictions,
    labels=priority_labels,
    save_plot_name="priority_refined_confusion_matrix.png"
)


# =====================================================
# 4. DATA QUALITY SUMMARY
# =====================================================

print("\n\n" + "=" * 65)
print("EVALUATION SUMMARY")
print("=" * 65)

print("Total dataset rows:", len(df))
print("Disaster-type evaluation rows:", len(disaster_df))
print("Priority evaluation rows:", len(priority_df))
print("Rows without priority labels:", df["priority"].isna().sum())

print("\nFiles generated:")
print("- disaster_type_confusion_matrix.png")
print("- saved_disaster_type_confusion_matrix.png")
print("- priority_raw_confusion_matrix.png")
print("- priority_refined_confusion_matrix.png")

print("\nEvaluation completed.")
print("No model files were overwritten.")
