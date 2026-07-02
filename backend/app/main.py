"""Application entrypoint for the Investment Portfolio Tracker API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import initialize_database
from app.routes.analytics import router as analytics_router
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.portfolio import router as portfolio_router

# Ensure required tables and compatibility columns exist before serving requests.
initialize_database()

app = FastAPI(
    title="Investment Portfolio Tracker",
)

# Allow the local Vite frontend to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(portfolio_router)


@app.get("/")
def root():
    """Expose a simple health-style message for the API root."""
    return {
        "message": "Investment Portfolio Tracker API!"
    }