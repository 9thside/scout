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

    # Reliable product images using picsum.photos (always-available placeholder service)
    # Uses /id/{number} format which always works reliably
    CATEGORY_IMAGES = {
        "Outerwear": [
            "https://picsum.photos/id/1/400/400",
            "https://picsum.photos/id/10/400/400",
            "https://picsum.photos/id/100/400/400",
            "https://picsum.photos/id/1000/400/400",
            "https://picsum.photos/id/1001/400/400",
            "https://picsum.photos/id/1002/400/400",
            "https://picsum.photos/id/1003/400/400",
            "https://picsum.photos/id/1004/400/400",
        ],
        "Shoes": [
            "https://picsum.photos/id/1005/400/400",
            "https://picsum.photos/id/1006/400/400",
            "https://picsum.photos/id/101/400/400",
            "https://picsum.photos/id/102/400/400",
            "https://picsum.photos/id/103/400/400",
            "https://picsum.photos/id/104/400/400",
            "https://picsum.photos/id/106/400/400",
            "https://picsum.photos/id/107/400/400",
        ],
        "Furniture": [
            "https://picsum.photos/id/108/400/400",
            "https://picsum.photos/id/109/400/400",
            "https://picsum.photos/id/11/400/400",
            "https://picsum.photos/id/110/400/400",
            "https://picsum.photos/id/111/400/400",
            "https://picsum.photos/id/112/400/400",
            "https://picsum.photos/id/113/400/400",
            "https://picsum.photos/id/114/400/400",
        ],
        "Watches": [
            "https://picsum.photos/id/115/400/400",
            "https://picsum.photos/id/116/400/400",
            "https://picsum.photos/id/117/400/400",
            "https://picsum.photos/id/118/400/400",
            "https://picsum.photos/id/119/400/400",
            "https://picsum.photos/id/12/400/400",
            "https://picsum.photos/id/120/400/400",
            "https://picsum.photos/id/121/400/400",
        ],
        "Bags": [
            "https://picsum.photos/id/122/400/400",
            "https://picsum.photos/id/123/400/400",
            "https://picsum.photos/id/124/400/400",
            "https://picsum.photos/id/125/400/400",
            "https://picsum.photos/id/126/400/400",
            "https://picsum.photos/id/127/400/400",
            "https://picsum.photos/id/128/400/400",
            "https://picsum.photos/id/129/400/400",
        ],
        "Electronics": [
            "https://picsum.photos/id/13/400/400",
            "https://picsum.photos/id/130/400/400",
            "https://picsum.photos/id/131/400/400",
            "https://picsum.photos/id/132/400/400",
            "https://picsum.photos/id/133/400/400",
            "https://picsum.photos/id/134/400/400",
            "https://picsum.photos/id/135/400/400",
            "https://picsum.photos/id/136/400/400",
        ],
        "Home Decor": [
            "https://picsum.photos/id/137/400/400",
            "https://picsum.photos/id/139/400/400",
            "https://picsum.photos/id/14/400/400",
            "https://picsum.photos/id/140/400/400",
            "https://picsum.photos/id/141/400/400",
            "https://picsum.photos/id/142/400/400",
            "https://picsum.photos/id/143/400/400",
            "https://picsum.photos/id/144/400/400",
        ],
        "General": [
            "https://picsum.photos/id/145/400/400",
            "https://picsum.photos/id/146/400/400",
            "https://picsum.photos/id/147/400/400",
            "https://picsum.photos/id/149/400/400",
            "https://picsum.photos/id/15/400/400",
            "https://picsum.photos/id/150/400/400",
            "https://picsum.photos/id/151/400/400",
            "https://picsum.photos/id/152/400/400",
        ],
    }

    # Real retailer product URL patterns (use Google Shopping as reliable fallback)
    SOURCE_URLS = {
        "Nordstrom": "https://www.google.com/search?q={query}+site:nordstrom.com&tbm=shop",
        "SSENSE": "https://www.ssense.com/en-us/search?q={query}",
        "Mr Porter": "https://www.google.com/search?q={query}+site:mrporter.com&tbm=shop",
        "END.": "https://www.endclothing.com/us/catalogsearch/result/?q={query}",
        "Grailed": "https://www.grailed.com/shop?query={query}",
        "eBay": "https://www.ebay.com/sch/i.html?_nkw={query}",
        "Farfetch": "https://www.google.com/search?q={query}+site:farfetch.com&tbm=shop",
        "Net-a-Porter": "https://www.google.com/search?q={query}+site:net-a-porter.com&tbm=shop",
        "Shopbop": "https://www.google.com/search?q={query}+site:shopbop.com&tbm=shop",
        "Matches Fashion": "https://www.google.com/search?q={query}+site:matchesfashion.com&tbm=shop",
        "The RealReal": "https://www.google.com/search?q={query}+site:therealreal.com&tbm=shop",
        "Vestiaire Collective": "https://www.google.com/search?q={query}+site:vestiairecollective.com&tbm=shop",
    }

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

            # Use real category-appropriate images from Unsplash
            cat_images = self.CATEGORY_IMAGES.get(cat, self.CATEGORY_IMAGES["General"])
            image_url = cat_images[random.randint(0, len(cat_images) - 1)]

            # Generate working search URLs on real retailer sites
            search_query = title.replace(" ", "+")
            url_template = self.SOURCE_URLS.get(source, "https://www.google.com/search?q={query}")
            product_url = url_template.format(query=search_query, slug=title.lower().replace(" ", "-"))

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
