"""Business logic for calculating authenticated portfolio dashboard metrics."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.schemas.dashboard import DashboardResponse
from app.services.analytics import get_performance_summary
from app.services.portfolio import list_user_portfolios


def get_dashboard_summary(db: Session, user_id: int) -> DashboardResponse:
    """Calculate portfolio totals for the authenticated user using live prices."""
    holdings = list_user_portfolios(db, user_id)
    performance = get_performance_summary(db, user_id)

    return DashboardResponse(
        total_investment=performance.investment,
        current_portfolio_value=performance.current_value,
        total_profit_loss=performance.profit,
        return_percentage=performance.return_percentage,
        number_of_holdings=len(holdings),
    )