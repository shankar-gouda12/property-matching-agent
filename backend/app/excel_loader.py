from app.google_sheets_loader import load_google_sheet


def load_inventory(
    force_refresh: bool = False,
):
    """
    Compatibility wrapper.

    Inventory is loaded exclusively from Google Sheets.
    """

    return load_google_sheet(
        force_refresh=force_refresh
    )