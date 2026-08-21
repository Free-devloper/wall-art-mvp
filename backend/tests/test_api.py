import pytest
from app.config import settings
from app.services.circuit_breaker import CircuitBreaker
from app.services.moderation_service import ModerationService
from app.models.order import Order


def test_settings():
    assert settings.APP_ENV in ["development", "staging", "production", "test"]
    assert settings.DAILY_AI_SPEND_CAP_USD > 0


def test_moderation_service_blocked_terms():
    is_clean, terms = ModerationService.check_instructions("A picture of spider-man in space")
    assert not is_clean
    assert "spider-man" in terms


def test_moderation_service_clean_text():
    is_clean, terms = ModerationService.check_instructions("A fantasy watercolor oil painting with warm tones")
    assert is_clean
    assert len(terms) == 0


def test_moderation_sanitization():
    sanitized = ModerationService.sanitize_instructions("Please add mickey mouse on the wall")
    assert "mickey mouse" not in sanitized.lower()
    assert "***" in sanitized


def test_order_status_transitions():
    order = Order(status="new")
    assert order.is_valid_status_transition("awaiting_approval")
    assert order.is_valid_status_transition("cancelled")
    assert not order.is_valid_status_transition("shipped")

    order.status = "paid"
    assert order.is_valid_status_transition("in_production")
    assert order.is_valid_status_transition("refunded")
    assert not order.is_valid_status_transition("new")
