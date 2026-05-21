from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.connection import engine, Base
from backend.routes import (
    events,
    treks,
    offroad,
    destinations,
    heatmap,
    map,
    wishlist,
    history,
    feedback,
    users
)

# Create all tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Wanderlust AI",
    description="AI powered travel companion for independent adventurers",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(events.router)
app.include_router(treks.router)
app.include_router(offroad.router)
app.include_router(destinations.router)
app.include_router(heatmap.router)
app.include_router(map.router)
app.include_router(wishlist.router)
app.include_router(history.router)
app.include_router(feedback.router)
app.include_router(users.router)


# Health check
@app.get("/")
def root():
    return {
        "message": "Wanderlust AI backend is running 🌍",
        "status": "healthy",
        "version": "1.0.0",
        "routes": [
            "/events",
            "/treks",
            "/offroad",
            "/destinations",
            "/heatmap",
            "/map/pins",
            "/wishlist",
            "/history",
            "/feedback",
            "/users"
        ]
    }