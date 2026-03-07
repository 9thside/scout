"""Relevance scoring engine for matching products to saved searches."""
from typing import Optional, List
from app.models.saved_search import SavedSearch
from app.models.product import Product


def compute_relevance_score(product: Product, search: SavedSearch) -> tuple[float, str]:
    """
    Compute a relevance score (0-100) for how well a product matches a saved search.
    Returns (score, match_reason).
    """
    score = 0.0
    reasons: list[str] = []

    # 1. Keyword match (up to 40 points)
    keyword_score = _keyword_match_score(product, search.query)
    score += keyword_score
    if keyword_score > 20:
        reasons.append("Strong keyword match")
    elif keyword_score > 10:
        reasons.append("Partial keyword match")

    # 2. Category match (up to 10 points)
    if search.category and product.category:
        if search.category.lower() == product.category.lower():
            score += 10
            reasons.append("Category match")

    # 3. Brand preference (up to 15 points)
    if product.brand:
        brand_lower = product.brand.lower()
        preferred = [b.lower() for b in (search.preferred_brands or [])]
        excluded = [b.lower() for b in (search.excluded_brands or [])]
        if brand_lower in excluded:
            score -= 30
            reasons.append("Excluded brand")
        elif brand_lower in preferred:
            score += 15
            reasons.append(f"Preferred brand: {product.brand}")

    # 4. Budget alignment (up to 15 points)
    if product.price is not None:
        budget_score = _budget_alignment_score(product.price, search)
        score += budget_score
        if budget_score > 10:
            reasons.append("Great price fit")
        elif budget_score > 5:
            reasons.append("Good price fit")

    # 5. Style profile influence (up to 10 points)
    style_score = _style_profile_score(product, search.style_profile)
    score += style_score

    # 6. Condition match (up to 5 points)
    if search.condition:
        if search.condition == "new_only" and product.condition == "new":
            score += 5
        elif search.condition == "new_resale":
            score += 5
        elif search.condition == "resale_only" and product.condition != "new":
            score += 5

    # 7. Size/variant match (up to 5 points)
    variant_score = _variant_match_score(product, search)
    score += variant_score
    if variant_score > 0:
        reasons.append("Size/variant match")

    # Clamp score
    score = max(0.0, min(100.0, score))
    match_reason = ". ".join(reasons) if reasons else "General match"
    return score, match_reason


def _keyword_match_score(product: Product, query: str) -> float:
    """Score based on how many query keywords appear in product title/description."""
    if not query:
        return 0.0

    keywords = query.lower().split()
    searchable = f"{product.title or ''} {product.description or ''} {product.brand or ''} {product.material or ''} {product.color or ''}".lower()

    matched = sum(1 for kw in keywords if kw in searchable)
    if not keywords:
        return 0.0
    return (matched / len(keywords)) * 40


def _budget_alignment_score(price: float, search: SavedSearch) -> float:
    """Score based on budget preference and price range."""
    score = 0.0

    # Check hard price limits
    if search.min_price is not None and price < search.min_price:
        return 0.0
    if search.max_price is not None and price > search.max_price:
        return -10.0

    # Budget preference scoring
    budget_ranges = {
        "value": (0, 100),
        "mid-range": (50, 300),
        "premium": (200, 800),
        "luxury": (500, float("inf")),
    }

    pref = (search.budget_preference or "any").lower()
    if pref in budget_ranges:
        low, high = budget_ranges[pref]
        if low <= price <= high:
            score += 15
        elif price < low:
            score += 5
        else:
            score += 2
    else:
        score += 10  # "any" budget gets moderate score

    return score


def _style_profile_score(product: Product, style_profile: Optional[str]) -> float:
    """Influence score based on style profile."""
    if not style_profile:
        return 5.0

    profile = style_profile.lower()

    # Premium brands get boosted for premium/designer profiles
    premium_indicators = ["designer", "luxury", "premium", "exclusive", "limited"]
    product_text = f"{product.title or ''} {product.brand or ''} {product.description or ''}".lower()

    if profile in ("designer", "premium-brand"):
        if any(ind in product_text for ind in premium_indicators):
            return 10.0
        return 3.0
    elif profile == "niche":
        return 7.0  # Niche items get moderate boost
    elif profile == "trend-forward":
        return 6.0
    elif profile == "everyday":
        return 5.0
    else:
        return 5.0  # "open" or unknown


def _variant_match_score(product: Product, search: SavedSearch) -> float:
    """Score based on size, color, material match."""
    score = 0.0
    checks = 0

    if search.color and product.color:
        checks += 1
        if search.color.lower() in product.color.lower():
            score += 2

    if search.material and product.material:
        checks += 1
        if search.material.lower() in product.material.lower():
            score += 2

    if search.shoe_size and product.size:
        checks += 1
        if search.shoe_size in product.size:
            score += 2

    if search.clothing_size and product.size:
        checks += 1
        if search.clothing_size.lower() in product.size.lower():
            score += 2

    return min(score, 5.0)
