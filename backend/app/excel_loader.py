import json
import time

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from app.config import settings


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

CACHE_TTL_SECONDS = 30

_cached_inventory: pd.DataFrame | None = None
_cached_at = 0.0


def _get_credentials() -> Credentials:
    service_account_json = settings.GOOGLE_SERVICE_ACCOUNT_JSON

    if not service_account_json:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is not configured."
        )

    try:
        service_account_info = json.loads(service_account_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON contains invalid JSON."
        ) from exc

    try:
        if service_account_info.get("type") != "service_account":
            raise ValueError("the JSON must contain type=service_account")
        return Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Invalid GOOGLE_SERVICE_ACCOUNT_JSON: {exc}"
        ) from exc


def _fetch_sheet() -> pd.DataFrame:
    spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID

    if not spreadsheet_id:
        raise RuntimeError(
            "GOOGLE_SHEETS_SPREADSHEET_ID must be configured."
        )

    worksheet = settings.GOOGLE_SHEETS_WORKSHEET

    if not worksheet:
        raise RuntimeError(
            "GOOGLE_SHEETS_WORKSHEET must be configured."
        )

    try:
        worksheet = gspread.authorize(_get_credentials()).open_by_key(
            spreadsheet_id
        ).worksheet(worksheet)
        values = worksheet.get_all_values()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to read Google Sheet: {exc}"
        ) from exc

    header_index = settings.INVENTORY_HEADER_ROW - 1

    if len(values) <= header_index:
        raise ValueError(
            "Google Sheet does not contain the configured header row."
        )

    headers = [
        str(header).strip()
        for header in values[header_index]
    ]

    rows = values[header_index + 1 :]

    width = max(
        [
            len(headers),
            *(len(row) for row in rows),
        ],
        default=0,
    )

    headers.extend(
        f"Extra_{index}"
        for index in range(len(headers), width)
    )

    normalized_rows = [
        row + [None] * (width - len(row))
        for row in rows
    ]

    dataframe = pd.DataFrame(
        normalized_rows,
        columns=headers,
    )

    dataframe.rename(
        columns={
            "BHK/ Area": "BHK",
            "Rate": "Budget (Cr)",
            "Project name": "Project Name",
        },
        inplace=True,
    )

    dataframe.dropna(
        axis=0,
        how="all",
        inplace=True,
    )

    dataframe.dropna(
        axis=1,
        how="all",
        inplace=True,
    )

    if dataframe.empty:
        raise ValueError(
            "Google Sheet does not contain any property rows."
        )

    required_columns = {
        "Property Type",
        "BHK",
        "Budget (Cr)",
        "Location",
        "Status",
    }
    missing_columns = sorted(required_columns - set(dataframe.columns))
    if missing_columns:
        raise ValueError(
            "Missing required inventory column(s): "
            + ", ".join(missing_columns)
        )

    return dataframe.reset_index(drop=True)


def load_google_sheet(
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Load property inventory from Google Sheets.

    The inventory is cached for 30 seconds by default.
    force_refresh=True bypasses the cache.
    """

    global _cached_at
    global _cached_inventory

    now = time.monotonic()

    if (
        not force_refresh
        and _cached_inventory is not None
        and now - _cached_at < CACHE_TTL_SECONDS
    ):
        return _cached_inventory

    dataframe = _fetch_sheet()

    _cached_inventory = dataframe
    _cached_at = now

    return _cached_inventory


def load_inventory(force_refresh: bool = False) -> pd.DataFrame:
    """Load the configured property inventory for API routes."""
    return load_google_sheet(force_refresh=force_refresh)