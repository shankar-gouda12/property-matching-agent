import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings:
    PROJECT_NAME = "Property Matching Agent"
    INVENTORY_FILE_PATH = Path(os.getenv("INVENTORY_FILE_PATH", Path(__file__).parent / "Inventory.xlsx"))
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
    GOOGLE_SHEETS_WORKSHEET = os.getenv("GOOGLE_SHEETS_WORKSHEET", "Sheet1")
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    INVENTORY_HEADER_ROW = int(os.getenv("INVENTORY_HEADER_ROW", "2"))
    INVENTORY_REFRESH_SECONDS = int(os.getenv("INVENTORY_REFRESH_SECONDS", "30"))
    AUTH_USERS = os.getenv("AUTH_USERS", "")
    AUTH_JWT_SECRET = os.getenv("AUTH_JWT_SECRET", "")
    AUTH_TOKEN_EXPIRE_MINUTES = int(os.getenv("AUTH_TOKEN_EXPIRE_MINUTES", "480"))
    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]


settings = Settings()
