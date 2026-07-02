"""Pydantic schemas that define the dashboard summary API contract."""

from decimal import Decimal

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    """Aggregated portfolio metrics returned for the authenticated user."""

    total_investment: Decimal
    current_portfolio_value: Decimal
    total_profit_loss: Decimal
    return_percentage: Decimal
    number_of_holdings: int