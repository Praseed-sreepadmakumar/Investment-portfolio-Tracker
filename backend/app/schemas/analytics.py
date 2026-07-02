"""Pydantic schemas that define analytics APIs for frontend chart rendering."""

from decimal import Decimal

from pydantic import BaseModel


class AllocationItemResponse(BaseModel):
    """Allocation percentage for a single holding symbol."""

    symbol: str
    company_name: str
    percentage: Decimal


class PerformanceResponse(BaseModel):
    """Aggregate portfolio performance metrics for chart summaries."""

    current_value: Decimal
    investment: Decimal
    profit: Decimal
    return_percentage: Decimal