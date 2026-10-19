import pandas as pd

file_path = "data/disaster_reports.csv"

df = pd.read_csv(file_path)

print("\n--- Dataset Loaded Successfully ---")

print("\nNumber of records:")

print(len(df))

print("\nColumns:")

print(df.columns.tolist())

print("\nFirst 5 records:")

print(df.head())

print("\nPriority distribution:")

print(df["priority"].value_counts())

print("\nMissing values:")

print(df.isnull().sum())