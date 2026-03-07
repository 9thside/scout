"""Product schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProductResponse(BaseModel):
    id: int
    title: str
    source: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    currency: str = "USD"
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    availability: str = "in_stock"
    condition: str = "new"
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    description: Optional[str] = None
    is_on_sale: bool = False
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: float
    original_price: Optional[float] = None
    recorded_at: datetime

    class Config:
        from_attributes = True


class ProductWithMatchInfo(ProductResponse):
    relevance_score: Optional[float] = None
    match_reason: Optional[str] = None
    user_action: Optional[str] = None
