import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { SavedSearch, Product, Alert, SearchRunLog, STYLE_PROFILES, BUDGET_PREFERENCES } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ArrowLeft,
  Edit,
  RefreshCw,
  Pause,
  Play,
  ExternalLink,
  Heart,
  X,
  ShoppingCart,
  TrendingDown,
  Sparkles,
  Tag,
  RotateCcw,
  Bell,
  Clock,
  CheckCircle2,
  AlertCircle,
  Activity,
} from "lucide-react";

const ALERT_ICONS: Record<string, typeof Bell> = {
  new_match: Sparkles,
  price_drop: TrendingDown,
  sale: Tag,
  restock: RotateCcw,
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

export default function SearchDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [search, setSearch] = useState<SavedSearch | null>(null);
  const [matches, setMatches] = useState<Product[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [activity, setActivity] = useState<SearchRunLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const loadData = async () => {
    if (!id) return;
    try {
      const [s, m, a, act] = await Promise.all([
        api.getSearch(Number(id)) as Promise<SavedSearch>,
        api.getSearchMatches(Number(id)) as Promise<Product[]>,
        api.getSearchAlerts(Number(id)) as Promise<Alert[]>,
        api.getSearchActivity(Number(id)) as Promise<SearchRunLog[]>,
      ]);
      setSearch(s);
      setMatches(m);
      setAlerts(a);
      setActivity(act);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleRun = async () => {
    if (!id) return;
    setRunning(true);
    try {
      await api.runSearch(Number(id));
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  const handleTogglePause = async () => {
    if (!search || !id) return;
    const newStatus = search.status === "active" ? "paused" : "active";
    await api.updateSearch(Number(id), { status: newStatus });
    await loadData();
  };

  const handleItemAction = async (productId: number, action: string) => {
    try {
      await api.createItemAction({ product_id: productId, action });
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-40 rounded-xl" />
        <Skeleton className="h-96 rounded-xl" />
      </div>
    );
  }

  if (!search) {
    return (
      <div className="py-16 text-center">
        <p className="text-zinc-500">Search not found</p>
        <Link to="/searches">
          <Button variant="outline" className="mt-4">Back to searches</Button>
        </Link>
      </div>
    );
  }

  const getStyleLabel = (v: string | null) =>
    STYLE_PROFILES.find((s) => s.value === v)?.label || v;
  const getBudgetLabel = (v: string | null) =>
    BUDGET_PREFERENCES.find((b) => b.value === v)?.label || v;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate("/searches")}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
                {search.name}
              </h1>
              <Badge variant={search.status === "active" ? "default" : "secondary"}>
                {search.status === "active" ? "Monitoring" : search.status === "paused" ? "Paused" : "Archived"}
              </Badge>
              {search.last_run_status && (
                search.last_run_status === "success" ? (
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-amber-500" />
                )
              )}
            </div>
            <p className="text-sm text-zinc-500">{search.query}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleTogglePause}>
            {search.status === "active" ? (
              <><Pause className="mr-2 h-4 w-4" />Pause</>
            ) : (
              <><Play className="mr-2 h-4 w-4" />Resume</>
            )}
          </Button>
          <Link to={`/searches/${id}/edit`}>
            <Button variant="outline" size="sm">
              <Edit className="mr-2 h-4 w-4" />Edit
            </Button>
          </Link>
          <Button size="sm" onClick={handleRun} disabled={running}>
            <RefreshCw className={`mr-2 h-4 w-4 ${running ? "animate-spin" : ""}`} />
            {running ? "Scanning..." : "Scan now"}
          </Button>
        </div>
      </div>

      {/* Search Settings Summary */}
      <Card className="border-zinc-200/80 shadow-sm">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-2">
            {search.category && <Badge variant="outline">{search.category}</Badge>}
            {search.style_profile && (
              <Badge variant="outline">{getStyleLabel(search.style_profile)}</Badge>
            )}
            {search.budget_preference && (
              <Badge variant="outline">{getBudgetLabel(search.budget_preference)}</Badge>
            )}
            {(search.min_price || search.max_price) && (
              <Badge variant="outline">
                ${search.min_price || 0} - ${search.max_price || "any"}
              </Badge>
            )}
            {search.condition && (
              <Badge variant="outline">
                {search.condition === "new_only" ? "New only" : search.condition === "new_resale" ? "New + Resale" : "Resale only"}
              </Badge>
            )}
            <Badge variant="outline" className="gap-1">
              <Clock className="h-3 w-3" />
              {search.search_frequency === "1h" ? "Every hour" : search.search_frequency === "6h" ? "Every 6 hours" : "Daily"}
            </Badge>
            <Badge variant="secondary">{search.match_count} {search.match_count === 1 ? "find" : "finds"}</Badge>
            {search.last_checked_at && (
              <Badge variant="outline" className="text-zinc-400">
                Last scanned {timeAgo(search.last_checked_at)}
              </Badge>
            )}
            {search.last_run_message && (
              <Badge variant="outline" className="text-zinc-400">
                {search.last_run_message}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tabs: Discoveries / Alerts / Activity */}
      <Tabs defaultValue="matches">
        <TabsList>
          <TabsTrigger value="matches">Discoveries ({matches.length})</TabsTrigger>
          <TabsTrigger value="alerts">Alerts ({alerts.length})</TabsTrigger>
          <TabsTrigger value="activity">Activity ({activity.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="matches" className="mt-4">
          {matches.length === 0 ? (
            <Card className="border-zinc-200/80 shadow-sm">
              <CardContent className="flex flex-col items-center py-12">
                <Sparkles className="mb-3 h-8 w-8 text-zinc-300" />
                <p className="text-sm text-zinc-500">Nothing found yet</p>
                <p className="text-xs text-zinc-400">Run this search to discover products</p>
                <Button variant="outline" size="sm" className="mt-4" onClick={handleRun}>
                  <RefreshCw className="mr-2 h-4 w-4" />Scan now
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {matches.map((product) => (
                <Card key={product.id} className="overflow-hidden border-zinc-200/80 shadow-sm transition-shadow hover:shadow-md">
                  <div className="aspect-square bg-zinc-100">
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
                  </div>
                  <CardContent className="p-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-zinc-900">
                          {product.title}
                        </p>
                        <p className="text-xs text-zinc-500">{product.brand} · {product.source}</p>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center gap-2">
                      {product.price && (
                        <span className="text-sm font-semibold text-zinc-900">
                          ${product.price.toFixed(0)}
                        </span>
                      )}
                      {product.original_price && (
                        <span className="text-xs text-zinc-400 line-through">
                          ${product.original_price.toFixed(0)}
                        </span>
                      )}
                      {product.is_on_sale && (
                        <Badge className="bg-green-50 text-green-700 text-xs">On Sale</Badge>
                      )}
                    </div>
                    {product.relevance_score !== undefined && product.relevance_score !== null && (
                      <div className="mt-2">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 flex-1 rounded-full bg-zinc-100">
                            <div
                              className="h-1.5 rounded-full bg-zinc-900"
                              style={{ width: `${Math.min(product.relevance_score, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs text-zinc-500">
                            {product.relevance_score.toFixed(0)}% match
                          </span>
                        </div>
                        {product.match_reason && (
                          <p className="mt-1 text-xs text-zinc-400">{product.match_reason}</p>
                        )}
                      </div>
                    )}
                    <div className="mt-3 flex gap-1">
                      {product.product_url && (
                        <a href={product.product_url} target="_blank" rel="noopener noreferrer">
                          <Button variant="outline" size="sm" className="gap-1 text-xs">
                            <ExternalLink className="h-3 w-3" />View listing
                          </Button>
                        </a>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleItemAction(product.id, "liked")}
                        className="text-xs"
                        title="Save this item"
                      >
                        <Heart className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleItemAction(product.id, "dismissed")}
                        className="text-xs"
                        title="Not interested"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="alerts" className="mt-4">
          {alerts.length === 0 ? (
            <Card className="border-zinc-200/80 shadow-sm">
              <CardContent className="flex flex-col items-center py-12">
                <Bell className="mb-3 h-8 w-8 text-zinc-300" />
                <p className="text-sm text-zinc-500">No alerts yet</p>
                <p className="text-xs text-zinc-400">Alerts appear when Scout finds something notable</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-2">
              {alerts.map((alert) => {
                const Icon = ALERT_ICONS[alert.alert_type] || Bell;
                return (
                  <Card key={alert.id} className="border-zinc-200/80 shadow-sm">
                    <CardContent className="flex items-start gap-3 p-3">
                      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-zinc-100">
                        <Icon className="h-4 w-4 text-zinc-600" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-zinc-900">{alert.title}</p>
                        {alert.message && (
                          <p className="mt-0.5 text-xs text-zinc-500">{alert.message}</p>
                        )}
                        <p className="mt-1 text-xs text-zinc-400">
                          {timeAgo(alert.created_at)}
                        </p>
                      </div>
                      {alert.product?.product_url && (
                        <a href={alert.product.product_url} target="_blank" rel="noopener noreferrer">
                          <Button variant="ghost" size="sm">
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        </a>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </TabsContent>

        <TabsContent value="activity" className="mt-4">
          {activity.length === 0 ? (
            <Card className="border-zinc-200/80 shadow-sm">
              <CardContent className="flex flex-col items-center py-12">
                <Activity className="mb-3 h-8 w-8 text-zinc-300" />
                <p className="text-sm text-zinc-500">No activity yet</p>
                <p className="text-xs text-zinc-400">Run this search to see its history</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-2">
              {activity.map((run) => (
                <Card key={run.id} className="border-zinc-200/80 shadow-sm">
                  <CardContent className="flex items-center gap-3 p-3">
                    {run.status === "success" ? (
                      <CheckCircle2 className="h-5 w-5 shrink-0 text-green-500" />
                    ) : (
                      <AlertCircle className="h-5 w-5 shrink-0 text-amber-500" />
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-zinc-900">
                        {run.message || (run.status === "success" ? "Scan completed" : "Scan encountered an issue")}
                      </p>
                      <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
                        <span>{timeAgo(run.created_at)}</span>
                        <span className="text-zinc-300">·</span>
                        <span>{run.items_found} items scanned</span>
                        {run.duration_ms !== null && (
                          <>
                            <span className="text-zinc-300">·</span>
                            <span>{run.duration_ms < 1000 ? `${run.duration_ms}ms` : `${(run.duration_ms / 1000).toFixed(1)}s`}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex shrink-0 gap-1.5">
                      {run.new_matches > 0 && (
                        <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-xs">
                          {run.new_matches} new
                        </Badge>
                      )}
                      {run.price_drops > 0 && (
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 text-xs">
                          {run.price_drops} price drop{run.price_drops > 1 ? "s" : ""}
                        </Badge>
                      )}
                      {run.sales > 0 && (
                        <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200 text-xs">
                          {run.sales} sale{run.sales > 1 ? "s" : ""}
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
