import json
import time

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from app.config import settings

_inventory_df: pd.DataFrame | None = None
_inventory_version: float | None = None
_last_loaded_at = 0.0

REQUIRED_COLUMNS = [
    "Property Type",
    "BHK",
    "Budget (Cr)",
    "Location",
    "Status",
]
GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise ValueError("Inventory source is empty.")

    df.columns = [
        str(col).strip()
        if not str(col).startswith("Unnamed")
        else f"Extra_{i}"
        for i, col in enumerate(df.columns)
    ]

    df.rename(columns={
        "BHK/ Area": "BHK",
        "Rate": "Budget (Cr)",
        "Project name": "Project Name",
    }, inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    df.dropna(axis=0, how="all", inplace=True)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required inventory column(s): {', '.join(missing)}")
    return df.reset_index(drop=True)


def _load_excel() -> tuple[pd.DataFrame, float]:
    file_path = settings.INVENTORY_FILE_PATH
    if not file_path.exists():
        raise FileNotFoundError(f"Excel inventory file not found at: {file_path}")
    try:
        df = pd.read_excel(file_path, header=settings.INVENTORY_HEADER_ROW - 1, engine="openpyxl")
    except Exception as error:
        raise RuntimeError(f"Failed to read Excel file: {error}") from error
    return _clean_and_validate(df), file_path.stat().st_mtime


def _load_google_sheet() -> pd.DataFrame:
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is required when using Google Sheets.")
    try:
        credentials = Credentials.from_service_account_info(
            json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON), scopes=GOOGLE_SHEETS_SCOPES
        )
        worksheet = gspread.authorize(credentials).open_by_key(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID
        ).worksheet(settings.GOOGLE_SHEETS_WORKSHEET)
        values = worksheet.get_all_values()
    except Exception as error:
        raise RuntimeError(f"Failed to read Google Sheet: {error}") from error
    header_index = settings.INVENTORY_HEADER_ROW - 1
    if len(values) <= header_index:
        raise ValueError("Google Sheet does not contain the configured header row.")
    return _clean_and_validate(pd.DataFrame(values[header_index + 1:], columns=values[header_index]))


def load_inventory(force_refresh: bool = False) -> pd.DataFrame:
    """Load from Google Sheets when configured, otherwise use the local Excel file."""
    global _inventory_df, _inventory_version, _last_loaded_at
    use_google_sheets = bool(settings.GOOGLE_SHEETS_SPREADSHEET_ID)
    now = time.monotonic()
    if use_google_sheets:
        if not force_refresh and _inventory_df is not None and now - _last_loaded_at < settings.INVENTORY_REFRESH_SECONDS:
            return _inventory_df
        df, version = _load_google_sheet(), now
    else:
        df, version = _load_excel()
        if not force_refresh and _inventory_df is not None and _inventory_version == version:
            return _inventory_df

    _inventory_df, _inventory_version, _last_loaded_at = df, version, now
    print(f"Inventory loaded: {len(df)} properties from {'Google Sheets' if use_google_sheets else 'Excel'}")
    return _inventory_df
