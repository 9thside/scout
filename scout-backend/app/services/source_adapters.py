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

    # Real product images from picsum.photos (reliable placeholder service)
    CATEGORY_IMAGES = {
        "Outerwear": [
            "https://images.unsplash.com/photo-1544923246-77307dd270cb?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1608063615781-e2ef8c73d114?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1548883354-94bcfe321cbb?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1611312449408-fcece27cdbb7?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1557418669-b85a26e4437c?w=400&h=400&fit=crop",
        ],
        "Shoes": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=400&h=400&fit=crop",
        ],
        "Furniture": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1618220179428-22790b461013?w=400&h=400&fit=crop",
        ],
        "Watches": [
            "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1539874754764-5a96559165b0?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1533139502658-0198f920d8e8?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1587925358603-c2eea5305bbc?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1614164185128-e4ec99c436d7?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=400&h=400&fit=crop",
        ],
        "Bags": [
            "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1547949003-9571a8d1e6cc?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1594223274512-ad4803739b7c?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1622560480654-d96214fdc887?w=400&h=400&fit=crop",
        ],
        "Electronics": [
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1546868871-af0de0ae72be?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1558089687-f282ffcbc126?w=400&h=400&fit=crop",
        ],
        "Home Decor": [
            "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1493397212122-2b85dda8106b?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=400&h=400&fit=crop",
        ],
        "General": [
            "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1434389677669-e08b4cda3a06?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1516762689617-e1cffcef479d?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&h=400&fit=crop",
            "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400&h=400&fit=crop",
        ],
    }

    # Real retailer product URL patterns
    SOURCE_URLS = {
        "Nordstrom": "https://www.nordstrom.com/s/search/{slug}",
        "SSENSE": "https://www.ssense.com/en-us/search?q={query}",
        "Mr Porter": "https://www.mrporter.com/en-us/mens/search?query={query}",
        "END.": "https://www.endclothing.com/us/catalogsearch/result/?q={query}",
        "Grailed": "https://www.grailed.com/shop?query={query}",
        "eBay": "https://www.ebay.com/sch/i.html?_nkw={query}",
        "Farfetch": "https://www.farfetch.com/shopping/men/search/items.aspx?q={query}",
        "Net-a-Porter": "https://www.net-a-porter.com/en-us/shop/search/{query}",
        "Shopbop": "https://www.shopbop.com/s?searchterm={query}",
        "Matches Fashion": "https://www.matchesfashion.com/us/search?q={query}",
        "The RealReal": "https://www.therealreal.com/search?q={query}",
        "Vestiaire Collective": "https://www.vestiairecollective.com/search/?q={query}",
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
