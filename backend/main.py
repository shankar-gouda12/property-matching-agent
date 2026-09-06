from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, search
from app.config import settings
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

# Include routes
app.include_router(auth.router, prefix="/api")
app.include_router(search.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Property Matching Agent API is running."}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)
