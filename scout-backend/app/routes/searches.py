"""Saved search CRUD routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.saved_search import SavedSearch, SearchRunLog
from app.models.alert import SearchMatch, Alert
from app.models.product import Product, PriceHistory
from app.schemas.saved_search import SavedSearchCreate, SavedSearchUpdate, SavedSearchResponse, SearchRunLogResponse
from app.schemas.product import ProductWithMatchInfo, PriceHistoryResponse
from app.schemas.alert import AlertResponse
from app.services.auth import get_current_user
from app.services.monitor import run_search_job

router = APIRouter(prefix="/api/searches", tags=["searches"])


@router.get("", response_model=List[SavedSearchResponse])
def list_searches(
    status: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(SavedSearch).filter(SavedSearch.user_id == user.id)
    if status:
        query = query.filter(SavedSearch.status == status)
    searches = query.order_by(SavedSearch.created_at.desc()).all()
    return [SavedSearchResponse.model_validate(s) for s in searches]


@router.post("", response_model=SavedSearchResponse)
def create_search(
    data: SavedSearchCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = SavedSearch(
        user_id=user.id,
        **data.model_dump(),
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return SavedSearchResponse.model_validate(search)


@router.get("/{search_id}", response_model=SavedSearchResponse)
def get_search(
    search_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    return SavedSearchResponse.model_validate(search)


@router.put("/{search_id}", response_model=SavedSearchResponse)
def update_search(
    search_id: int,
    data: SavedSearchUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(search, key, value)

    db.commit()
    db.refresh(search)
    return SavedSearchResponse.model_validate(search)


@router.delete("/{search_id}")
def delete_search(
    search_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    db.delete(search)
    db.commit()
    return {"ok": True}


@router.post("/{search_id}/duplicate", response_model=SavedSearchResponse)
def duplicate_search(
    search_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    new_search = SavedSearch(
        user_id=user.id,
        name=f"{search.name} (copy)",
        query=search.query,
        category=search.category,
        style_profile=search.style_profile,
        budget_preference=search.budget_preference,
        min_price=search.min_price,
        max_price=search.max_price,
        condition=search.condition,
        preferred_brands=search.preferred_brands,
        excluded_brands=search.excluded_brands,
        clothing_size=search.clothing_size,
        shoe_size=search.shoe_size,
        color=search.color,
        material=search.material,
        dimensions=search.dimensions,
        gender_fit=search.gender_fit,
        notify_sms=search.notify_sms,
        notify_whatsapp=search.notify_whatsapp,
        notify_new_matches=search.notify_new_matches,
        notify_price_drops=search.notify_price_drops,
        notify_sales=search.notify_sales,
        notify_restocks=search.notify_restocks,
        digest_frequency=search.digest_frequency,
        search_frequency=search.search_frequency,
    )
    db.add(new_search)
    db.commit()
    db.refresh(new_search)
    return SavedSearchResponse.model_validate(new_search)


@router.post("/{search_id}/run")
def run_search(
    search_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger a search job."""
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    stats = run_search_job(db, search, user)
    return {"ok": True, "stats": stats}


@router.get("/{search_id}/matches", response_model=List[ProductWithMatchInfo])
def get_search_matches(
    search_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    matches = (
        db.query(SearchMatch, Product)
        .join(Product, SearchMatch.product_id == Product.id)
        .filter(SearchMatch.search_id == search_id)
        .order_by(SearchMatch.relevance_score.desc())
        .all()
    )

    results = []
    for match, product in matches:
        data = ProductWithMatchInfo.model_validate(product)
        data.relevance_score = match.relevance_score
        data.match_reason = match.match_reason
        results.append(data)

    return results


@router.get("/{search_id}/alerts", response_model=List[AlertResponse])
def get_search_alerts(
    search_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    alerts = (
        db.query(Alert)
        .filter(Alert.search_id == search_id)
        .order_by(Alert.created_at.desc())
        .limit(100)
        .all()
    )

    results = []
    for alert in alerts:
        data = AlertResponse.model_validate(alert)
        if alert.product_id:
            product = db.query(Product).filter(Product.id == alert.product_id).first()
            if product:
                from app.schemas.product import ProductResponse
                data.product = ProductResponse.model_validate(product)
        data.search_name = search.name
        results.append(data)

    return results


@router.get("/{search_id}/activity", response_model=List[SearchRunLogResponse])
def get_search_activity(
    search_id: int,
    limit: int = Query(20, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get activity log for a search."""
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    logs = (
        db.query(SearchRunLog)
        .filter(SearchRunLog.search_id == search_id)
        .order_by(SearchRunLog.created_at.desc())
        .limit(limit)
        .all()
    )
    results = []
    for log in logs:
        data = SearchRunLogResponse.model_validate(log)
        data.search_name = search.name
        results.append(data)
    return results


@router.get("/{search_id}/price-history", response_model=List[PriceHistoryResponse])
def get_search_price_history(
    search_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id, SavedSearch.user_id == user.id
    ).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    # Get all product IDs matched to this search
    match_product_ids = (
        db.query(SearchMatch.product_id)
        .filter(SearchMatch.search_id == search_id)
        .all()
    )
    product_ids = [pid for (pid,) in match_product_ids]

    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id.in_(product_ids))
        .order_by(PriceHistory.recorded_at.desc())
        .limit(200)
        .all()
    )

    return [PriceHistoryResponse.model_validate(h) for h in history]
