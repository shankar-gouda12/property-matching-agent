import re
import pandas as pd


def normalize_text(value) -> str:
    """
    Normalize general text:
    - Handles empty/NaN values
    - Converts to lowercase
    - Removes extra spaces
    - Removes surrounding spaces
    """

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return " ".join(
        str(value).strip().lower().split()
    )


def normalize_bhk(value) -> int | None:
    """
    Converts:
        2
        2.0
        2 BHK
        2BHK
        2-BHK
        2 bhk

    into:

        2
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    text = str(value).strip()

    match = re.search(r"\d+", text)

    if match:
        return int(match.group())

    return None


def normalize_budget(value) -> float | None:
    """
    Converts property prices into Crores.

    Examples:

        0.75
        ₹0.75 Cr
        0.75 Crore
        75 Lakhs
        ₹75 Lakh

    Results:

        0.75
        0.75
        0.75
        0.75
        0.75
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    text = (
        str(value)
        .lower()
        .replace("₹", "")
        .replace(",", "")
        .strip()
    )

    # Extract number
    match = re.search(
        r"\d+(?:\.\d+)?",
        text
    )

    if not match:
        return None

    number = float(match.group())

    # Lakhs / Lakh / Lac / Lacs
    if re.search(
        r"\b(lakh|lakhs|lac|lacs|l)\b",
        text
    ):
        return number / 100

    # Crores / Crore / Cr
    if re.search(
        r"\b(crore|crores|cr|c)\b",
        text
    ):
        return number

    # If there is no unit, assume value is already in Crores
    return number


def normalize_location(value) -> str:
    """
    Normalizes common location variations.

    Examples:

        Hennur
        HENNUR
        Hennur Road
        Hennur Rd
        Hennur, Bangalore

    """

    normalized = normalize_text(value)

    if not normalized:
        return ""

    # Remove common road suffixes
    normalized = re.sub(
        r"\broad\b",
        "",
        normalized
    )

    normalized = re.sub(
        r"\brd\b",
        "",
        normalized
    )

    # Remove common city suffixes
    normalized = re.sub(
        r",?\s*\b(bangalore|bengaluru)\b$",
        "",
        normalized
    )

    # Remove duplicate spaces
    normalized = " ".join(
        normalized.split()
    )

    return normalized.strip()


def normalize_property_type(value) -> str:
    """
    Normalizes property types.

    Apartment / apartment / APARTMENT
    Villa / villa
    Plot / plot
    """

    normalized = normalize_text(value)

    # Common aliases
    aliases = {
        "flat": "apartment",
        "flats": "apartment",
        "apt": "apartment",
        "apts": "apartment",
    }

    return aliases.get(
        normalized,
        normalized
    )


def normalize_status(value) -> str:
    """
    Normalizes property status.
    """

    normalized = normalize_text(value)

    # Convert common variations
    aliases = {
        "ready": "ready to move",
        "ready-to-move": "ready to move",
        "ready to move in": "ready to move",
        "under construction": "under construction",
        "uc": "under construction",
    }

    return aliases.get(
        normalized,
        normalized
    )