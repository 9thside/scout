"""
Relevance scoring engine for matching products to saved searches.

Architecture note: This module uses a rules-based scoring pipeline that produces
human-readable "why this matched" explanations. The pipeline is structured so it
can be augmented with LLM-based ranking later:

  1. Replace compute_relevance_score() with an LLM call that takes
     (product, search) and returns (score, explanation).
  2. Or use the rules-based score as a pre-filter, then re-rank the top N
     results with an LLM for richer explanations.
  3. The match_reason field is already stored per product-search pair,
     so the UI will display LLM explanations with zero frontend changes.
"""
from typing import Optional
from app.models.saved_search import SavedSearch
from app.models.product import Product


def compute_relevance_score(product: Product, search: SavedSearch) -> tuple[float, str]:
    """
    Compute a relevance score (0-100) for how well a product matches a saved search.
    Returns (score, explanation) where explanation is a concise, consumer-friendly
    sentence describing why this item is a good match.
    """
    score = 0.0
    signals: list[str] = []
    highlights: list[str] = []

    # 1. Keyword match (up to 40 points)
    keyword_score = _keyword_match_score(product, search.query)
    score += keyword_score
    if keyword_score > 25:
        highlights.append("strong keyword match")
    elif keyword_score > 10:
        highlights.append("partial keyword match")

    # 2. Category match (up to 10 points)
    if search.category and product.category:
        if search.category.lower() == product.category.lower():
            score += 10
            signals.append("category")

    # 3. Brand preference (up to 15 points)
    if product.brand:
        brand_lower = product.brand.lower()
        preferred = [b.lower() for b in (search.preferred_brands or [])]
        excluded = [b.lower() for b in (search.excluded_brands or [])]
        if brand_lower in excluded:
            score -= 30
            highlights.append("excluded brand")
        elif brand_lower in preferred:
            score += 15
            signals.append("preferred brand")

    # 4. Budget alignment (up to 15 points)
    if product.price is not None:
        budget_score = _budget_alignment_score(product.price, search)
        score += budget_score
        if budget_score >= 12:
            signals.append("great price fit")
        elif budget_score >= 7:
            signals.append("good price fit")

    # 5. Style profile influence (up to 10 points)
    style_score = _style_profile_score(product, search.style_profile)
    score += style_score
    if style_score >= 8:
        signals.append("matches your style")

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
        signals.append("size match")

    # 8. Sale / discount bonus (up to 5 points)
    if product.is_on_sale and product.discount_percent:
        if product.discount_percent >= 30:
            score += 5
            signals.append(f"{int(product.discount_percent)}% off")
        elif product.discount_percent >= 15:
            score += 3
            signals.append("on sale")

    # Clamp score
    score = max(0.0, min(100.0, score))

    # Generate consumer-friendly explanation
    explanation = _generate_explanation(product, search, signals, highlights, score)
    return score, explanation


def _generate_explanation(
    product: Product,
    search: SavedSearch,
    signals: list[str],
    highlights: list[str],
    score: float,
) -> str:
    """
    Generate a concise, consumer-friendly explanation of why this product matched.
    Designed to read like a personal shopper's note.

    Future: Replace this with an LLM call for richer, more contextual explanations.
    The function signature stays the same -- just swap the implementation.
    """
    parts: list[str] = []

    has_brand = "preferred brand" in signals
    has_style = "matches your style" in signals
    has_price = "great price fit" in signals or "good price fit" in signals
    has_sale = any("off" in s or s == "on sale" for s in signals)

    if has_brand and has_price:
        parts.append("From a brand you love, and fits your budget")
    elif has_brand and has_style:
        parts.append("A brand you love that matches your style")
    elif has_brand:
        parts.append("From one of your preferred brands")
    elif has_style and has_price:
        parts.append("Matches your style and budget")
    elif has_style:
        parts.append("Fits your style profile")
    elif has_price and has_sale:
        parts.append("Great deal — fits your budget and currently on sale")
    elif has_price:
        parts.append("Well within your budget")
    elif "strong keyword match" in highlights:
        parts.append("Closely matches what you're looking for")
    elif "partial keyword match" in highlights:
        parts.append("Partially matches your search")
    else:
        parts.append("Related to your search")

    if has_sale and "sale" not in " ".join(parts).lower():
        sale_signal = next((s for s in signals if "off" in s), None)
        if sale_signal:
            parts.append(sale_signal)

    return ". ".join(parts) if parts else "General match"


def _keyword_match_score(product: Product, query: str) -> float:
    """Score based on how many query keywords appear in product title/description."""
    if not query:
        return 0.0

    stop_words = {"a", "an", "the", "in", "on", "at", "for", "and", "or", "with", "under", "over", "to", "of"}
    keywords = [w for w in query.lower().split() if w not in stop_words and len(w) > 1]
    searchable = f"{product.title or ''} {product.description or ''} {product.brand or ''} {product.material or ''} {product.color or ''}".lower()

    if not keywords:
        return 0.0

    matched = sum(1 for kw in keywords if kw in searchable)
    return (matched / len(keywords)) * 40


def _budget_alignment_score(price: float, search: SavedSearch) -> float:
    """Score based on budget preference and price range."""
    score = 0.0

    if search.min_price is not None and price < search.min_price:
        return 0.0
    if search.max_price is not None and price > search.max_price:
        return -10.0

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
        score += 10

    return score


def _style_profile_score(product: Product, style_profile: Optional[str]) -> float:
    """Influence score based on style profile."""
    if not style_profile:
        return 5.0

    profile = style_profile.lower()

    premium_indicators = ["designer", "luxury", "premium", "exclusive", "limited"]
    product_text = f"{product.title or ''} {product.brand or ''} {product.description or ''}".lower()

    if profile in ("designer", "premium-brand"):
        if any(ind in product_text for ind in premium_indicators):
            return 10.0
        return 3.0
    elif profile == "niche":
        return 7.0
    elif profile == "trend-forward":
        return 6.0
    elif profile == "everyday":
        return 5.0
    else:
        return 5.0


def _variant_match_score(product: Product, search: SavedSearch) -> float:
    """Score based on size, color, material match."""
    score = 0.0

    if search.color and product.color:
        if search.color.lower() in product.color.lower():
            score += 2

    if search.material and product.material:
        if search.material.lower() in product.material.lower():
            score += 2

    if search.shoe_size and product.size:
        if search.shoe_size in product.size:
            score += 2

    if search.clothing_size and product.size:
        if search.clothing_size.lower() in product.size.lower():
            score += 2

    return min(score, 5.0)
