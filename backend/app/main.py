from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, videos, circuits

settings = get_settings()

app = FastAPI(
    title="Kilter Up API",
    description="AI-powered climbing video form analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — permissive in dev, restricted in prod
origins = (
    ["*"]
    if settings.environment == "development"
    else [
        "https://kilter-training-app.vercel.app",
        "https://*.vercel.app",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(circuits.router, prefix="/api/circuits", tags=["circuits"])


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
