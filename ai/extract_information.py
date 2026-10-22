
import re


def extract_information(report):
    """
    Extract affected, trapped, and injured people from an
    emergency report.

    Supports numeric quantities (12) and word quantities (twelve).
    Handles common negations such as "nobody is trapped".
    """

    text = report.lower()

    # -----------------------------------
    # QUANTITY MAP
    # -----------------------------------

    quantity_map = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "few": 3,
        "several": 5,
        "many": 10
    }

    quantity_words = "|".join(
        sorted(quantity_map.keys(), key=len, reverse=True)
    )
    quantity_pattern = rf"(?:\d+|{quantity_words})"

    def get_quantity(value):
        """Convert a numeric or word quantity into an integer."""
        value = value.lower()

        if value.isdigit():
            return int(value)

        return quantity_map.get(value, 0)

    # -----------------------------------
    # TRAPPED / STRANDED / STUCK PEOPLE
    # -----------------------------------

    trapped = 0

    # Detect statements explicitly saying nobody is trapped.
    trapped_negation_patterns = [
        r"\bno\s+(?:people|persons|residents|victims|one|"
        r"family members|anyone)\b.{0,35}\b"
        r"(?:trapped|stranded|stuck)\b",

        r"\bnobody\b.{0,35}\b"
        r"(?:trapped|stranded|stuck)\b",

        r"\bno one\b.{0,35}\b"
        r"(?:trapped|stranded|stuck)\b",

        r"\b(?:nobody|no one)\s+"
        r"(?:is|was|has been|remains)\s+"
        r"(?:unable to escape|unable to leave)\b",

        r"\bno\s+(?:people|persons|residents|victims)\b"
        r".{0,35}\b(?:unable to escape|unable to leave)\b"
    ]

    trapped_is_negated = any(
        re.search(pattern, text)
        for pattern in trapped_negation_patterns
    )

    # Handle combined phrases such as:
    # "no injuries or people trapped"
    # "no injuries and nobody is trapped"
    # "no injuries, no people trapped"
    combined_negation_patterns = [
        r"\bno\s+injuries?\b.{0,40}\b(?:people|persons|residents|victims)?"
        r"\s*(?:are|were)?\s*(?:trapped|stranded|stuck)\b",

        r"\bno\s+injuries?\b.{0,40}\bno\s+"
        r"(?:people|persons|residents|victims|one|anyone)\b",

        r"\bno\s+(?:people|persons|residents|victims)\s+"
        r"(?:are\s+)?(?:trapped|stranded|stuck)\b"
    ]

    if any(
        re.search(pattern, text)
        for pattern in combined_negation_patterns
    ):
        trapped_is_negated = True

    # Only extract trapped people when the report does not
    # explicitly negate the trapped-person statement.
    if not trapped_is_negated:

        trapped_patterns = [
            # 12 people are trapped / twelve are trapped
            rf"\b({quantity_pattern})\s+"
            r"(?:(?:people|persons|residents|victims|families)\s+)?"
            r"(?:(?:are|were|remain|remain\s+currently)\s+)?"
            r"(?:trapped|stranded|stuck)\b",

            # 12 people are unable to escape
            rf"\b({quantity_pattern})\s+"
            r"(?:people|persons|residents|victims|families)\s+"
            r"(?:(?:are|were)\s+)?"
            r"(?:unable|not able)\s+to\s+(?:escape|leave|get out)\b",

            # 12 family members are trapped
            rf"\b({quantity_pattern})\s+"
            r"(?:family members|members of my family)\s+"
            r"(?:(?:are|were)\s+)?(?:trapped|stuck)\b"
        ]

        for pattern in trapped_patterns:
            match = re.search(pattern, text)

            if match:
                trapped = get_quantity(match.group(1))
                break

        # Family statements without a known number
        if trapped == 0:
            family_patterns = [
                r"\b(?:my|our)\s+family\s+(?:is|are|was|were)\s*"
                r"(?:trapped|stuck)\b",

                r"\b(?:my|our)\s+family\s+(?:is|are|was|were)\s*"
                r"(?:unable|not able)\s+to\s+(?:escape|leave|get out)\b"
            ]

            if any(
                re.search(pattern, text)
                for pattern in family_patterns
            ):
                trapped = 4  # Estimate only; actual family size unknown.

        # General trapped-person statements without a quantity
        if trapped == 0:
            general_trapped_patterns = [
                r"\b(?:people|persons|residents|victims)\s+"
                r"(?:(?:are|were)\s+)?(?:trapped|stranded|stuck)\b",

                r"\b(?:people|persons|residents|victims)\s+"
                r"(?:(?:are|were)\s+)?(?:unable|not able)\s+to\s+"
                r"(?:escape|leave|get out)\b"
            ]

            if any(
                re.search(pattern, text)
                for pattern in general_trapped_patterns
            ):
                trapped = 10  # Estimate only; actual count unknown.

    # -----------------------------------
    # INJURED PEOPLE
    # -----------------------------------

    injured = 0

    # Detect explicit statements that there are no injuries.
    injury_negation_patterns = [
        r"\bno\s+(?:people|persons|residents|victims|one|"
        r"injuries|injury|casualties)\b",

        r"\bno\s+(?:one|person)\s+"
        r"(?:is|was|has been)\s+injured\b",

        r"\bnobody\s+"
        r"(?:is|was|has been)\s+injured\b",

        r"\bno injuries\b"
    ]

    injuries_negated = any(
        re.search(pattern, text)
        for pattern in injury_negation_patterns
    )

    if not injuries_negated:
        injured_patterns = [
            # 5 people are injured / five people were injured
            rf"\b({quantity_pattern})\s+"
            r"(?:(?:people|persons|residents|victims)\s+)?"
            r"(?:(?:are|were|have been)\s+)?injured\b",

            # 5 people have injuries / suffered injuries
            rf"\b({quantity_pattern})\s+"
            r"(?:people|persons|residents|victims)\s+"
            r"(?:(?:have|has)\s+|(?:suffered|sustained)\s+)"
            r"(?:minor|major|serious|multiple)?\s*"
            r"(?:injuries|injury)\b",

            # 5 injured
            rf"\b({quantity_pattern})\s+injured\b",

            # 5 people have a serious injury
            rf"\b({quantity_pattern})\s+"
            r"(?:people|persons|residents|victims)\s+"
            r"(?:have|has)\s+(?:a|an)?\s*"
            r"(?:minor|major|serious)?\s*injury\b"
        ]

        for pattern in injured_patterns:
            match = re.search(pattern, text)

            if match:
                injured = get_quantity(match.group(1))
                break

        # Single-person injury
        if injured == 0:
            single_injury_patterns = [
                r"\b(?:one|a)\s+person\s+(?:is|was)\s+injured\b",

                r"\b(?:one|a)\s+person\s+"
                r"(?:has|had|suffered)\s+(?:a|an)?\s*"
                r"(?:minor|major|serious)?\s*injury\b"
            ]

            if any(
                re.search(pattern, text)
                for pattern in single_injury_patterns
            ):
                injured = 1

    # -----------------------------------
    # AFFECTED PEOPLE
    # -----------------------------------

    # Trapped people are also considered affected.
    affected = trapped

    affected_patterns = [
        rf"\b({quantity_pattern})\s+affected\b",
        # 20 people are affected
        rf"\b({quantity_pattern})\s+"
        r"(?:people|persons|residents|victims)\s+"
        r"(?:(?:are|were)\s+)?affected\b",

        # The disaster affected 20 people
        rf"\baffected\s+({quantity_pattern})\s+"
        r"(?:people|persons|residents|victims)\b",

        # 20 people have been affected
        rf"\b({quantity_pattern})\s+"
        r"(?:people|persons|residents|victims)\s+"
        r"(?:have|has)\s+been\s+affected\b",

        # 20 people are stranded or missing
        rf"\b({quantity_pattern})\s+"
        r"(?:people|persons|residents|victims)\s+"
        r"(?:(?:are|were)\s+)?(?:stranded|missing)\b",

        # 20 family members are missing
        rf"\b({quantity_pattern})\s+"
        r"(?:family members|family member|members of my family)\s+"
        r"(?:(?:are|were)\s+)?missing\b",

        # Lost 20 family members / missing 20 people
        rf"\b(?:lost|missing)\s+({quantity_pattern})\s+"
        r"(?:family members|family member|people|persons|"
        r"members of my family)\b"
    ]

    for pattern in affected_patterns:
        match = re.search(pattern, text)

        if match:
            affected = max(
                affected,
                get_quantity(match.group(1))
            )

    # Injured people are also affected.
    affected = max(affected, injured)

    # -----------------------------------
    # RETURN RESULT
    # -----------------------------------

    return {
        "affected_people": affected,
        "trapped_people": trapped,
        "injured_people": injured
    }


# -----------------------------------
# INTERACTIVE TESTING
# -----------------------------------

if __name__ == "__main__":
    print("Emergency Information Extraction")
    print("--------------------------------")

    report = input("Enter emergency report: ")
    result = extract_information(report)

    print("\n--- Extracted Information ---")
    print("Affected people:", result["affected_people"])
    print("Trapped people:", result["trapped_people"])
    print("Injured people:", result["injured_people"])

    print("\n--- Automatic Tests ---")

    test_reports = [
        "12 people are trapped inside a flooded house",
        "Twelve people are trapped inside a flooded house",
        "Five people are injured after a cyclone",
        "Three people are affected by a flood",
        "Several residents are stranded",
        "A person is injured in a fire",
        "Small fire, no injuries or people trapped",
        "Nobody is trapped after the flood",
        "No one is injured and no people are trapped",
        "Severe flooding has affected twenty people. "
        "Five people are trapped and two people are injured"
    ]

    for test_report in test_reports:
        print("\nReport:", test_report)
        print("Result:", extract_information(test_report))
