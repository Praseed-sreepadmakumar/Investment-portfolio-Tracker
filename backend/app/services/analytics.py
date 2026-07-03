"""Business logic for portfolio allocation and performance analytics."""

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.schemas.analytics import AllocationItemResponse, PerformanceResponse
from app.services.market import (
    InvalidStockSymbolError,
    MarketDataUnavailableError,
    get_company_name,
)
from app.services.portfolio import (
    list_user_portfolios,
    resolve_holding_price_with_fallback,
)

MONEY_QUANTIZE = Decimal("0.01")
PERCENT_QUANTIZE = Decimal("0.01")


def _to_decimal(value: object) -> Decimal:
    """Convert numeric values to Decimal without float precision drift."""
    return Decimal(str(value))


def _round_money(value: Decimal) -> Decimal:
    """Round currency values to two decimal places for API responses."""
    return value.quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)


def _round_percentage(value: Decimal) -> Decimal:
    """Round percentage values to two decimal places for API responses."""
    return value.quantize(PERCENT_QUANTIZE, rounding=ROUND_HALF_UP)


def _calculate_performance_values(db: Session, user_id: int) -> tuple[Decimal, Decimal]:
    """Return total investment and current value using live prices for each holding."""
    holdings = list_user_portfolios(db, user_id)

    total_investment = Decimal("0")
    current_portfolio_value = Decimal("0")
    has_cached_price_updates = False

    for holding in holdings:
        quantity = _to_decimal(holding.quantity)
        purchase_price = _to_decimal(holding.purchase_price)
        market_price, _, cache_updated = resolve_holding_price_with_fallback(holding)
        has_cached_price_updates = has_cached_price_updates or cache_updated

        total_investment += quantity * purchase_price
        current_portfolio_value += quantity * market_price

    if has_cached_price_updates:
        db.commit()

    return total_investment, current_portfolio_value


def get_performance_summary(db: Session, user_id: int) -> PerformanceResponse:
    """Return aggregate investment, value, profit, and return percentage."""
    total_investment, current_portfolio_value = _calculate_performance_values(db, user_id)

    total_profit = current_portfolio_value - total_investment
    if total_investment > 0:
        return_percentage = (total_profit / total_investment) * Decimal("100")
    else:
        return_percentage = Decimal("0")

    return PerformanceResponse(
        current_value=_round_money(current_portfolio_value),
        investment=_round_money(total_investment),
        profit=_round_money(total_profit),
        return_percentage=_round_percentage(return_percentage),
    )


def get_allocation_summary(db: Session, user_id: int) -> list[AllocationItemResponse]:
    """Return per-symbol allocation percentages based on live current value."""
    holdings = list_user_portfolios(db, user_id)

    symbol_totals: dict[str, Decimal] = {}
    symbol_names: dict[str, str] = {}
    total_portfolio_value = Decimal("0")
    has_cached_price_updates = False

    for holding in holdings:
        if holding.symbol not in symbol_names:
            try:
                symbol_names[holding.symbol] = get_company_name(holding.symbol)
            except (InvalidStockSymbolError, MarketDataUnavailableError):
                symbol_names[holding.symbol] = holding.symbol

        market_price, _, cache_updated = resolve_holding_price_with_fallback(holding)
        has_cached_price_updates = has_cached_price_updates or cache_updated
        holding_value = _to_decimal(holding.quantity) * market_price
        symbol_totals[holding.symbol] = symbol_totals.get(holding.symbol, Decimal("0")) + holding_value
        total_portfolio_value += holding_value

    if has_cached_price_updates:
        db.commit()

    if total_portfolio_value == 0:
        return []

    allocation_items = [
        AllocationItemResponse(
            symbol=symbol,
            company_name=symbol_names[symbol],
            percentage=_round_percentage((value / total_portfolio_value) * Decimal("100")),
        )
        for symbol, value in symbol_totals.items()
    ]

    return sorted(allocation_items, key=lambda item: item.percentage, reverse=True)