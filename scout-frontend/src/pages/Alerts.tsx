import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Alert } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Bell,
  TrendingDown,
  Sparkles,
  Tag,
  RotateCcw,
  ExternalLink,
  Check,
  X,
  CheckCheck,
  ShoppingCart,
} from "lucide-react";

const ALERT_TYPE_CONFIG: Record<string, { icon: typeof Bell; color: string; bg: string; label: string; accent: string }> = {
  new_match: { icon: Sparkles, color: "text-blue-700", bg: "bg-blue-50 border-blue-200", label: "New Find", accent: "border-l-blue-500" },
  price_drop: { icon: TrendingDown, color: "text-emerald-700", bg: "bg-emerald-50 border-emerald-200", label: "Price Drop", accent: "border-l-emerald-500" },
  sale: { icon: Tag, color: "text-amber-700", bg: "bg-amber-50 border-amber-200", label: "On Sale", accent: "border-l-amber-500" },
  restock: { icon: RotateCcw, color: "text-violet-700", bg: "bg-violet-50 border-violet-200", label: "Back in Stock", accent: "border-l-violet-500" },
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

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  const loadAlerts = async () => {
    try {
      const params: Record<string, string> = { limit: "100" };
      if (filter !== "all") params.alert_type = filter;
      const data = (await api.getAlerts(params)) as Alert[];
      setAlerts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [filter]);

  const handleDismiss = async (alertId: number) => {
    try {
      await api.updateAlert(alertId, { is_dismissed: true });
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkRead = async (alertId: number) => {
    try {
      await api.updateAlert(alertId, { is_read: true });
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, is_read: true } : a))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllRead();
      setAlerts((prev) => prev.map((a) => ({ ...a, is_read: true })));
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
    );
  }

  const unreadCount = alerts.filter((a) => !a.is_read).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">Alerts</h1>
          <p className="text-sm text-zinc-500">
            {unreadCount > 0 ? `${unreadCount} new alert${unreadCount !== 1 ? "s" : ""} to review` : "You're all caught up"}
          </p>
        </div>
        {unreadCount > 0 && (
          <Button variant="outline" size="sm" onClick={handleMarkAllRead}>
            <CheckCheck className="mr-2 h-4 w-4" />
            Mark all read
          </Button>
        )}
      </div>

      {/* Filter */}
      <Tabs value={filter} onValueChange={setFilter}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="new_match">New Finds</TabsTrigger>
          <TabsTrigger value="price_drop">Price Drops</TabsTrigger>
          <TabsTrigger value="sale">On Sale</TabsTrigger>
          <TabsTrigger value="restock">Back in Stock</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Alert List */}
      {alerts.length === 0 ? (
        <Card className="border-zinc-200/80 shadow-sm">
          <CardContent className="flex flex-col items-center py-20">
            <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-zinc-100">
              <Bell className="h-6 w-6 text-zinc-400" />
            </div>
            <p className="text-base font-medium text-zinc-900">You're all caught up</p>
            <p className="mt-1.5 max-w-sm text-center text-sm text-zinc-500">
              When Scout finds new items, price drops, sales, or restocks matching your searches, they'll appear here
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {alerts.map((alert) => {
            const config = ALERT_TYPE_CONFIG[alert.alert_type] || ALERT_TYPE_CONFIG.new_match;
            const Icon = config.icon;
            return (
              <Card
                key={alert.id}
                className={`border-l-4 border-zinc-200/80 shadow-sm transition-colors ${config.accent} ${
                  !alert.is_read ? "bg-zinc-50/80" : ""
                }`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    {/* Product Image */}
                    <div className="hidden h-16 w-16 shrink-0 overflow-hidden rounded-lg bg-zinc-100 sm:block">
                      {alert.product?.image_url ? (
                        <img
                          src={alert.product.image_url}
                          alt=""
                          className="h-full w-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = "none";
                          }}
                        />
                      ) : (
                        <div className="flex h-full items-center justify-center">
                          <ShoppingCart className="h-5 w-5 text-zinc-300" />
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className={`gap-1 ${config.bg} ${config.color}`}>
                          <Icon className="h-3 w-3" />
                          {config.label}
                        </Badge>
                        {alert.search_name && (
                          <span className="text-xs text-zinc-400">
                            from "{alert.search_name}"
                          </span>
                        )}
                        {!alert.is_read && (
                          <div className="h-2 w-2 rounded-full bg-blue-500" />
                        )}
                      </div>
                      <p className="mt-1 text-sm font-medium text-zinc-900">
                        {alert.title}
                      </p>
                      {alert.message && (
                        <p className="mt-0.5 text-xs text-zinc-500">{alert.message}</p>
                      )}
                      <div className="mt-2 flex items-center gap-3">
                        {alert.product?.price && (
                          <span className="text-sm font-semibold text-zinc-900">
                            ${alert.product.price.toFixed(0)}
                          </span>
                        )}
                        {alert.product?.original_price && (
                          <span className="text-xs text-zinc-400 line-through">
                            ${alert.product.original_price.toFixed(0)}
                          </span>
                        )}
                        {alert.product?.source && (
                          <span className="text-xs text-zinc-400">{alert.product.source}</span>
                        )}
                        <span className="text-xs text-zinc-400">
                          {timeAgo(alert.created_at)}
                        </span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex shrink-0 items-center gap-1">
                      {!alert.is_read && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleMarkRead(alert.id)}
                          title="Mark as read"
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                      )}
                      {alert.product?.product_url && (
                        <a
                          href={alert.product.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <Button variant="ghost" size="sm" title="View product">
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        </a>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDismiss(alert.id)}
                        title="Dismiss"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
