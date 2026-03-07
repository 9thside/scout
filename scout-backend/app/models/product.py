"""Product and price history models."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=True)  # e.g., Nordstrom, eBay, etc.
    brand = Column(String, nullable=True)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    original_price = Column(Float, nullable=True)
    discount_percent = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    image_url = Column(Text, nullable=True)
    product_url = Column(Text, nullable=True)
    availability = Column(String, default="in_stock")  # in_stock, out_of_stock, limited
    condition = Column(String, default="new")  # new, used, refurbished
    size = Column(String, nullable=True)
    color = Column(String, nullable=True)
    material = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    # Fingerprint for deduplication
    fingerprint = Column(String, unique=True, index=True, nullable=True)
    first_seen_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_on_sale = Column(Boolean, default=False)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)
