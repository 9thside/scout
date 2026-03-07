"""Saved search and run log models."""
import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, JSON
from app.database import Base


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    query = Column(String, nullable=False)
    category = Column(String, nullable=True)
    style_profile = Column(String, nullable=True)  # everyday, trend-forward, niche, premium-brand, designer, open
    budget_preference = Column(String, nullable=True)  # any, value, mid-range, premium, luxury
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    condition = Column(String, default="new_only")  # new_only, new_resale, resale_only
    preferred_brands = Column(JSON, nullable=True)  # list of strings
    excluded_brands = Column(JSON, nullable=True)  # list of strings
    # Size/variant fields
    clothing_size = Column(String, nullable=True)
    shoe_size = Column(String, nullable=True)
    color = Column(String, nullable=True)
    material = Column(String, nullable=True)
    dimensions = Column(String, nullable=True)
    gender_fit = Column(String, nullable=True)
    # Notification settings
    notify_sms = Column(Boolean, default=True)
    notify_whatsapp = Column(Boolean, default=False)
    notify_new_matches = Column(Boolean, default=True)
    notify_price_drops = Column(Boolean, default=True)
    notify_sales = Column(Boolean, default=True)
    notify_restocks = Column(Boolean, default=True)
    digest_frequency = Column(String, default="instant")  # instant, daily, weekly
    # Search frequency
    search_frequency = Column(String, default="daily")  # 1h, 6h, daily
    # Status
    status = Column(String, default="active")  # active, paused, archived
    last_checked_at = Column(DateTime, nullable=True)
    last_run_status = Column(String, nullable=True)  # success, error
    last_run_message = Column(String, nullable=True)  # brief summary of last run
    match_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class SearchRunLog(Base):
    """Activity log for search runs — tracks every execution."""
    __tablename__ = "search_run_logs"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(String, nullable=False)  # success, error
    items_found = Column(Integer, default=0)
    new_matches = Column(Integer, default=0)
    price_drops = Column(Integer, default=0)
    sales = Column(Integer, default=0)
    restocks = Column(Integer, default=0)
    message = Column(String, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
