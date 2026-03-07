"""Saved search schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SavedSearchCreate(BaseModel):
    name: str
    query: str
    category: Optional[str] = None
    style_profile: Optional[str] = None
    budget_preference: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Optional[str] = "new_only"
    preferred_brands: Optional[List[str]] = None
    excluded_brands: Optional[List[str]] = None
    clothing_size: Optional[str] = None
    shoe_size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[str] = None
    gender_fit: Optional[str] = None
    notify_sms: Optional[bool] = True
    notify_whatsapp: Optional[bool] = False
    notify_new_matches: Optional[bool] = True
    notify_price_drops: Optional[bool] = True
    notify_sales: Optional[bool] = True
    notify_restocks: Optional[bool] = True
    digest_frequency: Optional[str] = "instant"
    search_frequency: Optional[str] = "daily"


class SavedSearchUpdate(BaseModel):
    name: Optional[str] = None
    query: Optional[str] = None
    category: Optional[str] = None
    style_profile: Optional[str] = None
    budget_preference: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Optional[str] = None
    preferred_brands: Optional[List[str]] = None
    excluded_brands: Optional[List[str]] = None
    clothing_size: Optional[str] = None
    shoe_size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[str] = None
    gender_fit: Optional[str] = None
    notify_sms: Optional[bool] = None
    notify_whatsapp: Optional[bool] = None
    notify_new_matches: Optional[bool] = None
    notify_price_drops: Optional[bool] = None
    notify_sales: Optional[bool] = None
    notify_restocks: Optional[bool] = None
    digest_frequency: Optional[str] = None
    search_frequency: Optional[str] = None
    status: Optional[str] = None


class SavedSearchResponse(BaseModel):
    id: int
    user_id: int
    name: str
    query: str
    category: Optional[str] = None
    style_profile: Optional[str] = None
    budget_preference: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Optional[str] = None
    preferred_brands: Optional[List[str]] = None
    excluded_brands: Optional[List[str]] = None
    clothing_size: Optional[str] = None
    shoe_size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[str] = None
    gender_fit: Optional[str] = None
    notify_sms: bool
    notify_whatsapp: bool
    notify_new_matches: bool
    notify_price_drops: bool
    notify_sales: bool
    notify_restocks: bool
    digest_frequency: str
    search_frequency: str
    status: str
    last_checked_at: Optional[datetime] = None
    last_run_status: Optional[str] = None
    last_run_message: Optional[str] = None
    match_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SearchRunLogResponse(BaseModel):
    id: int
    search_id: int
    user_id: int
    status: str
    items_found: int
    new_matches: int
    price_drops: int
    sales: int
    restocks: int
    message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    search_name: Optional[str] = None

    class Config:
        from_attributes = True
