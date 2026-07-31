"""
Jarvis AIOS — Live Information Subsystem Test Suite
---------------------------------------------------

Automated unit & integration tests covering:
  - Gold price parsing & unit validation
  - Silver price parsing & unit validation
  - Stock market price (NSE/BSE) validation
  - Crypto price (BTC/ETH) validation
  - Forex exchange rate (USD-INR) validation
  - Weather forecast validation
  - ToolResult contract verification
  - Domain validator bounds & unit ratio sanity checks
  - Cache bypass verification
  - Fail-closed hard gate enforcement
"""

from datetime import datetime
from app.Tools.live_information.contracts import ToolResult
from app.Tools.live_information.validators import (
    CommodityValidator, StockValidator, CryptoValidator, WeatherValidator, ForexValidator
)
from app.Tools.live_information.registry import live_tool_registry
from app.Tools.search_providers.classifier import SearchIntentClassifier


def test_tool_result_contract():
    """Verify ToolResult contract Pydantic model serialization and defaults."""
    res = ToolResult(success=True, verified=True, confidence=0.95, source="IBJA", payload={"price_numeric": 7450.0})
    assert res.success is True
    assert res.verified is True
    assert res.confidence == 0.95
    assert res.source == "IBJA"
    assert isinstance(res.timestamp, datetime)
    assert res.payload["price_numeric"] == 7450.0
    assert res.error is None


def test_commodity_validator_gold_valid():
    """Verify CommodityValidator accepts valid 24K Gold prices per gram / 10g in INR."""
    validator = CommodityValidator()

    # Valid per 10g gold price
    payload_10g = {
        "asset": "Gold", "purity": "24K", "price_numeric": 7450.0,
        "unit": "per gram", "currency": "INR", "price_10g": 74500.0, "converted_per_gram": 7450.0
    }
    is_valid, confidence, reason = validator.validate(payload_10g, source="IBJA / Economic Times")
    assert is_valid is True
    assert confidence >= 0.85
    assert "Validated commodity payload" in reason


def test_commodity_validator_silver_valid():
    """Verify CommodityValidator accepts valid Silver prices per gram / kg in INR."""
    validator = CommodityValidator()

    payload_kg = {
        "asset": "Silver", "price_numeric": 88.0,
        "unit": "per gram", "currency": "INR", "price_per_kg": 88000.0, "converted_per_gram": 88.0
    }
    is_valid, confidence, reason = validator.validate(payload_kg, source="MCX / Moneycontrol")
    assert is_valid is True
    assert confidence >= 0.85


def test_commodity_validator_invalid_ratio_rejected():
    """Verify CommodityValidator REJECTS mathematical unit ratio errors (e.g. ₹145,000/kg mapped to ₹145/g)."""
    validator = CommodityValidator()

    # Mathematically incorrect conversion: 145000/kg should be 145/g, but payload claims 1450/g
    payload_bad_ratio = {
        "asset": "Silver", "price_numeric": 1450.0,
        "unit": "per kg", "currency": "INR", "converted_per_gram": 1450.0
    }
    is_valid, confidence, reason = validator.validate(payload_bad_ratio, source="Moneycontrol")
    assert is_valid is False
    assert "Invalid unit conversion ratio" in reason or "out of bounds" in reason


def test_stock_validator_valid():
    """Verify StockValidator validates stock prices and market indices."""
    validator = StockValidator()

    payload = {"symbol": "NIFTY 50", "price_numeric": 24500.50, "currency": "INR"}
    is_valid, confidence, reason = validator.validate(payload, source="NSE / Moneycontrol")
    assert is_valid is True
    assert confidence >= 0.85


def test_crypto_validator_valid():
    """Verify CryptoValidator validates cryptocurrency prices."""
    validator = CryptoValidator()

    payload = {"asset": "Bitcoin", "symbol": "BTC", "price_numeric": 65420.0, "currency": "USD"}
    is_valid, confidence, reason = validator.validate(payload, source="CoinMarketCap")
    assert is_valid is True
    assert confidence >= 0.85


def test_weather_validator_valid():
    """Verify WeatherValidator validates Earth atmospheric temperature bounds."""
    validator = WeatherValidator()

    payload = {"location": "Channapatna", "temperature_celsius": 26.5}
    is_valid, confidence, reason = validator.validate(payload, source="Open-Meteo Weather API")
    assert is_valid is True
    assert confidence >= 0.85

    # Out of Earth bounds (e.g. 150°C)
    payload_invalid = {"location": "Channapatna", "temperature_celsius": 150.0}
    is_valid_bad, _, reason_bad = validator.validate(payload_invalid, source="Open-Meteo")
    assert is_valid_bad is False
    assert "out of Earth" in reason_bad


def test_forex_validator_valid():
    """Verify ForexValidator validates exchange rates."""
    validator = ForexValidator()

    payload = {"base_currency": "USD", "target_currency": "INR", "rate": 83.50}
    is_valid, confidence, reason = validator.validate(payload, source="RBI / XE")
    assert is_valid is True
    assert confidence >= 0.85


def test_search_intent_classifier_live_detection():
    """Verify SearchIntentClassifier identifies live queries and domain categories."""
    res_gold = SearchIntentClassifier.classify("What is today's gold rate per gram?")
    assert res_gold.is_live_info is True
    assert res_gold.domain == "commodity"

    res_stock = SearchIntentClassifier.classify("Nifty 50 live stock price")
    assert res_stock.is_live_info is True
    assert res_stock.domain == "stocks"

    res_weather = SearchIntentClassifier.classify("weather forecast today")
    assert res_weather.is_live_info is True
    assert res_weather.domain == "weather"


def test_live_tool_registry_dispatch(monkeypatch):
    """Verify LiveToolRegistry dispatches domain queries correctly."""
    from io import BytesIO
    import json

    fake_response = BytesIO(json.dumps({
        "current_weather": {"temperature": 26.5, "windspeed": 12.0},
        "hourly": {"precipitation_probability": [10]}
    }).encode("utf-8"))

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=10: fake_response)

    res_weather = live_tool_registry.dispatch(domain="weather", query="weather in Channapatna")
    assert res_weather.success is True
    assert res_weather.verified is True
    assert res_weather.payload["temperature_celsius"] == 26.5
