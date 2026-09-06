from fastapi import APIRouter, Depends, HTTPException
from app.auth import require_authenticated_user
from app.models import SearchRequest, SearchResponse, FilterOptions
from app.google_sheets_loader import load_google_sheet
from app.matcher import run_match
from app.normalizer import normalize_bhk
import pandas as pd

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
def search_properties(req: SearchRequest, _: str = Depends(require_authenticated_user)):
    try:
        df = load_google_sheet()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    matches = run_match(df, req)
    return SearchResponse(
        success=True,
        total_matches=len(matches),
        matches=matches
    )

@router.get("/filters", response_model=FilterOptions)
def get_filters(_: str = Depends(require_authenticated_user)):
    try:
        df = load_google_sheet()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Extract unique values and clean them up
    # Keep original forms but deduplicate based on normalized values to present nicely
    
    def get_unique_options(col_name: str, is_bhk: bool = False):
        if col_name not in df.columns:
            return []
        
        raw_vals = df[col_name].dropna().unique()
        seen = set()
        unique_list = []
        
        for val in raw_vals:
            val_str = str(val).strip()
            if not val_str:
                continue
            
            # Use normalization to avoid duplicates (e.g., Hennur vs hennur)
            norm = val_str.lower()
            if norm not in seen:
                seen.add(norm)
                unique_list.append(val_str)
                
        if is_bhk:
            # Sort BHKs numerically if possible
            unique_list.sort(key=lambda x: normalize_bhk(x) or 0)
        else:
            unique_list.sort()
            
        return unique_list

    return FilterOptions(
        property_types=get_unique_options("Property Type"),
        bhks=get_unique_options("BHK", is_bhk=True),
        locations=get_unique_options("Location"),
        statuses=get_unique_options("Status")
    )


@router.post("/inventory/refresh")
def refresh_inventory(_: str = Depends(require_authenticated_user)):
    try:
        df = load_google_sheet(force_refresh=True)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    return {"success": True, "total_properties": len(df)}
