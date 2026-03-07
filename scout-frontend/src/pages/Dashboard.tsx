import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { DashboardStats, Alert, SavedSearch, Product } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Search,
  Bell,
  TrendingDown,
  Sparkles,
  Plus,
  RefreshCw,
  ArrowRight,
  ExternalLink,
  Tag,
  RotateCcw,
  ShoppingBag,
  CheckCircle2,
  AlertCircle,
  Zap,
  Eye,
  Trophy,
} from "lucide-react";

const ALERT_TYPE_CONFIG: Record<string, { icon: typeof Bell; color: string; label: string }> = {
  new_match: { icon: Sparkles, color: "bg-blue-50 text-blue-700 border-blue-200", label: "New Find" },
  price_drop: { icon: TrendingDown, color: "bg-emerald-50 text-emerald-700 border-emerald-200", label: "Price Drop" },
  sale: { icon: Tag, color: "bg-amber-50 text-amber-700 border-amber-200", label: "On Sale" },
  restock: { icon: RotateCcw, color: "bg-violet-50 text-violet-700 border-violet-200", label: "Back in Stock" },
};

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [topProducts, setTopProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const loadData = async () => {
    try {
      const [s, a, sr, prods] = await Promise.all([
        api.getDashboard() as Promise<DashboardStats>,
        api.getAlerts({ limit: "5" }) as Promise<Alert[]>,
        api.getSearches() as Promise<SavedSearch[]>,
        api.getProducts({ limit: "6", on_sale: "true" }) as Promise<Product[]>,
      ]);
      setStats(s);
      setAlerts(a);
      setSearches(sr);
      setTopProducts(prods);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunAll = async () => {
    setRunning(true);
    try {
      await api.runAllSearches();
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  const activeSearches = searches.filter((s) => s.status === "active");
  const hasData = activeSearches.length > 0;
  const greeting = new Date().getHours() < 12 ? "Good morning" : new Date().getHours() < 18 ? "Good afternoon" : "Good evening";

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-40 rounded-2xl" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-64 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 p-6 text-white sm:p-8">
        <div className="relative flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              {greeting}
            </h1>
            <p className="mt-1 text-sm text-zinc-400">
              {hasData
                ? `Scout is monitoring ${activeSearches.length} search${activeSearches.length !== 1 ? "es" : ""} for you`
                : "Your personal shopping concierge is ready"}
            </p>
          </div>
          <div className="flex gap-2">
            {hasData && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleRunAll}
                disabled={running}
                className="border-zinc-600 bg-transparent text-white hover:bg-zinc-700 hover:text-white"
              >
                <RefreshCw className={`mr-2 h-4 w-4 ${running ? "animate-spin" : ""}`} />
                {running ? "Scanning..." : "Scan now"}
              </Button>
            )}
            <Link to="/searches/new">
              <Button size="sm" className="bg-white text-zinc-900 hover:bg-zinc-100">
                <Plus className="mr-2 h-4 w-4" />
                New search
              </Button>
            </Link>
          </div>
        </div>

        {/* Quick Stats Strip */}
        {stats && hasData && (
          <div className="relative mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div className="rounded-xl bg-white/5 px-4 py-3 backdrop-blur-sm">
              <div className="flex items-center gap-2">
                <Eye className="h-4 w-4 text-zinc-400" />
                <span className="text-2xl font-semibold">{stats.total_active_searches}</span>
              </div>
              <p className="mt-0.5 text-xs text-zinc-400">Active searches</p>
            </div>
            <div className="rounded-xl bg-white/5 px-4 py-3 backdrop-blur-sm">
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4 text-zinc-400" />
                <span className="text-2xl font-semibold">{stats.total_alerts_this_week}</span>
              </div>
              <p className="mt-0.5 text-xs text-zinc-400">Alerts this week</p>
            </div>
            <div className="rounded-xl bg-white/5 px-4 py-3 backdrop-blur-sm">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-emerald-400" />
                <span className="text-2xl font-semibold">{stats.price_drops_count}</span>
              </div>
              <p className="mt-0.5 text-xs text-zinc-400">Prices dropped</p>
            </div>
            <div className="rounded-xl bg-white/5 px-4 py-3 backdrop-blur-sm">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-amber-400" />
                <span className="text-2xl font-semibold">{stats.new_items_count}</span>
              </div>
              <p className="mt-0.5 text-xs text-zinc-400">New discoveries</p>
            </div>
          </div>
        )}
      </div>

      {/* Best Opportunities */}
      {topProducts.length > 0 && (
        <div>
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-amber-500" />
              <h2 className="text-lg font-semibold text-zinc-900">Best opportunities</h2>
            </div>
            <Link to="/inbox">
              <Button variant="ghost" size="sm" className="gap-1 text-xs text-zinc-500">
                View all <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {topProducts.slice(0, 3).map((product) => (
              <Card key={product.id} className="group overflow-hidden border-zinc-200/80 shadow-sm transition-all hover:shadow-md">
                <div className="relative aspect-[4/3] bg-zinc-100">
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.title}
                      className="h-full w-full object-cover transition-transform group-hover:scale-105"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <ShoppingBag className="h-8 w-8 text-zinc-300" />
                    </div>
                  )}
                  {product.discount_percent && product.discount_percent > 0 && (
                    <Badge className="absolute left-2.5 top-2.5 bg-emerald-500 text-white shadow-sm">
                      {product.discount_percent.toFixed(0)}% off
                    </Badge>
                  )}
                </div>
                <CardContent className="p-4">
                  <p className="truncate text-sm font-medium text-zinc-900">{product.title}</p>
                  <p className="mt-0.5 text-xs text-zinc-500">
                    {product.brand}{product.source ? ` · ${product.source}` : ""}
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    {product.price !== null && (
                      <span className="text-base font-semibold text-zinc-900">${product.price.toFixed(0)}</span>
                    )}
                    {product.original_price && (
                      <span className="text-sm text-zinc-400 line-through">${product.original_price.toFixed(0)}</span>
                    )}
                  </div>
                  {product.match_reason && (
                    <div className="mt-2 flex items-start gap-1.5">
                      <Zap className="mt-0.5 h-3 w-3 shrink-0 text-amber-500" />
                      <p className="text-xs leading-relaxed text-zinc-500">{product.match_reason}</p>
                    </div>
                  )}
                  {product.product_url && (
                    <a href={product.product_url} target="_blank" rel="noopener noreferrer" className="mt-3 block">
                      <Button variant="outline" size="sm" className="w-full gap-1.5 text-xs">
                        <ExternalLink className="h-3 w-3" />
                        View deal
                      </Button>
                    </a>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Two-Column: Alerts + Searches */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Alerts */}
        <Card className="border-zinc-200/80 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="text-base font-medium">Latest alerts</CardTitle>
            <Link to="/alerts">
              <Button variant="ghost" size="sm" className="gap-1 text-xs text-zinc-500">
                See all <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {alerts.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-zinc-100">
                  <Bell className="h-5 w-5 text-zinc-400" />
                </div>
                <p className="text-sm font-medium text-zinc-900">No alerts yet</p>
                <p className="mt-1 max-w-xs text-xs text-zinc-500">
                  {hasData
                    ? "Run a scan and Scout will alert you when it finds deals, price drops, or new items"
                    : "Create a search to start discovering items you'll love"}
                </p>
                {!hasData && (
                  <Link to="/searches/new" className="mt-3">
                    <Button variant="outline" size="sm" className="gap-1.5">
                      <Plus className="h-3.5 w-3.5" />Create your first search
                    </Button>
                  </Link>
                )}
              </div>
            ) : (
              <div className="space-y-2.5">
                {alerts.map((alert) => {
                  const config = ALERT_TYPE_CONFIG[alert.alert_type] || ALERT_TYPE_CONFIG.new_match;
                  const Icon = config.icon;
                  return (
                    <div
                      key={alert.id}
                      className={`flex items-start gap-3 rounded-lg border p-3 transition-colors ${
                        alert.is_read ? "bg-white border-zinc-200" : "bg-zinc-50/80 border-zinc-200"
                      }`}
                    >
                      <Badge variant="outline" className={`shrink-0 gap-1 ${config.color}`}>
                        <Icon className="h-3 w-3" />
                        {config.label}
                      </Badge>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-zinc-900">
                          {alert.title}
                        </p>
                        {alert.product?.price && (
                          <p className="text-xs text-zinc-500">
                            ${alert.product.price.toFixed(0)}
                            {alert.product.original_price && (
                              <span className="ml-1 line-through text-zinc-400">
                                ${alert.product.original_price.toFixed(0)}
                              </span>
                            )}
                            {alert.product.source && ` · ${alert.product.source}`}
                          </p>
                        )}
                      </div>
                      {alert.product?.product_url && (
                        <a
                          href={alert.product.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="shrink-0"
                        >
                          <ExternalLink className="h-4 w-4 text-zinc-400 hover:text-zinc-600" />
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Active Searches */}
        <Card className="border-zinc-200/80 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="text-base font-medium">Your searches</CardTitle>
            <Link to="/searches">
              <Button variant="ghost" size="sm" className="gap-1 text-xs text-zinc-500">
                Manage <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {activeSearches.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-zinc-100">
                  <Search className="h-5 w-5 text-zinc-400" />
                </div>
                <p className="text-sm font-medium text-zinc-900">Tell Scout what to look for</p>
                <p className="mt-1 max-w-xs text-xs text-zinc-500">
                  Describe what you want — a specific jacket, niche sneakers, a vintage watch — and Scout will monitor the market for you
                </p>
                <Link to="/searches/new" className="mt-3">
                  <Button size="sm" className="gap-1.5">
                    <Plus className="h-3.5 w-3.5" />Create your first search
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-2.5">
                {activeSearches.slice(0, 5).map((search) => (
                    <Link
                      key={search.id}
                      to={`/searches/${search.id}`}
                      className="flex items-center justify-between rounded-lg border border-zinc-200 p-3 transition-all hover:bg-zinc-50 hover:shadow-sm"
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <ShoppingBag className="h-4 w-4 text-zinc-400" />
                          <p className="truncate text-sm font-medium text-zinc-900">
                            {search.name}
                          </p>
                          {search.last_run_status && (
                            search.last_run_status === "success" ? (
                              <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-500" />
                            ) : (
                              <AlertCircle className="h-3.5 w-3.5 shrink-0 text-amber-500" />
                            )
                          )}
                        </div>
                        <p className="mt-0.5 truncate text-xs text-zinc-500">
                          {search.query}
                          {search.last_checked_at && (
                            <span className="text-zinc-400"> · scanned {timeAgo(search.last_checked_at)}</span>
                          )}
                        </p>
                      </div>
                      <div className="ml-3 flex shrink-0 items-center gap-2">
                        {search.match_count > 0 && (
                          <Badge variant="secondary" className="text-xs">
                            {search.match_count} {search.match_count === 1 ? "find" : "finds"}
                          </Badge>
                        )}
                        <ArrowRight className="h-4 w-4 text-zinc-400" />
                      </div>
                    </Link>
                  ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
