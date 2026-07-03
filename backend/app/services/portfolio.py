"""Business logic for creating, reading, updating, and deleting holdings."""

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioOverviewResponse,
    PortfolioUpdate,
)
from app.services.market import (
    InvalidStockSymbolError,
    MarketDataUnavailableError,
    get_current_price,
    validate_stock,
)

MONEY_QUANTIZE = Decimal("0.01")


def _to_decimal(value: object) -> Decimal:
    """Convert numeric values to Decimal without float precision drift."""
    return Decimal(str(value))


def _round_money(value: Decimal) -> Decimal:
    """Round money values to two decimals for consistent API responses."""
    return value.quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)


def resolve_holding_price_with_fallback(
    holding: Portfolio,
) -> tuple[Decimal, str, bool]:
    """Resolve price using live quote, then cached quote, then purchase price."""
    try:
        live_price = _round_money(_to_decimal(get_current_price(holding.symbol)))
        if holding.last_live_price != live_price:
            holding.last_live_price = live_price
            return live_price, "live", True
        return live_price, "live", False
    except (MarketDataUnavailableError, InvalidStockSymbolError):
        if holding.last_live_price is not None:
            return _to_decimal(holding.last_live_price), "cached", False
        return _to_decimal(holding.purchase_price), "purchase", False


def create_portfolio_holding(
    db: Session,
    user_id: int,
    portfolio_in: PortfolioCreate,
) -> Portfolio:
    """Create and persist a new holding for the authenticated user."""
    # Only persist holdings for symbols that resolve to live market data.
    validate_stock(portfolio_in.symbol)
    initial_live_price = _round_money(_to_decimal(get_current_price(portfolio_in.symbol)))

    portfolio = Portfolio(
        user_id=user_id,
        symbol=portfolio_in.symbol,
        quantity=portfolio_in.quantity,
        purchase_price=portfolio_in.purchase_price,
        last_live_price=initial_live_price,
        purchase_date=portfolio_in.purchase_date,
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


def list_user_portfolios(db: Session, user_id: int) -> list[Portfolio]:
    """Return all holdings owned by the authenticated user."""
    return (
        db.query(Portfolio)
        .filter(Portfolio.user_id == user_id)
        .order_by(Portfolio.purchase_date.desc(), Portfolio.id.desc())
        .all()
    )


def list_user_portfolio_overview(
    db: Session,
    user_id: int,
) -> list[PortfolioOverviewResponse]:
    """Return user holdings enriched with live price and profit/loss columns."""
    holdings = list_user_portfolios(db, user_id)
    overview_rows: list[PortfolioOverviewResponse] = []
    has_cached_price_updates = False

    for holding in holdings:
        quantity = _to_decimal(holding.quantity)
        purchase_price = _to_decimal(holding.purchase_price)
        current_price, price_source, cache_updated = resolve_holding_price_with_fallback(
            holding
        )
        has_cached_price_updates = has_cached_price_updates or cache_updated

        profit_loss = (current_price - purchase_price) * quantity

        overview_rows.append(
            PortfolioOverviewResponse(
                id=holding.id,
                symbol=holding.symbol,
                quantity=quantity,
                purchase_price=_round_money(purchase_price),
                current_price=_round_money(current_price),
                profit_loss=_round_money(profit_loss),
                is_live_price=price_source == "live",
                price_source=price_source,
            )
        )

    if has_cached_price_updates:
        db.commit()

    return overview_rows


def get_user_portfolio(db: Session, user_id: int, portfolio_id: int) -> Portfolio | None:
    """Return a single holding only when it belongs to the authenticated user."""
    return (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
        .first()
    )


def update_portfolio_holding(
    db: Session,
    portfolio: Portfolio,
    portfolio_in: PortfolioUpdate,
) -> Portfolio:
    """Apply user-owned holding updates and persist the changes."""
    # Re-validate the symbol in case the user changes the holding ticker.
    validate_stock(portfolio_in.symbol)
    refreshed_live_price = _round_money(_to_decimal(get_current_price(portfolio_in.symbol)))

    portfolio.symbol = portfolio_in.symbol
    portfolio.quantity = portfolio_in.quantity
    portfolio.purchase_price = portfolio_in.purchase_price
    portfolio.last_live_price = refreshed_live_price
    portfolio.purchase_date = portfolio_in.purchase_date
    db.commit()
    db.refresh(portfolio)
    return portfolio


def delete_portfolio_holding(db: Session, portfolio: Portfolio) -> None:
    """Delete a holding that belongs to the authenticated user."""
    db.delete(portfolio)
    db.commit()