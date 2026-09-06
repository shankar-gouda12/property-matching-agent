from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_authenticated_user
from app.google_sheets_loader import load_google_sheet
from app.matcher import run_match
from app.models import (
    FilterOptions,
    SearchRequest,
    SearchResponse,
)
from app.normalizer import normalize_bhk


router = APIRouter()


@router.post(
    "/search",
    response_model=SearchResponse,
)
def search_properties(
    req: SearchRequest,
    _: str = Depends(require_authenticated_user),
):
    try:
        df = load_google_sheet()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    matches = run_match(
        df,
        req,
    )

    return SearchResponse(
        success=True,
        total_matches=len(matches),
        matches=matches,
    )


@router.get(
    "/filters",
    response_model=FilterOptions,
)
def get_filters(
    _: str = Depends(require_authenticated_user),
):
    try:
        df = load_google_sheet()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    def get_unique_options(
        column_name: str,
        is_bhk: bool = False,
    ):
        if column_name not in df.columns:
            return []

        raw_values = (
            df[column_name]
            .dropna()
            .unique()
        )

        seen = set()
        unique_list = []

        for value in raw_values:
            value_string = str(value).strip()

            if not value_string:
                continue

            normalized = value_string.lower()

            if normalized not in seen:
                seen.add(normalized)
                unique_list.append(value_string)

        if is_bhk:
            unique_list.sort(
                key=lambda value: normalize_bhk(value) or 0
            )
        else:
            unique_list.sort()

        return unique_list

    return FilterOptions(
        property_types=get_unique_options(
            "Property Type"
        ),
        bhks=get_unique_options(
            "BHK",
            is_bhk=True,
        ),
        locations=get_unique_options(
            "Location"
        ),
        statuses=get_unique_options(
            "Status"
        ),
    )


@router.post(
    "/inventory/refresh"
)
def refresh_inventory(
    _: str = Depends(require_authenticated_user),
):
    try:
        df = load_google_sheet(
            force_refresh=True
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    return {
        "success": True,
        "total_properties": len(df),
    }