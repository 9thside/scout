"""Alert, search match, and user item action models."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    search_id = Column(Integer, nullable=True, index=True)
    product_id = Column(Integer, nullable=True, index=True)
    alert_type = Column(String, nullable=False)  # new_match, price_drop, sale, restock
    title = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)  # extra data like old_price, new_price, etc.
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SearchMatch(Base):
    __tablename__ = "search_matches"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    relevance_score = Column(Float, default=0.0)
    match_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class UserItemAction(Base):
    __tablename__ = "user_item_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    action = Column(String, nullable=False)  # liked, dismissed, purchased, ignored
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
