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

    # Real category-specific product images from Unsplash CDN (verified working)
    # Each category uses curated photos of actual products in that category
    CATEGORY_IMAGES = {
        "Outerwear": [
            "https://images.unsplash.com/photo-1611312449408-fcece27cdbb7?w=400&h=400&fit=crop&auto=format",  # denim jacket
            "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop&auto=format",  # winter jacket
            "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&h=400&fit=crop&auto=format",  # coat
            "https://images.unsplash.com/photo-1539533113208-f6df8cc8b543?w=400&h=400&fit=crop&auto=format",  # jacket
            "https://images.unsplash.com/photo-1548883354-94bcfe321cbb?w=400&h=400&fit=crop&auto=format",  # leather jacket
            "https://images.unsplash.com/photo-1521223890158-f9f7c3d5d504?w=400&h=400&fit=crop&auto=format",  # fur coat
            "https://images.unsplash.com/photo-1495105787522-5334e3ffa0ef?w=400&h=400&fit=crop&auto=format",  # blazer
            "https://images.unsplash.com/photo-1559551409-dadc959f76b8?w=400&h=400&fit=crop&auto=format",  # winter coat
        ],
        "Shoes": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop&auto=format",  # red Nike shoe
            "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop&auto=format",  # sneakers
            "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=400&h=400&fit=crop&auto=format",  # running shoes
            "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&h=400&fit=crop&auto=format",  # Jordan sneakers
            "https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=400&h=400&fit=crop&auto=format",  # Nike sneakers
            "https://images.unsplash.com/photo-1543508282-6319a3e2621f?w=400&h=400&fit=crop&auto=format",  # converse shoes
            "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop&auto=format",  # white sneakers
            "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop&auto=format",  # running shoe
        ],
        "Furniture": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop&auto=format",  # sofa
            "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=400&h=400&fit=crop&auto=format",  # modern furniture
            "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400&h=400&fit=crop&auto=format",  # interior
            "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=400&h=400&fit=crop&auto=format",  # mid century
            "https://images.unsplash.com/photo-1550581190-9c1c48d21d6c?w=400&h=400&fit=crop&auto=format",  # coffee table
            "https://images.unsplash.com/photo-1567538096621-38d2284b23ff?w=400&h=400&fit=crop&auto=format",  # furniture
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop&auto=format",  # living room
            "https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=400&h=400&fit=crop&auto=format",  # chair
        ],
        "Watches": [
            "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400&h=400&fit=crop&auto=format",  # classic watch
            "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=400&h=400&fit=crop&auto=format",  # luxury watch
            "https://images.unsplash.com/photo-1539874754764-5a96559165b0?w=400&h=400&fit=crop&auto=format",  # gold watch
            "https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=400&h=400&fit=crop&auto=format",  # wristwatch
            "https://images.unsplash.com/photo-1614164185128-e4ec99c436d7?w=400&h=400&fit=crop&auto=format",  # watch detail
            "https://images.unsplash.com/photo-1612817159949-195b6eb9e31a?w=400&h=400&fit=crop&auto=format",  # vintage watch
            "https://images.unsplash.com/photo-1618220179428-22790b461013?w=400&h=400&fit=crop&auto=format",  # smart watch
            "https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=400&h=400&fit=crop&auto=format",  # dress watch
        ],
        "Bags": [
            "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop&auto=format",  # leather bag
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop&auto=format",  # backpack
            "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400&h=400&fit=crop&auto=format",  # handbag
            "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400&h=400&fit=crop&auto=format",  # designer bag
            "https://images.unsplash.com/photo-1591561954557-26941169b49e?w=400&h=400&fit=crop&auto=format",  # leather bag
            "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=400&h=400&fit=crop&auto=format",  # tote bag
            "https://images.unsplash.com/photo-1594223274512-ad4803739b7c?w=400&h=400&fit=crop&auto=format",  # crossbody bag
            "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=400&h=400&fit=crop&auto=format",  # luxury bag
        ],
        "Electronics": [
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop&auto=format",  # headphones
            "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&h=400&fit=crop&auto=format",  # AirPods
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop&auto=format",  # headphones
            "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=400&h=400&fit=crop&auto=format",  # electronics
            "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&h=400&fit=crop&auto=format",  # gadgets
            "https://images.unsplash.com/photo-1519558260268-cde7e03a0152?w=400&h=400&fit=crop&auto=format",  # speaker
            "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=400&h=400&fit=crop&auto=format",  # tablet
            "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop&auto=format",  # laptop
        ],
        "Home Decor": [
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop&auto=format",  # decor
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop&auto=format",  # living room
            "https://images.unsplash.com/photo-1615529328331-f8917597711f?w=400&h=400&fit=crop&auto=format",  # vase
            "https://images.unsplash.com/photo-1563298723-dcfebaa392e3?w=400&h=400&fit=crop&auto=format",  # room decor
            "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=400&h=400&fit=crop&auto=format",  # bedroom
            "https://images.unsplash.com/photo-1501127122-f385ca6ddd9d?w=400&h=400&fit=crop&auto=format",  # minimalist room
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop&auto=format",  # sofa
            "https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=400&h=400&fit=crop&auto=format",  # chair
        ],
        "General": [
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=400&fit=crop&auto=format",  # store
            "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&h=400&fit=crop&auto=format",  # shopping
            "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=400&fit=crop&auto=format",  # fashion
            "https://images.unsplash.com/photo-1445205170230-053b83016050?w=400&h=400&fit=crop&auto=format",  # shopping bags
            "https://images.unsplash.com/photo-1607082349566-187342175e2f?w=400&h=400&fit=crop&auto=format",  # product
            "https://images.unsplash.com/photo-1560243563-062bfc001d68?w=400&h=400&fit=crop&auto=format",  # retail
            "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=400&h=400&fit=crop&auto=format",  # product display
            "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=400&h=400&fit=crop&auto=format",  # product
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
