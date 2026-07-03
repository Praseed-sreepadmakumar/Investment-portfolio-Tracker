"""Application entrypoint for the Investment Portfolio Tracker API."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import initialize_database
from app.routes.analytics import router as analytics_router
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.portfolio import router as portfolio_router
from app.services.market import probe_market_data_provider

logger = logging.getLogger(__name__)

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


@app.on_event("startup")
def log_market_data_probe() -> None:
    """Log a provider readiness probe to surface TLS/network issues early."""
    is_ready, message = probe_market_data_provider("AAPL")
    if is_ready:
        logger.info(message)
        return

    logger.warning(
        "%s Configure CURL_CA_BUNDLE/SSL_CERT_FILE with a trusted PEM bundle "
        "if your network uses custom root certificates.",
        message,
    )


@app.get("/")
def root():
    """Expose a simple health-style message for the API root."""
    return {
        "message": "Investment Portfolio Tracker API!"
    }