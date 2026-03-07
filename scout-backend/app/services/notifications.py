"""Notification service with Twilio integration."""
import os
import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.notification import NotificationLog
from app.models.alert import Alert
from app.models.product import Product
from app.models.saved_search import SavedSearch
from app.models.user import User

# Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

COOLDOWN_MINUTES = 30  # Don't re-notify about same product within this window


def get_twilio_client():
    """Get Twilio client if credentials are configured."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return None
    try:
        from twilio.rest import Client
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception:
        return None


def format_sms_message(alert: Alert, product: Optional[Product], search: Optional[SavedSearch]) -> str:
    """Format a premium, concise SMS notification."""
    search_name = search.name if search else "your search"

    if alert.alert_type == "new_match":
        if product:
            price_str = f"${product.price:.0f}" if product.price else "Price TBD"
            source_str = f" at {product.source}" if product.source else ""
            return (
                f"Scout: New match for \"{search_name}\": "
                f"{product.title}, {price_str}{source_str}. "
                f"{product.product_url or ''}"
            )
        return f"Scout: New match found for \"{search_name}\". Check your dashboard."

    elif alert.alert_type == "price_drop":
        details = alert.details or {}
        old_price = details.get("old_price", 0)
        new_price = details.get("new_price", 0)
        if product:
            return (
                f"Scout: Price drop on \"{search_name}\": "
                f"{product.title} fell from ${old_price:.0f} to ${new_price:.0f}. "
                f"{product.product_url or ''}"
            )
        return f"Scout: Price drop detected for \"{search_name}\". Check your dashboard."

    elif alert.alert_type == "sale":
        if product:
            discount = product.discount_percent or 0
            return (
                f"Scout: Sale alert for \"{search_name}\": "
                f"{product.title} is {discount:.0f}% off. "
                f"{product.product_url or ''}"
            )
        return f"Scout: Sale detected for \"{search_name}\". Check your dashboard."

    elif alert.alert_type == "restock":
        if product:
            return (
                f"Scout: Restock alert for \"{search_name}\": "
                f"{product.title} is back in stock. "
                f"{product.product_url or ''}"
            )
        return f"Scout: Item restocked for \"{search_name}\". Check your dashboard."

    return f"Scout: Update for \"{search_name}\". Check your dashboard."


def should_notify(db: Session, user_id: int, product_id: int, alert_type: str) -> bool:
    """Check if we should send a notification (dedup + cooldown)."""
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=COOLDOWN_MINUTES)
    existing = (
        db.query(NotificationLog)
        .join(Alert, NotificationLog.alert_id == Alert.id)
        .filter(
            NotificationLog.user_id == user_id,
            Alert.product_id == product_id,
            Alert.alert_type == alert_type,
            NotificationLog.sent_at > cutoff,
        )
        .first()
    )
    return existing is None


def send_notification(
    db: Session,
    alert: Alert,
    user: User,
    product: Optional[Product] = None,
    search: Optional[SavedSearch] = None,
) -> Optional[NotificationLog]:
    """Send SMS notification for an alert."""
    if not user.phone or not user.sms_enabled:
        return None

    # Check per-search notification settings
    if search:
        if alert.alert_type == "new_match" and not search.notify_new_matches:
            return None
        if alert.alert_type == "price_drop" and not search.notify_price_drops:
            return None
        if alert.alert_type == "sale" and not search.notify_sales:
            return None
        if alert.alert_type == "restock" and not search.notify_restocks:
            return None
        if not search.notify_sms:
            return None

    # Dedup check
    if product and not should_notify(db, user.id, product.id, alert.alert_type):
        return None

    message_body = format_sms_message(alert, product, search)

    # Try sending via Twilio
    twilio_sid = None
    send_status = "sent"
    client = get_twilio_client()

    if client and TWILIO_PHONE_NUMBER:
        try:
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=user.phone,
            )
            twilio_sid = message.sid
        except Exception as e:
            send_status = "failed"
            print(f"Twilio send error: {e}")
    else:
        # No Twilio configured — log as mock
        send_status = "mock"
        print(f"[MOCK SMS to {user.phone}]: {message_body}")

    # Log notification
    log = NotificationLog(
        user_id=user.id,
        alert_id=alert.id,
        channel="sms",
        phone=user.phone,
        message=message_body,
        status=send_status,
        twilio_sid=twilio_sid,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
