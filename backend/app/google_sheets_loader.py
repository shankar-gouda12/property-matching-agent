import json
import time

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.config import settings

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
CACHE_TTL_SECONDS = 30

_cached_inventory: pd.DataFrame | None = None
_cached_at = 0.0


def _get_credentials() -> Credentials:
    token_json = settings.GOOGLE_TOKEN_JSON

    if not token_json:
        raise RuntimeError(
            "GOOGLE_TOKEN_JSON is not configured."
        )

    try:
        token_info = json.loads(token_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "GOOGLE_TOKEN_JSON contains invalid JSON."
        ) from exc

    credentials = Credentials.from_authorized_user_info(
        token_info,
        SCOPES,
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials.valid:
        raise RuntimeError(
            "Google OAuth credentials are invalid or expired."
        )

    return credentials


def _fetch_sheet() -> pd.DataFrame:
    if not settings.GOOGLE_SHEETS_SPREADSHEET_ID:
        raise RuntimeError(
            "GOOGLE_SHEETS_SPREADSHEET_ID must be configured."
        )

    service = build(
        "sheets",
        "v4",
        credentials=_get_credentials(),
        cache_discovery=False,
    )

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            range=f"{settings.GOOGLE_SHEETS_WORKSHEET}!A:Z",
        )
        .execute()
    )

    values = result.get("values", [])

    header_index = settings.INVENTORY_HEADER_ROW - 1

    if len(values) <= header_index:
        raise ValueError(
            "Google Sheet does not contain the configured header row."
        )

    rows = values[header_index + 1:]

    width = max(
        [len(values[header_index]), *(len(row) for row in rows)],
        default=0,
    )

    headers = [
        str(header).strip()
        for header in values[header_index]
    ]

    headers.extend(
        f"Extra_{index}"
        for index in range(len(headers), width)
    )

    rows = [
        row + [None] * (width - len(row))
        for row in rows
    ]

    dataframe = pd.DataFrame(
        rows,
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

    return dataframe.reset_index(drop=True)


def load_google_sheet(
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Return Google Sheet inventory.

    The deployed function refreshes its in-memory cache
    at most every 30 seconds.
    """
    global _cached_at, _cached_inventory

    now = time.monotonic()

    if (
        not force_refresh
        and _cached_inventory is not None
        and now - _cached_at < CACHE_TTL_SECONDS
    ):
        return _cached_inventory

    _cached_inventory = _fetch_sheet()
    _cached_at = now

    return _cached_inventory