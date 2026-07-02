"""Analytics routes for authenticated allocation and performance data."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.analytics import AllocationItemResponse, PerformanceResponse
from app.services.analytics import get_allocation_summary, get_performance_summary
from app.services.market import InvalidStockSymbolError, MarketDataUnavailableError

router = APIRouter(tags=["analytics"])


@router.get("/allocation", response_model=list[AllocationItemResponse])
def get_allocation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return current portfolio allocation percentages for frontend charts."""
    try:
        return get_allocation_summary(db, current_user.id)
    except InvalidStockSymbolError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except MarketDataUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/performance", response_model=PerformanceResponse)
def get_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregate performance metrics for frontend summary charts."""
    try:
        return get_performance_summary(db, current_user.id)
    except InvalidStockSymbolError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except MarketDataUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc