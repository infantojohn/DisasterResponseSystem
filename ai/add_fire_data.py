
import pandas as pd

# Load the existing dataset without deleting any categories.
df = pd.read_csv("data/disaster_reports.csv")

# Additional Fire examples, including small and contained fires.
fire_reports = [
    "A small fire started in an empty storage shed.",
    "A small fire in an empty storage shed. The fire is contained, nobody is injured, and nobody is trapped.",
    "Small fire, no injuries or people trapped.",
    "A small fire broke out in an empty warehouse and was quickly contained.",
    "A minor fire started in a kitchen and was extinguished immediately.",
    "A small electrical fire was contained before it spread.",
    "A small fire started in an unoccupied building.",
    "A waste bin caught fire, but the flames were quickly extinguished.",
    "A small fire started in a storage room with no one inside.",
    "A minor kitchen fire caused smoke but no injuries.",
    "A small fire was reported in a garage with no injuries.",
    "A small fire started in an empty shop after closing time.",
    "A small electrical fire occurred with no injuries or trapped people.",
    "A cooking fire was extinguished before spreading to other rooms.",
    "A small fire in a shed was contained by a nearby resident.",
    "A fire broke out in a house, but everyone escaped safely.",
    "A small fire started in a room and was quickly put out.",
    "A minor fire occurred in a storage building with no casualties.",
    "A small fire was reported near a residential building.",
    "A contained fire occurred in a kitchen with no trapped people.",
    "A fire started in an electrical socket and was quickly extinguished.",
    "A small fire was reported in an empty office.",
    "A minor fire occurred in a shop without injuries.",
    "A small fire was extinguished before emergency services arrived.",
    "A fire started in a cooking pan but did not spread.",
    "A small fire broke out in a garden shed.",
    "A fire alarm was triggered by a small contained fire.",
    "A small fire occurred in a storage area with no people affected.",
    "A minor fire in an empty building was quickly brought under control.",
    "A small fire started in a trash container and was put out."
]

# Remove only duplicate reports that are already labeled Fire.
existing_fire = df.loc[
    df["disaster_type"].astype(str).str.strip().str.lower() == "fire",
    "report"
].astype(str).str.strip().str.lower()

existing_fire_set = set(existing_fire)

new_reports = [
    report for report in fire_reports
    if report.strip().lower() not in existing_fire_set
]

new_fire_df = pd.DataFrame({
    "report": new_reports,
    "disaster_type": ["Fire"] * len(new_reports)
})

# Preserve every existing record and append only new examples.
df = pd.concat([df, new_fire_df], ignore_index=True)

# Remove exact duplicate report/type pairs across the whole dataset.
df["report"] = df["report"].astype(str).str.strip()
df["disaster_type"] = df["disaster_type"].astype(str).str.strip()

df = df.drop_duplicates(
    subset=["report", "disaster_type"]
).reset_index(drop=True)

# Save the updated dataset.
df.to_csv("data/disaster_reports.csv", index=False)

print("Dataset updated successfully!")
print("New Fire examples added:", len(new_reports))
print("Total records:", len(df))
print("\nRecords per disaster type:")
print(df["disaster_type"].value_counts().to_string())
