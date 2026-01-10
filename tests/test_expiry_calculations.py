"""Tests for subscription expiry calculations."""
import pytest
from datetime import date, timedelta
from app.models.subscription import Subscription, SubscriptionStatus, BillingCycle


def test_days_until_renewal_future():
    """Test days_until_renewal for future dates."""
    sub = Subscription(
        vendor_name="Test",
        cost=10.0,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        next_renewal_date=date.today() + timedelta(days=15),
        status=SubscriptionStatus.ACTIVE
    )
    assert sub.days_until_renewal() == 15


def test_days_until_renewal_past():
    """Test days_until_renewal for past dates."""
    sub = Subscription(
        vendor_name="Test",
        cost=10.0,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today() - timedelta(days=60),
        next_renewal_date=date.today() - timedelta(days=5),
        status=SubscriptionStatus.ACTIVE
    )
    assert sub.days_until_renewal() == -5


def test_days_until_renewal_today():
    """Test days_until_renewal for today."""
    sub = Subscription(
        vendor_name="Test",
        cost=10.0,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today() - timedelta(days=30),
        next_renewal_date=date.today(),
        status=SubscriptionStatus.ACTIVE
    )
    assert sub.days_until_renewal() == 0


def test_is_expiring_soon_true():
    """Test is_expiring_soon returns True for subscriptions expiring within threshold."""
    sub = Subscription(
        vendor_name="Test",
        cost=10.0,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        next_renewal_date=date.today() + timedelta(days=15),
        status=SubscriptionStatus.ACTIVE
    )
    assert sub.is_expiring_soon(threshold_days=30) is True
    assert sub.is_expiring_soon(threshold_days=7) is False


def test_is_expiring_soon_false():
    """Test is_expiring_soon returns False for subscriptions far in the future."""
    sub = Subscription(
        vendor_name="Test",
        cost=10.0,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        next_renewal_date=date.today() + timedelta(days=60),
        status=SubscriptionStatus.ACTIVE
    )
    assert sub.is_expiring_soon(threshold_days=30) is False


def test_is_overdue_true():
    """Test is_overdue returns True for past renewal dates."""
    sub = Subscription(
        vendor_name="Test",
        cost=10.0,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today() - timedelta(days=60),
        next_renewal_date=date.today() - timedelta(days=5),
        status=SubscriptionStatus.ACTIVE
    )
    assert sub.is_overdue() is True


def test_is_overdue_false():
    """Test is_overdue returns False for future renewal dates."""
    sub = Subscription(
        vendor_name="Test",
        cost=10.0,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        next_renewal_date=date.today() + timedelta(days=15),
        status=SubscriptionStatus.ACTIVE
    )
    assert sub.is_overdue() is False


def test_is_overdue_today():
    """Test is_overdue returns False for renewal today."""
    sub = Subscription(
        vendor_name="Test",
        cost=10.0,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today() - timedelta(days=30),
        next_renewal_date=date.today(),
        status=SubscriptionStatus.ACTIVE
    )
    assert sub.is_overdue() is False
