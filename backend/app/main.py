from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, search
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(search.router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "message": "Property Matching Agent API is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }