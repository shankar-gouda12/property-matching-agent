from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class SearchRequest(BaseModel):
    property_type: Optional[str] = None
    bhk: Optional[Union[int, str]] = None
    budget_cr: Optional[float] = None
    location: Optional[str] = None
    status: Optional[str] = None
    mode: str = Field(default="STRICT")


class PropertyMatch(BaseModel):
    score: str
    details: Dict[str, Any]
    match_details: Dict[str, bool]


class SearchResponse(BaseModel):
    success: bool
    total_matches: int
    matches: List[PropertyMatch]


class FilterOptions(BaseModel):
    property_types: List[str]
    bhks: List[str]
    locations: List[str]
    statuses: List[str]