"""
Monitoring service: executes saved searches, processes results,
detects changes, creates alerts, and triggers notifications.
"""
import datetime
import time
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.saved_search import SavedSearch, SearchRunLog
from app.models.product import Product, PriceHistory
from app.models.alert import Alert, SearchMatch
from app.models.user import User
from app.services.source_adapters import get_source_adapters
from app.services.scoring import compute_relevance_score
from app.services.notifications import send_notification


def run_search_job(db: Session, search: SavedSearch, user: User) -> dict:
    """
    Execute a single saved search:
    1. Fetch products from all source adapters
    2. Normalize and deduplicate
    3. Score relevance
    4. Detect changes (new items, price drops, restocks)
    5. Create alerts
    6. Send notifications
    """
    start_time = time.time()
    adapters = get_source_adapters()
    all_raw_products: List[dict] = []
    run_status = "success"
    run_message = ""

    # Fetch from all sources
    for adapter in adapters:
        try:
            results = adapter.search(
                query=search.query,
                category=search.category,
                size=search.shoe_size or search.clothing_size,
            )
            all_raw_products.extend(results)
        except Exception as e:
            print(f"Source adapter {adapter.name} error: {e}")
            run_status = "error"
            run_message = f"Adapter {adapter.name} failed: {e}"

    stats = {"new_matches": 0, "price_drops": 0, "sales": 0, "restocks": 0, "total_processed": 0}

    for raw in all_raw_products:
        stats["total_processed"] += 1

        # Check for existing product by fingerprint
        existing = None
        if raw.get("fingerprint"):
            existing = db.query(Product).filter(Product.fingerprint == raw["fingerprint"]).first()

        if existing:
            # Check for price changes
            _handle_existing_product(db, existing, raw, search, user, stats)
        else:
            # New product
            _handle_new_product(db, raw, search, user, stats)

    # Update search metadata
    duration_ms = int((time.time() - start_time) * 1000)
    search.last_checked_at = datetime.datetime.utcnow()
    match_count = db.query(SearchMatch).filter(SearchMatch.search_id == search.id).count()
    search.match_count = match_count

    # Build run summary
    if run_status == "success":
        parts = []
        if stats["new_matches"]:
            parts.append(f"{stats['new_matches']} new")
        if stats["price_drops"]:
            parts.append(f"{stats['price_drops']} price drop{'s' if stats['price_drops'] > 1 else ''}")
        if stats["sales"]:
            parts.append(f"{stats['sales']} sale{'s' if stats['sales'] > 1 else ''}")
        if stats["restocks"]:
            parts.append(f"{stats['restocks']} restock{'s' if stats['restocks'] > 1 else ''}")
        run_message = ", ".join(parts) if parts else f"Scanned {stats['total_processed']} items, no new findings"

    search.last_run_status = run_status
    search.last_run_message = run_message

    # Log the run
    run_log = SearchRunLog(
        search_id=search.id,
        user_id=user.id,
        status=run_status,
        items_found=stats["total_processed"],
        new_matches=stats["new_matches"],
        price_drops=stats["price_drops"],
        sales=stats["sales"],
        restocks=stats["restocks"],
        message=run_message,
        duration_ms=duration_ms,
    )
    db.add(run_log)
    db.commit()

    return stats


def _handle_new_product(db: Session, raw: dict, search: SavedSearch, user: User, stats: dict):
    """Process a newly discovered product."""
    product = Product(
        title=raw["title"],
        source=raw.get("source"),
        brand=raw.get("brand"),
        category=raw.get("category"),
        price=raw.get("price"),
        original_price=raw.get("original_price"),
        discount_percent=raw.get("discount_percent"),
        currency=raw.get("currency", "USD"),
        image_url=raw.get("image_url"),
        product_url=raw.get("product_url"),
        availability=raw.get("availability", "in_stock"),
        condition=raw.get("condition", "new"),
        size=raw.get("size"),
        color=raw.get("color"),
        material=raw.get("material"),
        description=raw.get("description"),
        fingerprint=raw.get("fingerprint"),
        is_on_sale=raw.get("is_on_sale", False),
    )
    db.add(product)
    db.flush()

    # Record initial price
    if product.price is not None:
        price_record = PriceHistory(
            product_id=product.id,
            price=product.price,
            original_price=product.original_price,
        )
        db.add(price_record)

    # Score relevance
    score, reason = compute_relevance_score(product, search)

    # Only create match if score is reasonable
    if score >= 15:
        match = SearchMatch(
            search_id=search.id,
            product_id=product.id,
            relevance_score=score,
            match_reason=reason,
        )
        db.add(match)

        # Create alert
        alert = Alert(
            user_id=search.user_id,
            search_id=search.id,
            product_id=product.id,
            alert_type="new_match",
            title=f"New match: {product.title}",
            message=f"Found a new item matching \"{search.name}\": {product.title} at ${product.price:.0f}" if product.price else f"Found a new item matching \"{search.name}\"",
            details={"relevance_score": score, "match_reason": reason},
        )
        db.add(alert)
        db.flush()
        stats["new_matches"] += 1

        # Check for sale
        if product.is_on_sale and product.original_price:
            sale_alert = Alert(
                user_id=search.user_id,
                search_id=search.id,
                product_id=product.id,
                alert_type="sale",
                title=f"Sale: {product.title}",
                message=f"{product.title} is {product.discount_percent:.0f}% off at ${product.price:.0f}",
                details={"discount_percent": product.discount_percent, "original_price": product.original_price},
            )
            db.add(sale_alert)
            db.flush()
            stats["sales"] += 1

        # Send notification
        try:
            send_notification(db, alert, user, product, search)
        except Exception as e:
            print(f"Notification error: {e}")

    db.commit()


def _handle_existing_product(db: Session, existing: Product, raw: dict, search: SavedSearch, user: User, stats: dict):
    """Check for changes on an existing product."""
    new_price = raw.get("price")
    old_price = existing.price
    new_availability = raw.get("availability", "in_stock")
    old_availability = existing.availability

    # Update last seen and refresh image/product URLs
    existing.last_seen_at = datetime.datetime.utcnow()
    if raw.get("image_url"):
        existing.image_url = raw["image_url"]
    if raw.get("product_url"):
        existing.product_url = raw["product_url"]

    # Check for price drop
    if new_price is not None and old_price is not None and new_price < old_price:
        drop_percent = ((old_price - new_price) / old_price) * 100

        # Only alert on meaningful drops (>3%)
        if drop_percent >= 3:
            existing.price = new_price
            if raw.get("original_price"):
                existing.original_price = raw["original_price"]
            existing.discount_percent = raw.get("discount_percent")
            existing.is_on_sale = raw.get("is_on_sale", existing.is_on_sale)

            # Record price change
            price_record = PriceHistory(
                product_id=existing.id,
                price=new_price,
                original_price=raw.get("original_price"),
            )
            db.add(price_record)

            # Ensure search match exists
            existing_match = (
                db.query(SearchMatch)
                .filter(SearchMatch.search_id == search.id, SearchMatch.product_id == existing.id)
                .first()
            )
            if not existing_match:
                score, reason = compute_relevance_score(existing, search)
                match = SearchMatch(
                    search_id=search.id,
                    product_id=existing.id,
                    relevance_score=score,
                    match_reason=reason,
                )
                db.add(match)

            alert = Alert(
                user_id=search.user_id,
                search_id=search.id,
                product_id=existing.id,
                alert_type="price_drop",
                title=f"Price drop: {existing.title}",
                message=f"{existing.title} dropped from ${old_price:.0f} to ${new_price:.0f} ({drop_percent:.0f}% off)",
                details={"old_price": old_price, "new_price": new_price, "drop_percent": drop_percent},
            )
            db.add(alert)
            db.flush()
            stats["price_drops"] += 1

            try:
                send_notification(db, alert, user, existing, search)
            except Exception as e:
                print(f"Notification error: {e}")

    # Check for restock
    if old_availability == "out_of_stock" and new_availability == "in_stock":
        existing.availability = new_availability

        alert = Alert(
            user_id=search.user_id,
            search_id=search.id,
            product_id=existing.id,
            alert_type="restock",
            title=f"Back in stock: {existing.title}",
            message=f"{existing.title} is back in stock",
            details={},
        )
        db.add(alert)
        db.flush()
        stats["restocks"] += 1

        try:
            send_notification(db, alert, user, existing, search)
        except Exception as e:
            print(f"Notification error: {e}")

    db.commit()


def get_due_searches(db: Session) -> List[SavedSearch]:
    """Get all active searches that are due to run based on their frequency."""
    now = datetime.datetime.utcnow()
    searches = db.query(SavedSearch).filter(SavedSearch.status == "active").all()

    due = []
    for s in searches:
        if s.last_checked_at is None:
            due.append(s)
            continue

        freq_map = {
            "1h": datetime.timedelta(hours=1),
            "6h": datetime.timedelta(hours=6),
            "daily": datetime.timedelta(hours=24),
        }
        interval = freq_map.get(s.search_frequency, datetime.timedelta(hours=24))
        if now - s.last_checked_at >= interval:
            due.append(s)

    return due
