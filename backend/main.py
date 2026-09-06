from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, search
from app.config import settings
from app.excel_loader import load_inventory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Property Matching Agent Backend")

# Setup CORS so the Next.js frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup validation and loading
@app.on_event("startup")
def startup_event():
    logger.info("Initializing application and loading Excel spreadsheet...")
    try:
        df = load_inventory()
        logger.info(f"Successfully loaded spreadsheet with {len(df)} rows.")
    except Exception as e:
        logger.error(f"STARTUP ERROR: {str(e)}")
        # Raise exception to stop server from booting with invalid configuration
        raise e

# Include routes
app.include_router(auth.router, prefix="/api")
app.include_router(search.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Property Matching Agent API is running."}
