"""Alert schemas."""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from app.schemas.product import ProductResponse


class AlertResponse(BaseModel):
    id: int
    user_id: int
    search_id: Optional[int] = None
    product_id: Optional[int] = None
    alert_type: str
    title: str
    message: Optional[str] = None
    details: Optional[Any] = None
    is_read: bool
    is_dismissed: bool
    created_at: datetime
    product: Optional[ProductResponse] = None
    search_name: Optional[str] = None

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None


class UserItemActionCreate(BaseModel):
    product_id: int
    action: str  # liked, dismissed, purchased, ignored


class UserItemActionResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    action: str
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_active_searches: int
    total_alerts_this_week: int
    price_drops_count: int
    new_items_count: int
    saved_items_count: int
