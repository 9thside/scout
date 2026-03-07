import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Product } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Inbox as InboxIcon,
  ExternalLink,
  Heart,
  X,
  ShoppingCart,
  Search,
  Filter,
} from "lucide-react";

export default function Inbox() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [saleFilter, setSaleFilter] = useState("all");

  const loadProducts = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { limit: "100" };
      if (searchQuery) params.search_query = searchQuery;
      if (categoryFilter !== "all") params.category = categoryFilter;
      if (saleFilter === "on_sale") params.on_sale = "true";
      const data = (await api.getProducts(params)) as Product[];
      setProducts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [categoryFilter, saleFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadProducts();
  };

  const handleItemAction = async (productId: number, action: string) => {
    try {
      await api.createItemAction({ product_id: productId, action });
      if (action === "dismissed") {
        setProducts((prev) => prev.filter((p) => p.id !== productId));
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">Discoveries</h1>
        <p className="text-sm text-zinc-500">
          Everything Scout has found for you across all searches
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <form onSubmit={handleSearch} className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search your discoveries..."
              className="pl-9"
            />
          </div>
        </form>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-40">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="Outerwear">Outerwear</SelectItem>
            <SelectItem value="Shoes">Shoes</SelectItem>
            <SelectItem value="Furniture">Furniture</SelectItem>
            <SelectItem value="Watches">Watches</SelectItem>
            <SelectItem value="Bags">Bags</SelectItem>
            <SelectItem value="Electronics">Electronics</SelectItem>
            <SelectItem value="Home Decor">Home Decor</SelectItem>
            <SelectItem value="General">General</SelectItem>
          </SelectContent>
        </Select>
        <Select value={saleFilter} onValueChange={setSaleFilter}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Items</SelectItem>
            <SelectItem value="on_sale">On Sale</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Products Grid */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-80 rounded-xl" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <Card className="border-zinc-200/80 shadow-sm">
          <CardContent className="flex flex-col items-center py-16">
            <InboxIcon className="mb-4 h-10 w-10 text-zinc-300" />
            <p className="text-sm font-medium text-zinc-900">Nothing here yet</p>
            <p className="mt-1 text-xs text-zinc-500">
              Run a search and Scout will start filling your inbox with finds
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {products.map((product) => (
            <Card
              key={product.id}
              className="group overflow-hidden border-zinc-200/80 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="relative aspect-square bg-zinc-100">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.title}
                    className="h-full w-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                ) : (
                  <div className="flex h-full items-center justify-center">
                    <ShoppingCart className="h-8 w-8 text-zinc-300" />
                  </div>
                )}
                {product.is_on_sale && (
                  <Badge className="absolute left-2 top-2 bg-green-500 text-white text-xs">
                    {product.discount_percent ? `${product.discount_percent.toFixed(0)}% OFF` : "SALE"}
                  </Badge>
                )}
                {/* Hover Actions */}
                <div className="absolute inset-x-0 bottom-0 flex justify-center gap-2 bg-gradient-to-t from-black/50 to-transparent p-3 opacity-0 transition-opacity group-hover:opacity-100">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleItemAction(product.id, "liked")}
                    className="gap-1 text-xs"
                  >
                    <Heart className="h-3 w-3" />Save
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleItemAction(product.id, "dismissed")}
                    className="gap-1 text-xs"
                  >
                    <X className="h-3 w-3" />Dismiss
                  </Button>
                </div>
              </div>
              <CardContent className="p-3">
                <p className="truncate text-sm font-medium text-zinc-900">
                  {product.title}
                </p>
                <p className="text-xs text-zinc-500">
                  {product.brand}{product.source ? ` · ${product.source}` : ""}
                </p>
                <div className="mt-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {product.price !== null && (
                      <span className="text-sm font-semibold text-zinc-900">
                        ${product.price.toFixed(0)}
                      </span>
                    )}
                    {product.original_price && (
                      <span className="text-xs text-zinc-400 line-through">
                        ${product.original_price.toFixed(0)}
                      </span>
                    )}
                  </div>
                  {product.product_url && (
                    <a href={product.product_url} target="_blank" rel="noopener noreferrer">
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Button>
                    </a>
                  )}
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {product.condition !== "new" && (
                    <Badge variant="outline" className="text-xs">{product.condition}</Badge>
                  )}
                  {product.availability === "limited" && (
                    <Badge variant="outline" className="border-amber-200 bg-amber-50 text-amber-700 text-xs">
                      Limited
                    </Badge>
                  )}
                  {product.availability === "out_of_stock" && (
                    <Badge variant="outline" className="border-red-200 bg-red-50 text-red-700 text-xs">
                      Out of Stock
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
