"""Pydantic schemas that define the portfolio management API contract."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PortfolioBase(BaseModel):
    """Shared validation rules for portfolio write operations."""

    symbol: str = Field(min_length=1, max_length=20)
    quantity: Decimal = Field(gt=0)
    purchase_price: Decimal = Field(gt=0)
    purchase_date: date

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        """Trim and normalize stock symbols before persistence."""
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Stock symbol must not be empty")
        return normalized


class PortfolioCreate(PortfolioBase):
    """Payload accepted when a user creates a holding."""


class PortfolioUpdate(PortfolioBase):
    """Payload accepted when a user updates an existing holding."""


class PortfolioResponse(BaseModel):
    """Portfolio holding returned to the authenticated owner."""

    id: int
    user_id: int
    symbol: str
    quantity: Decimal
    purchase_price: Decimal
    purchase_date: date

    model_config = ConfigDict(from_attributes=True)


class PortfolioOverviewResponse(BaseModel):
    """Portfolio table row enriched with live market and profit metrics."""

    id: int
    symbol: str
    quantity: Decimal
    purchase_price: Decimal
    current_price: Decimal
    profit_loss: Decimal
    is_live_price: bool
    price_source: Literal["live", "cached", "purchase"]