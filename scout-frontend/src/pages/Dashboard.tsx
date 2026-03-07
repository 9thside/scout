import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { DashboardStats, Alert, SavedSearch } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Search,
  Bell,
  TrendingDown,
  Sparkles,
  Heart,
  Plus,
  RefreshCw,
  ArrowRight,
  ExternalLink,
  Tag,
  RotateCcw,
  ShoppingBag,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

const ALERT_TYPE_CONFIG: Record<string, { icon: typeof Bell; color: string; label: string }> = {
  new_match: { icon: Sparkles, color: "bg-blue-50 text-blue-700 border-blue-200", label: "New Find" },
  price_drop: { icon: TrendingDown, color: "bg-green-50 text-green-700 border-green-200", label: "Price Drop" },
  sale: { icon: Tag, color: "bg-orange-50 text-orange-700 border-orange-200", label: "On Sale" },
  restock: { icon: RotateCcw, color: "bg-purple-50 text-purple-700 border-purple-200", label: "Back in Stock" },
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
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const loadData = async () => {
    try {
      const [s, a, sr] = await Promise.all([
        api.getDashboard() as Promise<DashboardStats>,
        api.getAlerts({ limit: "5" }) as Promise<Alert[]>,
        api.getSearches() as Promise<SavedSearch[]>,
      ]);
      setStats(s);
      setAlerts(a);
      setSearches(sr);
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 18 ? "afternoon" : "evening"}
          </h1>
          <p className="text-sm text-zinc-500">
            Here's what Scout has been finding for you
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleRunAll} disabled={running}>
            <RefreshCw className={`mr-2 h-4 w-4 ${running ? "animate-spin" : ""}`} />
            {running ? "Scanning..." : "Scan now"}
          </Button>
          <Link to="/searches/new">
            <Button size="sm">
              <Plus className="mr-2 h-4 w-4" />
              New search
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <Card className="border-zinc-200/80 shadow-sm">
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-100">
                  <Search className="h-5 w-5 text-zinc-600" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-zinc-900">{stats.total_active_searches}</p>
                  <p className="text-xs text-zinc-500">Watching for you</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-zinc-200/80 shadow-sm">
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
                  <Bell className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-zinc-900">{stats.total_alerts_this_week}</p>
                  <p className="text-xs text-zinc-500">Alerts this week</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-zinc-200/80 shadow-sm">
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-50">
                  <TrendingDown className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-zinc-900">{stats.price_drops_count}</p>
                  <p className="text-xs text-zinc-500">Prices dropped</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-zinc-200/80 shadow-sm">
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-50">
                  <Sparkles className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-zinc-900">{stats.new_items_count}</p>
                  <p className="text-xs text-zinc-500">New discoveries</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-zinc-200/80 shadow-sm">
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-pink-50">
                  <Heart className="h-5 w-5 text-pink-600" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-zinc-900">{stats.saved_items_count}</p>
                  <p className="text-xs text-zinc-500">Items saved</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

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
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Bell className="mb-3 h-8 w-8 text-zinc-300" />
                <p className="text-sm text-zinc-500">No alerts yet</p>
                <p className="text-xs text-zinc-400">Run a search to start discovering items</p>
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
            {searches.filter((s) => s.status === "active").length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Search className="mb-3 h-8 w-8 text-zinc-300" />
                <p className="text-sm text-zinc-500">No searches yet</p>
                <Link to="/searches/new">
                  <Button variant="outline" size="sm" className="mt-3">
                    <Plus className="mr-2 h-4 w-4" />
                    Create your first search
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-2.5">
                {searches
                  .filter((s) => s.status === "active")
                  .slice(0, 5)
                  .map((search) => (
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
                              <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-green-500" />
                            ) : (
                              <AlertCircle className="h-3.5 w-3.5 shrink-0 text-amber-500" />
                            )
                          )}
                        </div>
                        <p className="mt-0.5 truncate text-xs text-zinc-500">
                          {search.query}
                          {search.last_checked_at && (
                            <span className="text-zinc-400"> · checked {timeAgo(search.last_checked_at)}</span>
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
