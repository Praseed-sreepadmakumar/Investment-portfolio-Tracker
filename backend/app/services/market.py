"""Reusable market data helpers backed by yfinance."""

from __future__ import annotations

from typing import Any

import yfinance as yf


class MarketDataError(Exception):
    """Base exception for market data failures."""


class InvalidStockSymbolError(MarketDataError):
    """Raised when a symbol cannot be resolved to a valid listed company."""


class MarketDataUnavailableError(MarketDataError):
    """Raised when market data could not be fetched from the provider."""


def _normalize_symbol(symbol: str) -> str:
    """Trim and normalize incoming symbols before provider lookups."""
    normalized = symbol.strip().upper()
    if not normalized:
        raise InvalidStockSymbolError("Stock symbol must not be empty")
    return normalized


def _get_ticker(symbol: str) -> yf.Ticker:
    """Build a reusable yfinance ticker instance for the requested symbol."""
    return yf.Ticker(_normalize_symbol(symbol))


def _get_ticker_info(ticker: yf.Ticker, symbol: str) -> dict[str, Any]:
    """Read provider metadata and translate transport failures into service errors."""
    try:
        info = ticker.info or {}
    except Exception as exc:
        raise MarketDataUnavailableError(
            f"Unable to fetch market data for symbol '{_normalize_symbol(symbol)}'"
        ) from exc

    if not info:
        raise InvalidStockSymbolError(
            f"Invalid stock symbol '{_normalize_symbol(symbol)}'"
        )

    return info


def validate_stock(symbol: str) -> bool:
    """Validate that the symbol resolves to a company with market data."""
    ticker = _get_ticker(symbol)
    info = _get_ticker_info(ticker, symbol)

    company_name = info.get("longName") or info.get("shortName")
    if not company_name:
        raise InvalidStockSymbolError(
            f"Invalid stock symbol '{_normalize_symbol(symbol)}'"
        )

    get_current_price(symbol)
    return True


def get_current_price(symbol: str) -> float:
    """Return the latest market price for a validated stock symbol."""
    ticker = _get_ticker(symbol)
    info = _get_ticker_info(ticker, symbol)

    for field_name in ("currentPrice", "regularMarketPrice", "previousClose"):
        price = info.get(field_name)
        if price is not None:
            return float(price)

    raise InvalidStockSymbolError(
        f"Market price is unavailable for symbol '{_normalize_symbol(symbol)}'"
    )


def get_company_name(symbol: str) -> str:
    """Return the listed company name for a validated stock symbol."""
    ticker = _get_ticker(symbol)
    info = _get_ticker_info(ticker, symbol)

    company_name = info.get("longName") or info.get("shortName")
    if not company_name:
        raise InvalidStockSymbolError(
            f"Company name is unavailable for symbol '{_normalize_symbol(symbol)}'"
        )

    return str(company_name)