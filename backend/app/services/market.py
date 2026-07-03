"""Reusable market data helpers backed by yfinance."""

from __future__ import annotations

import subprocess
import time
from urllib.parse import quote
from typing import Any

try:
    # Use OS trust store (e.g., Windows cert store) for HTTPS verification.
    import truststore

    truststore.inject_into_ssl()
except Exception:
    # Fall back to default SSL behavior when truststore is unavailable.
    pass

import requests
import yfinance as yf


_YF_SESSION = requests.Session()
_YF_SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
)

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
QUOTE_CACHE_TTL_SECONDS = 45
COMPANY_CACHE_TTL_SECONDS = 300

_price_cache: dict[str, tuple[float, float]] = {}
_company_cache: dict[str, tuple[str, float]] = {}


def _get_chart_result_via_powershell(symbol: str) -> dict[str, Any] | None:
    """Fetch Yahoo chart payload via PowerShell on Windows as network fallback."""
    normalized_symbol = _normalize_symbol(symbol)
    encoded_symbol = quote(normalized_symbol, safe="")
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}"
        "?range=5d&interval=1d"
    )

    script = (
        "$ErrorActionPreference='Stop'; "
        f"$r = Invoke-WebRequest -Uri '{url}' -UseBasicParsing; "
        "$r.Content"
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=12,
            check=False,
        )
    except Exception:
        return None

    if result.returncode != 0:
        return None

    raw_text = (result.stdout or "").strip()
    if not raw_text:
        return None

    try:
        payload = requests.models.complexjson.loads(raw_text)
    except ValueError:
        return None

    chart = payload.get("chart") or {}
    error = chart.get("error")
    if error:
        code = str(error.get("code") or "").lower()
        if "not found" in code:
            raise InvalidStockSymbolError(f"Invalid stock symbol '{normalized_symbol}'")
        raise MarketDataUnavailableError(
            f"Unable to fetch market data for symbol '{normalized_symbol}'"
        )

    result_rows = chart.get("result") or []
    if not result_rows:
        return None

    return result_rows[0]


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
    return yf.Ticker(_normalize_symbol(symbol), session=_YF_SESSION)


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


def _get_chart_result(symbol: str) -> dict[str, Any]:
    """Fetch Yahoo chart payload using a requests-backed session."""
    normalized_symbol = _normalize_symbol(symbol)
    url = YAHOO_CHART_URL.format(symbol=normalized_symbol)

    try:
        response = _YF_SESSION.get(
            url,
            params={"range": "5d", "interval": "1d"},
            timeout=12,
        )
    except Exception:
        powershell_result = _get_chart_result_via_powershell(normalized_symbol)
        if powershell_result is not None:
            return powershell_result
        raise MarketDataUnavailableError(
            f"Unable to fetch market data for symbol '{normalized_symbol}'"
        )

    if response.status_code == 429:
        raise MarketDataUnavailableError(
            f"Market data provider rate-limited requests for symbol '{normalized_symbol}'"
        )

    if response.status_code == 404:
        raise InvalidStockSymbolError(f"Invalid stock symbol '{normalized_symbol}'")

    if response.status_code >= 500:
        raise MarketDataUnavailableError(
            f"Market data provider is temporarily unavailable for symbol '{normalized_symbol}'"
        )

    content_type = (response.headers.get("Content-Type") or "").lower()
    raw_text = response.text[:400]
    if "text/html" in content_type or raw_text.lstrip().startswith("<!doctype html"):
        powershell_result = _get_chart_result_via_powershell(normalized_symbol)
        if powershell_result is not None:
            return powershell_result
        if "zscaler" in raw_text.lower():
            raise MarketDataUnavailableError(
                "Network security gateway intercepted market data requests (Zscaler). "
                "Allowlist Yahoo Finance domains or configure Python runtime proxy/cert trust."
            )
        raise MarketDataUnavailableError(
            f"Unexpected HTML response from market data provider for symbol '{normalized_symbol}'"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise MarketDataUnavailableError(
            f"Unable to parse market data response for symbol '{normalized_symbol}'"
        ) from exc

    chart = payload.get("chart") or {}
    error = chart.get("error")
    if error:
        code = str(error.get("code") or "").lower()
        if "not found" in code:
            raise InvalidStockSymbolError(f"Invalid stock symbol '{normalized_symbol}'")
        raise MarketDataUnavailableError(
            f"Unable to fetch market data for symbol '{normalized_symbol}'"
        )

    result = chart.get("result") or []
    if not result:
        raise MarketDataUnavailableError(
            f"Unable to fetch market data for symbol '{normalized_symbol}'"
        )

    return result[0]


def _get_chart_price(symbol: str) -> float:
    """Return price from Yahoo chart payload using regularMarketPrice or latest close."""
    normalized_symbol = _normalize_symbol(symbol)
    now = time.monotonic()
    cached_price = _price_cache.get(normalized_symbol)
    if cached_price and now < cached_price[1]:
        return cached_price[0]

    result = _get_chart_result(normalized_symbol)
    meta = result.get("meta") or {}

    regular_market_price = meta.get("regularMarketPrice")
    if regular_market_price is not None:
        value = float(regular_market_price)
        _price_cache[normalized_symbol] = (value, now + QUOTE_CACHE_TTL_SECONDS)
        return value

    indicators = result.get("indicators") or {}
    quote_rows = indicators.get("quote") or []
    if quote_rows:
        closes = quote_rows[0].get("close") or []
        valid_closes = [value for value in closes if value is not None]
        if valid_closes:
            value = float(valid_closes[-1])
            _price_cache[normalized_symbol] = (value, now + QUOTE_CACHE_TTL_SECONDS)
            return value

    raise MarketDataUnavailableError(
        f"Market price is temporarily unavailable for symbol '{_normalize_symbol(symbol)}'"
    )


def _get_chart_company_name(symbol: str) -> str:
    """Return company name from Yahoo chart payload metadata."""
    normalized_symbol = _normalize_symbol(symbol)
    now = time.monotonic()
    cached_company = _company_cache.get(normalized_symbol)
    if cached_company and now < cached_company[1]:
        return cached_company[0]

    result = _get_chart_result(normalized_symbol)
    meta = result.get("meta") or {}
    company_name = meta.get("longName") or meta.get("shortName")
    if not company_name:
        raise MarketDataUnavailableError(
            f"Company name is unavailable for symbol '{normalized_symbol}'"
        )

    value = str(company_name)
    _company_cache[normalized_symbol] = (value, now + COMPANY_CACHE_TTL_SECONDS)
    return value


def _get_last_close_price(ticker: yf.Ticker) -> float | None:
    """Read the most recent close from short history when quote endpoints fail."""
    try:
        history = ticker.history(period="5d", interval="1d", auto_adjust=False)
    except Exception:
        return None

    if history.empty:
        return None

    close_series = history.get("Close")
    if close_series is None:
        return None

    close_series = close_series.dropna()
    if close_series.empty:
        return None

    return float(close_series.iloc[-1])


def _read_field(source: Any, field_name: str) -> Any:
    """Safely read a field from either a dict-like object or an attribute object."""
    if isinstance(source, dict):
        return source.get(field_name)

    if source is None:
        return None

    return getattr(source, field_name, None)


def validate_stock(symbol: str) -> bool:
    """Validate that the symbol resolves to a company with market data."""
    _ = get_current_price(symbol)
    return True


def get_current_price(symbol: str) -> float:
    """Return the latest market price for a validated stock symbol."""
    return _get_chart_price(symbol)


def get_company_name(symbol: str) -> str:
    """Return the listed company name for a validated stock symbol."""
    return _get_chart_company_name(symbol)


def probe_market_data_provider(symbol: str = "AAPL") -> tuple[bool, str]:
    """Check provider availability and return a diagnostic message for startup logs."""
    normalized_symbol = _normalize_symbol(symbol)

    try:
        price = _get_chart_price(normalized_symbol)
        return True, (
            f"Market data provider reachable for {normalized_symbol}; sample price={price:.2f}"
        )
    except MarketDataError as exc:
        return False, (
            "Market data provider probe failed. "
            "Live quotes may be unavailable and fallbacks will be used. "
            f"Details: {exc.__class__.__name__}: {exc}"
        )
    except Exception as exc:
        return False, (
            "Market data provider probe failed with an unexpected error. "
            "Live quotes may be unavailable and fallbacks will be used. "
            f"Details: {exc.__class__.__name__}: {exc}"
        )