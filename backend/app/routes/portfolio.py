"""Portfolio routes for managing authenticated user holdings."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioOverviewResponse,
    PortfolioResponse,
    PortfolioUpdate,
)
from app.services.market import InvalidStockSymbolError, MarketDataUnavailableError
from app.services.portfolio import (
    create_portfolio_holding,
    delete_portfolio_holding,
    get_user_portfolio,
    list_user_portfolio_overview,
    list_user_portfolios,
    update_portfolio_holding,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a holding for the authenticated user."""
    try:
        return create_portfolio_holding(db, current_user.id, portfolio)
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


@router.get("", response_model=list[PortfolioResponse])
def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List only the holdings owned by the authenticated user."""
    return list_user_portfolios(db, current_user.id)


@router.get("/overview", response_model=list[PortfolioOverviewResponse])
def get_portfolio_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List holdings with current market price and profit/loss columns."""
    try:
        return list_user_portfolio_overview(db, current_user.id)
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


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    portfolio_in: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user-owned holding or return 404 when it is not accessible."""
    portfolio = get_user_portfolio(db, current_user.id, portfolio_id)
    if portfolio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio holding not found",
        )

    try:
        return update_portfolio_holding(db, portfolio, portfolio_in)
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


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a user-owned holding or return 404 when it is not accessible."""
    portfolio = get_user_portfolio(db, current_user.id, portfolio_id)
    if portfolio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio holding not found",
        )

    delete_portfolio_holding(db, portfolio)
    return Response(status_code=status.HTTP_204_NO_CONTENT)