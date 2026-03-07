import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { SavedSearch, STYLE_PROFILES, BUDGET_PREFERENCES, SEARCH_FREQUENCIES } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Plus,
  MoreVertical,
  Pause,
  Play,
  Copy,
  Archive,
  Trash2,
  Clock,
  RefreshCw,
  Search,
  ShoppingBag,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

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

export default function Searches() {
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  const loadSearches = async () => {
    try {
      const data = (await api.getSearches()) as SavedSearch[];
      setSearches(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSearches();
  }, []);

  const handleAction = async (
    searchId: number,
    action: "pause" | "resume" | "duplicate" | "archive" | "delete"
  ) => {
    try {
      switch (action) {
        case "pause":
          await api.updateSearch(searchId, { status: "paused" });
          break;
        case "resume":
          await api.updateSearch(searchId, { status: "active" });
          break;
        case "duplicate":
          await api.duplicateSearch(searchId);
          break;
        case "archive":
          await api.updateSearch(searchId, { status: "archived" });
          break;
        case "delete":
          await api.deleteSearch(searchId);
          break;
      }
      await loadSearches();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunSearch = async (searchId: number) => {
    try {
      await api.runSearch(searchId);
      await loadSearches();
    } catch (err) {
      console.error(err);
    }
  };

  const filteredSearches = searches.filter((s) => {
    if (filter === "all") return true;
    return s.status === filter;
  });

  const getStyleLabel = (value: string | null) =>
    STYLE_PROFILES.find((s) => s.value === value)?.label || value;
  const getBudgetLabel = (value: string | null) =>
    BUDGET_PREFERENCES.find((b) => b.value === value)?.label || value;
  const getFreqLabel = (value: string) =>
    SEARCH_FREQUENCIES.find((f) => f.value === value)?.label || value;

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-28 rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            My Searches
          </h1>
          <p className="text-sm text-zinc-500">
            {searches.length === 0
              ? "Tell Scout what to look for"
              : `${searches.filter(s => s.status === "active").length} active, monitoring the market for you`}
          </p>
        </div>
        <Link to="/searches/new">
          <Button size="sm">
            <Plus className="mr-2 h-4 w-4" />
            New search
          </Button>
        </Link>
      </div>

      {/* Filter Tabs */}
      <Tabs value={filter} onValueChange={setFilter}>
        <TabsList>
          <TabsTrigger value="all">All ({searches.length})</TabsTrigger>
          <TabsTrigger value="active">
            Active ({searches.filter((s) => s.status === "active").length})
          </TabsTrigger>
          <TabsTrigger value="paused">
            Paused ({searches.filter((s) => s.status === "paused").length})
          </TabsTrigger>
          <TabsTrigger value="archived">
            Archived ({searches.filter((s) => s.status === "archived").length})
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Search List */}
      {filteredSearches.length === 0 ? (
        <Card className="border-zinc-200/80 shadow-sm">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-zinc-100">
              <Search className="h-6 w-6 text-zinc-400" />
            </div>
            <p className="text-base font-medium text-zinc-900">
              {filter === "all" ? "Tell Scout what to look for" : `No ${filter} searches`}
            </p>
            <p className="mt-1.5 max-w-sm text-center text-sm text-zinc-500">
              {filter === "all"
                ? "Describe a product you want and Scout will continuously search the market for you"
                : `You don't have any ${filter} searches right now`}
            </p>
            {filter === "all" && (
              <Link to="/searches/new" className="mt-4">
                <Button size="sm" className="gap-1.5">
                  <Plus className="h-3.5 w-3.5" />
                  Create your first search
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filteredSearches.map((search) => (
            <Card key={search.id} className="border-zinc-200/80 shadow-sm transition-shadow hover:shadow-md">
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <Link to={`/searches/${search.id}`} className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <ShoppingBag className="h-4 w-4 shrink-0 text-zinc-400" />
                      <h3 className="truncate text-sm font-medium text-zinc-900">
                        {search.name}
                      </h3>
                      <Badge
                        variant={
                          search.status === "active"
                            ? "default"
                            : search.status === "paused"
                            ? "secondary"
                            : "outline"
                        }
                        className="shrink-0 text-xs"
                      >
                        {search.status === "active" ? "Monitoring" : search.status === "paused" ? "Paused" : "Archived"}
                      </Badge>
                      {search.last_run_status && (
                        search.last_run_status === "success" ? (
                          <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-500" />
                        ) : (
                          <AlertCircle className="h-3.5 w-3.5 shrink-0 text-amber-500" />
                        )
                      )}
                    </div>
                    <p className="mt-1 truncate text-xs text-zinc-500">{search.query}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      {search.category && (
                        <Badge variant="outline" className="text-xs">{search.category}</Badge>
                      )}
                      {search.style_profile && (
                        <Badge variant="outline" className="text-xs">
                          {getStyleLabel(search.style_profile)}
                        </Badge>
                      )}
                      {search.budget_preference && (
                        <Badge variant="outline" className="text-xs">
                          {getBudgetLabel(search.budget_preference)}
                        </Badge>
                      )}
                      {(search.min_price || search.max_price) && (
                        <Badge variant="outline" className="text-xs">
                          {search.min_price ? `$${search.min_price}` : "$0"} -{" "}
                          {search.max_price ? `$${search.max_price}` : "any"}
                        </Badge>
                      )}
                    </div>
                  </Link>

                  <div className="flex shrink-0 items-center gap-2">
                    <div className="hidden text-right sm:block">
                      <div className="flex items-center gap-1 text-xs text-zinc-500">
                        <Clock className="h-3 w-3" />
                        {getFreqLabel(search.search_frequency)}
                      </div>
                      <p className="mt-0.5 text-xs font-medium text-zinc-700">
                        {search.match_count} {search.match_count === 1 ? "find" : "finds"}
                      </p>
                      {search.last_checked_at && (
                        <p className="text-xs text-zinc-400">
                          Scanned {timeAgo(search.last_checked_at)}
                        </p>
                      )}
                      {search.last_run_message && (
                        <p className="mt-0.5 max-w-[180px] truncate text-xs text-zinc-400">
                          {search.last_run_message}
                        </p>
                      )}
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.preventDefault();
                        handleRunSearch(search.id);
                      }}
                      title="Scan now"
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>

                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem asChild>
                          <Link to={`/searches/${search.id}/edit`}>Edit search</Link>
                        </DropdownMenuItem>
                        {search.status === "active" ? (
                          <DropdownMenuItem onClick={() => handleAction(search.id, "pause")}>
                            <Pause className="mr-2 h-4 w-4" />
                            Pause monitoring
                          </DropdownMenuItem>
                        ) : (
                          <DropdownMenuItem onClick={() => handleAction(search.id, "resume")}>
                            <Play className="mr-2 h-4 w-4" />
                            Resume monitoring
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuItem onClick={() => handleAction(search.id, "duplicate")}>
                          <Copy className="mr-2 h-4 w-4" />
                          Duplicate
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleAction(search.id, "archive")}>
                          <Archive className="mr-2 h-4 w-4" />
                          Archive
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-red-600"
                          onClick={() => handleAction(search.id, "delete")}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
