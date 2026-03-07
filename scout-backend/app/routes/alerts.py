"""Alert and dashboard routes."""
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.saved_search import SavedSearch, SearchRunLog
from app.models.product import Product
from app.models.alert import Alert, UserItemAction
from app.schemas.alert import AlertResponse, AlertUpdate, DashboardStats, UserItemActionCreate, UserItemActionResponse
from app.schemas.saved_search import SearchRunLogResponse
from app.schemas.product import ProductResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api", tags=["alerts"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    total_active = db.query(SavedSearch).filter(
        SavedSearch.user_id == user.id,
        SavedSearch.status == "active",
    ).count()

    total_alerts_week = db.query(Alert).filter(
        Alert.user_id == user.id,
        Alert.created_at >= week_ago,
    ).count()

    price_drops = db.query(Alert).filter(
        Alert.user_id == user.id,
        Alert.alert_type == "price_drop",
        Alert.created_at >= week_ago,
    ).count()

    new_items = db.query(Alert).filter(
        Alert.user_id == user.id,
        Alert.alert_type == "new_match",
        Alert.created_at >= week_ago,
    ).count()

    saved_items = db.query(UserItemAction).filter(
        UserItemAction.user_id == user.id,
        UserItemAction.action == "liked",
    ).count()

    return DashboardStats(
        total_active_searches=total_active,
        total_alerts_this_week=total_alerts_week,
        price_drops_count=price_drops,
        new_items_count=new_items,
        saved_items_count=saved_items,
    )


@router.get("/alerts", response_model=List[AlertResponse])
def list_alerts(
    alert_type: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Alert).filter(
        Alert.user_id == user.id,
        Alert.is_dismissed == False,
    )
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)

    alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for alert in alerts:
        data = AlertResponse.model_validate(alert)
        if alert.product_id:
            product = db.query(Product).filter(Product.id == alert.product_id).first()
            if product:
                data.product = ProductResponse.model_validate(product)
        if alert.search_id:
            search = db.query(SavedSearch).filter(SavedSearch.id == alert.search_id).first()
            if search:
                data.search_name = search.name
        results.append(data)

    return results


@router.put("/alerts/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    data: AlertUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if data.is_read is not None:
        alert.is_read = data.is_read
    if data.is_dismissed is not None:
        alert.is_dismissed = data.is_dismissed

    db.commit()
    db.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.post("/alerts/mark-all-read")
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Alert).filter(
        Alert.user_id == user.id,
        Alert.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"ok": True}


# Products / Inbox
@router.get("/products", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    condition: Optional[str] = Query(None),
    on_sale: Optional[bool] = Query(None),
    search_query: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all products found across all searches for the user."""
    from app.models.alert import SearchMatch
    # Get product IDs from user's searches
    user_search_ids = [s.id for s in db.query(SavedSearch).filter(SavedSearch.user_id == user.id).all()]

    if not user_search_ids:
        return []

    product_ids_query = (
        db.query(SearchMatch.product_id)
        .filter(SearchMatch.search_id.in_(user_search_ids))
        .distinct()
    )

    query = db.query(Product).filter(Product.id.in_(product_ids_query))

    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if condition:
        query = query.filter(Product.condition == condition)
    if on_sale is not None:
        query = query.filter(Product.is_on_sale == on_sale)
    if search_query:
        query = query.filter(Product.title.ilike(f"%{search_query}%"))

    products = query.order_by(Product.last_seen_at.desc()).offset(offset).limit(limit).all()
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.get("/products/{product_id}/price-history", response_model=List)
def get_product_price_history(
    product_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.product import PriceHistory
    from app.schemas.product import PriceHistoryResponse
    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.recorded_at.asc())
        .all()
    )
    return [PriceHistoryResponse.model_validate(h) for h in history]


# User Item Actions
@router.post("/item-actions", response_model=UserItemActionResponse)
def create_item_action(
    data: UserItemActionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Upsert - replace existing action for same product
    existing = db.query(UserItemAction).filter(
        UserItemAction.user_id == user.id,
        UserItemAction.product_id == data.product_id,
    ).first()

    if existing:
        existing.action = data.action
        db.commit()
        db.refresh(existing)
        return UserItemActionResponse.model_validate(existing)

    action = UserItemAction(
        user_id=user.id,
        product_id=data.product_id,
        action=data.action,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return UserItemActionResponse.model_validate(action)


@router.get("/item-actions", response_model=List[UserItemActionResponse])
def list_item_actions(
    action: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(UserItemAction).filter(UserItemAction.user_id == user.id)
    if action:
        query = query.filter(UserItemAction.action == action)
    return [UserItemActionResponse.model_validate(a) for a in query.all()]


# Activity log
@router.get("/activity", response_model=List[SearchRunLogResponse])
def get_activity_log(
    limit: int = Query(30, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get global activity log across all searches."""
    logs = (
        db.query(SearchRunLog)
        .filter(SearchRunLog.user_id == user.id)
        .order_by(SearchRunLog.created_at.desc())
        .limit(limit)
        .all()
    )
    results = []
    for log in logs:
        data = SearchRunLogResponse.model_validate(log)
        search = db.query(SavedSearch).filter(SavedSearch.id == log.search_id).first()
        if search:
            data.search_name = search.name
        results.append(data)
    return results


# Job runner endpoint
@router.post("/jobs/run-searches")
def run_all_due_searches(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run all due search jobs for the current user."""
    from app.services.monitor import get_due_searches, run_search_job
    due = get_due_searches(db)
    user_due = [s for s in due if s.user_id == user.id]
    results = []
    for search in user_due:
        stats = run_search_job(db, search, user)
        results.append({"search_id": search.id, "search_name": search.name, "stats": stats})
    return {"ok": True, "searches_run": len(results), "results": results}


@router.post("/jobs/run-all")
def run_all_searches_now(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force run ALL active searches for the user (ignoring schedule)."""
    from app.services.monitor import run_search_job
    searches = db.query(SavedSearch).filter(
        SavedSearch.user_id == user.id,
        SavedSearch.status == "active",
    ).all()
    results = []
    for search in searches:
        stats = run_search_job(db, search, user)
        results.append({"search_id": search.id, "search_name": search.name, "stats": stats})
    return {"ok": True, "searches_run": len(results), "results": results}
