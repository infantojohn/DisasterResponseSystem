import pandas as pd
import random

random.seed(42)

# Load original dataset
file_path = "data/disaster_reports.csv"
df_original = pd.read_csv(file_path)

# Templates for generating varied emergency reports
templates = {
    "Flood": {
        "Low": [
            "Minor flooding reported near {} with no casualties",
            "Light waterlogging observed around {}",
            "Small amount of flood water reported near {}",
            "Flood water has reached the roadside near {} but no injuries reported",
            "Minor flooding affecting a few houses near {}",
        ],
        "Medium": [
            "Flood water has entered several houses near {}",
            "Moderate flooding reported in {} and some residents need assistance",
            "Rising flood water is affecting homes around {}",
            "Several roads are blocked by flood water near {}",
            "Flooding has disrupted movement in {} and residents are stranded",
        ],
        "High": [
            "Rapidly rising flood water has stranded families near {}",
            "Several residents are unable to leave their homes because of flooding in {}",
            "Flood water has isolated a residential area near {}",
            "People are stranded on rooftops after severe flooding in {}",
            "Major flooding has blocked access to several houses in {}",
        ],
        "Critical": [
            "Many people are trapped inside flooded houses in {} and several are injured",
            "Severe flooding has trapped families inside buildings near {}",
            "Flood water has entered a school in {} and many students are stranded",
            "Several people are trapped by rapidly rising flood water in {}",
            "Major flooding has submerged houses in {} and injured residents",
        ],
    },

    "Cyclone": {
        "Low": [
            "Light cyclone damage reported in {} with no casualties",
            "Strong winds caused minor roof damage near {}",
            "Minor cyclone damage reported around {}",
            "A few trees were damaged by cyclone winds near {}",
            "Light rain and winds reported in {} with no injuries",
        ],
        "Medium": [
            "Strong cyclone winds damaged several roofs in {}",
            "Cyclone conditions have damaged homes around {}",
            "Heavy rain and strong winds are affecting residents in {}",
            "Several roads are blocked by cyclone debris in {}",
            "Moderate cyclone damage reported in {} and residents need assistance",
        ],
        "High": [
            "Severe cyclone winds damaged houses and injured residents in {}",
            "Several people were injured by falling debris during the cyclone in {}",
            "Strong cyclone winds have damaged multiple buildings in {}",
            "Cyclone debris has blocked roads and injured several people near {}",
            "Severe winds have left several families stranded in {}",
        ],
        "Critical": [
            "Severe cyclone has destroyed houses and trapped several residents in {}",
            "Extremely strong winds have trapped families inside damaged houses in {}",
            "Cyclone damage has caused multiple injuries and trapped people in {}",
            "Several buildings collapsed during the cyclone and people are trapped in {}",
            "A major cyclone has caused widespread destruction and trapped residents in {}",
        ],
    },

    "Landslide": {
        "Low": [
            "Small rocks have fallen onto the road near {}",
            "Minor landslide reported on a local road near {}",
            "Small rockfall has partially blocked a road in {}",
            "Light soil movement reported near {} with no injuries",
            "Minor landslide debris is blocking part of the road near {}",
        ],
        "Medium": [
            "Heavy rain caused a landslide near several houses in {}",
            "A moderate landslide has blocked a road near {}",
            "Landslide debris has affected several houses in {}",
            "A landslide has disrupted road access around {}",
            "Several residents are affected by a landslide near {}",
        ],
        "High": [
            "Large landslide has blocked the highway near {} and people are stranded",
            "Major landslide has isolated a village near {}",
            "Several houses are threatened by a large landslide in {}",
            "Landslide debris has blocked the main road and stranded residents in {}",
            "A major landslide has isolated several families near {}",
        ],
        "Critical": [
            "Major landslide buried houses and several people are trapped in {}",
            "Large landslide has buried buildings and trapped residents near {}",
            "Several people are trapped under landslide debris in {}",
            "A massive landslide has destroyed houses and injured residents in {}",
            "Landslide debris has buried homes and trapped multiple people near {}",
        ],
    },

    "Building Collapse": {
        "Low": [
            "Old wall collapsed near {} but nobody was injured",
            "Minor structural damage reported at a building in {}",
            "A small section of a wall collapsed in {} with no casualties",
            "Part of an old structure collapsed near {} without injuries",
            "Minor building damage reported in {} with no trapped people",
        ],
        "Medium": [
            "A wall collapsed and one person was injured in {}",
            "Part of a building collapsed near {} causing minor injuries",
            "A building has partially collapsed in {} and residents need assistance",
            "Structural damage reported at a building in {} with one injured person",
            "A damaged building partially collapsed in {}",
        ],
        "High": [
            "A building partially collapsed and several people were injured in {}",
            "Several people are injured after a building collapse in {}",
            "A collapsed structure has injured residents and blocked access in {}",
            "Part of a building collapsed and residents are trapped near {}",
            "Building debris has injured several people in {}",
        ],
        "Critical": [
            "Building collapsed and many people are trapped under the debris in {}",
            "Several people are trapped after a major building collapse in {}",
            "A large building has collapsed and injured people are trapped inside {}",
            "Multiple people are trapped under a collapsed structure in {}",
            "Major building collapse has buried residents under debris in {}",
        ],
    },
}

# Locations used only to make the reports more varied
locations = [
    "a residential area",
    "a village",
    "the coastal region",
    "a nearby town",
    "a rural area",
    "the city outskirts",
    "a highway area",
    "a densely populated neighborhood",
    "a low-lying area",
    "a remote village",
    "the local district",
    "a market area",
    "a school zone",
    "a roadside settlement",
    "a hill-side village",
    "the town center",
]

new_records = []

# Generate 20 records for each disaster type + priority combination
for disaster_type in templates:
    for priority in templates[disaster_type]:
        for i in range(20):
            template = random.choice(templates[disaster_type][priority])
            location = random.choice(locations)

            report = template.format(location)

            # Generate realistic numerical information
            if priority == "Low":
                affected = random.randint(0, 5)
                trapped = 0
                injured = 0

            elif priority == "Medium":
                affected = random.randint(3, 12)
                trapped = random.randint(0, 2)
                injured = random.randint(0, 2)

            elif priority == "High":
                affected = random.randint(8, 25)
                trapped = random.randint(2, 10)
                injured = random.randint(1, 6)

            else:  # Critical
                affected = random.randint(15, 40)
                trapped = random.randint(8, 25)
                injured = random.randint(3, 10)

            new_records.append({
                "report": report,
                "disaster_type": disaster_type,
                "affected_people": affected,
                "trapped_people": trapped,
                "injured_people": injured,
                "priority": priority
            })

# Convert generated data to DataFrame
df_new = pd.DataFrame(new_records)

# Combine original + generated records
df_final = pd.concat(
    [df_original, df_new],
    ignore_index=True
)

# Remove exact duplicate reports if any
df_final = df_final.drop_duplicates(subset=["report"]).reset_index(drop=True)

# Save expanded dataset
df_final.to_csv(file_path, index=False)

print("\n--- Dataset Expanded Successfully ---")
print("Original records:", len(df_original))
print("Generated records:", len(df_new))
print("Final records:", len(df_final))

print("\nDisaster type distribution:")
print(df_final["disaster_type"].value_counts())

print("\nPriority distribution:")
print(df_final["priority"].value_counts())

print("\nMissing values:")
print(df_final.isnull().sum())