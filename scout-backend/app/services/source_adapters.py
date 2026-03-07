"""
Source adapters for product discovery.
Each adapter fetches products from a different source and normalizes them.

For MVP, we provide a mock adapter that generates realistic sample data.
The architecture supports adding real adapters (e.g., for specific retailers) later.
"""
import hashlib
import random
import datetime
from typing import List, Optional
from app.models.product import Product


class SourceAdapter:
    """Base class for source adapters."""
    name: str = "base"

    def search(self, query: str, category: Optional[str] = None, **kwargs) -> List[dict]:
        """Search for products. Returns list of normalized product dicts."""
        raise NotImplementedError


class MockSourceAdapter(SourceAdapter):
    """
    Mock adapter that generates realistic sample products.
    Useful for development and demonstrating the system.
    """
    name = "mock"

    # Realistic product data pools
    BRANDS = {
        "Outerwear": ["Canada Goose", "The North Face", "Moncler", "Arc'teryx", "Samsoe Samsoe", "Patagonia", "Mackage", "Moose Knuckles", "Woolrich", "Stone Island"],
        "Shoes": ["Common Projects", "GH Bass", "Gucci", "Dr. Martens", "Paraboot", "Alden", "Church's", "Cole Haan", "Allen Edmonds", "Nike"],
        "Furniture": ["West Elm", "CB2", "Article", "Room & Board", "Floyd", "Muuto", "HAY", "Restoration Hardware", "Crate & Barrel", "IKEA"],
        "Watches": ["Seiko", "Omega", "Tudor", "Casio", "Orient", "Hamilton", "Tissot", "Grand Seiko", "Nomos", "Swatch"],
        "Bags": ["Tumi", "Mismo", "Filson", "Bellroy", "Coach", "Louis Vuitton", "Goyard", "Aer", "Peak Design", "Freitag"],
        "Electronics": ["Sony", "Apple", "Samsung", "Bose", "Bang & Olufsen", "Sonos", "Marshall", "Sennheiser", "Dyson", "LG"],
        "Home Decor": ["Muji", "HAY", "West Elm", "Anthropologie", "CB2", "Zara Home", "H&M Home", "Target", "Schoolhouse", "Rejuvenation"],
        "General": ["Nike", "Adidas", "Uniqlo", "COS", "Everlane", "Aesop", "Le Labo", "Byredo", "Acne Studios", "A.P.C."],
    }

    SOURCES = ["Nordstrom", "SSENSE", "Mr Porter", "END.", "Grailed", "eBay", "Farfetch", "Net-a-Porter", "Shopbop", "Matches Fashion", "The RealReal", "Vestiaire Collective"]

    TEMPLATES = {
        "Outerwear": [
            "{brand} {adj} Puffer Jacket {detail}",
            "{brand} Wool Overcoat in {color}",
            "{brand} {adj} Down Parka",
            "{brand} Bomber Jacket in {material}",
            "{brand} Quilted {color} Vest",
        ],
        "Shoes": [
            "{brand} {adj} Leather Loafers",
            "{brand} Derby Shoes in {color}",
            "{brand} Chelsea Boots {detail}",
            "{brand} Suede {color} Sneakers",
            "{brand} {adj} Oxford Shoes",
        ],
        "Furniture": [
            "{brand} {adj} {material} Coffee Table",
            "{brand} {color} Accent Chair",
            "{brand} {material} Dining Table",
            "{brand} {adj} Bookshelf in {material}",
            "{brand} Credenza in {color} {material}",
        ],
        "Watches": [
            "{brand} {adj} Automatic Watch",
            "{brand} Chronograph in {color}",
            "{brand} Diver's Watch {detail}",
            "{brand} {adj} Dress Watch",
            "{brand} Field Watch in {color}",
        ],
        "Bags": [
            "{brand} {adj} Leather Tote",
            "{brand} {color} Crossbody Bag",
            "{brand} {material} Backpack",
            "{brand} {adj} Messenger Bag",
            "{brand} Weekender in {color}",
        ],
        "General": [
            "{brand} {adj} {color} T-Shirt",
            "{brand} Relaxed Fit {material} Pants",
            "{brand} {adj} Hoodie in {color}",
            "{brand} {color} Button-Down Shirt",
            "{brand} {adj} Knit Sweater",
        ],
    }

    ADJECTIVES = ["Premium", "Classic", "Modern", "Slim", "Relaxed", "Minimalist", "Heritage", "Limited Edition", "Signature", "Essential"]
    COLORS = ["Black", "Navy", "Charcoal", "Olive", "Tan", "White", "Grey", "Brown", "Burgundy", "Forest Green"]
    MATERIALS = ["Leather", "Wool", "Cotton", "Cashmere", "Denim", "Nylon", "Walnut", "Oak", "Linen", "Canvas"]
    DETAILS = ["with Fur Trim", "Water-Resistant", "Made in Italy", "Japanese Selvedge", "Hand-Stitched", "Organic", "Recycled", "Gore-Tex", "Titanium Case", "Swiss Movement"]
    CONDITIONS = ["new", "new", "new", "new", "used", "refurbished"]  # Weighted toward new

    def search(self, query: str, category: Optional[str] = None, **kwargs) -> List[dict]:
        """Generate mock products matching the query."""
        cat = category or "General"
        if cat not in self.TEMPLATES:
            cat = "General"

        brands = self.BRANDS.get(cat, self.BRANDS["General"])
        templates = self.TEMPLATES.get(cat, self.TEMPLATES["General"])

        num_results = random.randint(3, 8)
        products = []

        for _ in range(num_results):
            brand = random.choice(brands)
            adj = random.choice(self.ADJECTIVES)
            color = random.choice(self.COLORS)
            material = random.choice(self.MATERIALS)
            detail = random.choice(self.DETAILS)
            source = random.choice(self.SOURCES)
            template = random.choice(templates)

            title = template.format(brand=brand, adj=adj, color=color, material=material, detail=detail)

            # Price generation based on category and brand
            base_price = random.uniform(50, 1500)
            if cat in ("Watches", "Furniture"):
                base_price = random.uniform(150, 3000)
            elif cat == "Shoes":
                base_price = random.uniform(80, 800)

            price = round(base_price, 2)
            is_on_sale = random.random() < 0.3
            original_price = round(price * random.uniform(1.15, 1.6), 2) if is_on_sale else None
            discount = round((1 - price / original_price) * 100, 1) if original_price else None

            condition = random.choice(self.CONDITIONS)
            availability = random.choice(["in_stock", "in_stock", "in_stock", "limited", "out_of_stock"])

            # Generate fingerprint for dedup
            fingerprint = hashlib.md5(f"{title}:{source}:{price}".encode()).hexdigest()

            # Generate realistic image URLs (placeholder)
            image_url = f"https://images.unsplash.com/photo-{random.randint(1500000000, 1700000000)}-{hashlib.md5(title.encode()).hexdigest()[:12]}?w=400&h=400&fit=crop"

            product_url = f"https://{source.lower().replace(' ', '').replace('.', '')}.com/product/{hashlib.md5(title.encode()).hexdigest()[:8]}"

            products.append({
                "title": title,
                "source": source,
                "brand": brand,
                "category": cat,
                "price": price,
                "original_price": original_price,
                "discount_percent": discount,
                "currency": "USD",
                "image_url": image_url,
                "product_url": product_url,
                "availability": availability,
                "condition": condition,
                "size": kwargs.get("size"),
                "color": color,
                "material": material,
                "description": f"{title}. Available from {source}.",
                "fingerprint": fingerprint,
                "is_on_sale": is_on_sale,
            })

        # Filter by query keywords to make results more relevant
        query_words = query.lower().split() if query else []
        if query_words:
            scored = []
            for p in products:
                searchable = f"{p['title']} {p['brand']} {p['color']} {p['material']}".lower()
                match_count = sum(1 for w in query_words if w in searchable)
                scored.append((match_count, p))
            scored.sort(key=lambda x: x[0], reverse=True)
            products = [p for _, p in scored]

        return products


def get_source_adapters() -> List[SourceAdapter]:
    """Return all available source adapters."""
    return [MockSourceAdapter()]
