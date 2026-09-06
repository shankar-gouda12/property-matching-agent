import pandas as pd
from typing import List
from app.models import SearchRequest, PropertyMatch
from app.normalizer import (
    normalize_property_type,
    normalize_bhk,
    normalize_budget,
    normalize_location,
    normalize_status
)


def run_match(
    df: pd.DataFrame,
    req: SearchRequest
) -> List[PropertyMatch]:

    results = []

    # Normalize user input
    req_type = (
        normalize_property_type(req.property_type)
        if req.property_type
        else None
    )

    req_bhk = req.bhk if req.bhk is not None else None

    req_budget = (
        float(req.budget_cr)
        if req.budget_cr is not None
        else None
    )

    req_loc = (
        normalize_location(req.location)
        if req.location
        else None
    )

    req_status = (
        normalize_status(req.status)
        if req.status
        else None
    )

    for _, row in df.iterrows():

        match_details = {
            "property_type": True,
            "bhk": True,
            "budget": True,
            "location": True,
            "status": True
        }

        # -----------------------------------
        # 1. PROPERTY TYPE
        # -----------------------------------

        if req_type:
            row_type = normalize_property_type(
                row.get("Property Type")
            )

            if row_type != req_type:
                match_details["property_type"] = False

        # -----------------------------------
        # 2. BHK
        # -----------------------------------

        if req_bhk is not None:
            row_bhk = normalize_bhk(row.get("BHK"))

            if row_bhk != req_bhk:
                match_details["bhk"] = False

        # -----------------------------------
        # 3. BUDGET
        # User budget is MAXIMUM budget
        # -----------------------------------

        if req_budget is not None:

            row_budget = normalize_budget(
                row.get("Budget (Cr)")
            )

            if row_budget is None:
                match_details["budget"] = False

            elif row_budget > req_budget:
                match_details["budget"] = False

        # -----------------------------------
        # 4. LOCATION
        # -----------------------------------

        if req_loc:
            row_loc = normalize_location(
                row.get("Location")
            )

            if row_loc != req_loc:
                match_details["location"] = False

        # -----------------------------------
        # 5. STATUS
        # -----------------------------------

        if req_status:
            row_status = normalize_status(
                row.get("Status")
            )

            if row_status != req_status:
                match_details["status"] = False

        # -----------------------------------
        # SCORE
        # -----------------------------------

        score_val = sum(
            1 for value in match_details.values()
            if value
        )

        score_str = f"{score_val}/5"

        # -----------------------------------
        # CONVERT EXCEL ROW TO JSON-SAFE DATA
        # -----------------------------------

        details = {}

        for col in df.columns:
            val = row[col]

            if pd.isna(val):
                details[col] = None
            elif hasattr(val, "item"):
                details[col] = val.item()
            else:
                details[col] = val

        # -----------------------------------
        # STRICT MODE
        # -----------------------------------

        if req.mode and req.mode.upper() == "STRICT":

            if score_val != 5:
                continue

        # -----------------------------------
        # FLEXIBLE MODE
        # -----------------------------------

        elif req.mode and req.mode.upper() == "FLEXIBLE":

            if score_val < 3:
                continue

        # -----------------------------------
        # ADD MATCH
        # -----------------------------------

        results.append(
            PropertyMatch(
                score=score_str,
                details=details,
                match_details=match_details
            )
        )

    # Highest matches first
    results.sort(
        key=lambda x: int(x.score.split("/")[0]),
        reverse=True
    )

    return results