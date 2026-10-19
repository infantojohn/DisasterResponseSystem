
from ai.analyze_report import (
    analyze_report,
    priority_model,
    disaster_model,
    refine_priority,
)
from ai.extract_information import extract_information


cases = [
    (
        "LOW",
        "A small fire in an empty storage shed. "
        "The fire is contained, nobody is injured, "
        "and nobody is trapped."
    ),
    (
        "MEDIUM",
        "A fire broke out in a house. Three people suffered "
        "minor injuries. Nobody is trapped."
    ),
    (
        "HIGH",
        "Flood water has affected eight people in a residential "
        "area. Nobody is trapped or injured."
    ),
    (
        "CRITICAL",
        "Severe flooding has affected twenty people. "
        "Five people are trapped and two people are injured."
    ),
]


print("=" * 55)
print("DISASTER RESPONSE - PRIORITY DIAGNOSTIC")
print("=" * 55)

for number, (expected, report) in enumerate(cases, start=1):
    print(f"\n{'=' * 55}")
    print(f"TEST {number}: Expected {expected}")
    print("Report:", report)

    try:
        # 1. Check the raw ML predictions
        raw_priority = priority_model.predict([report])[0]
        raw_disaster = disaster_model.predict([report])[0]

        # 2. Check the extracted people counts
        information = extract_information(report)

        affected = information["affected_people"]
        trapped = information["trapped_people"]
        injured = information["injured_people"]

        # 3. Check the rule-based refinement independently
        refined_priority = refine_priority(
            raw_priority,
            affected,
            trapped,
            injured,
        )

        # 4. Run the complete AI pipeline
        result = analyze_report(report)
        actual = result["priority"]

        print("\n--- Raw ML Predictions ---")
        print("Priority:", raw_priority)
        print("Disaster type:", raw_disaster)

        print("\n--- Extracted Information ---")
        print("Affected:", affected)
        print("Trapped:", trapped)
        print("Injured:", injured)

        print("\n--- Priority Refinement ---")
        print("Priority after refinement:", refined_priority)

        print("\n--- Complete AI Pipeline ---")
        print("Final priority:", actual)
        print("Final disaster type:", result["disaster_type"])

        print("\n--- Test Result ---")
        if actual.lower() == expected.lower():
            print("PASS")
        else:
            print("FAIL")

    except Exception as error:
        print("\nERROR:", type(error).__name__, error)

print(f"\n{'=' * 55}")
print("DIAGNOSTIC COMPLETE")
print("=" * 55)
