import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { SearchRunLog } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Activity as ActivityIcon,
  CheckCircle2,
  AlertCircle,
  Search,
} from "lucide-react";

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

export default function Activity() {
  const [logs, setLogs] = useState<SearchRunLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getActivity()
      .then((data) => setLogs(data as SearchRunLog[]))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-20 rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">Activity</h1>
        <p className="text-sm text-zinc-500">
          A log of every time Scout scanned your searches
        </p>
      </div>

      {/* Activity List */}
      {logs.length === 0 ? (
        <Card className="border-zinc-200/80 shadow-sm">
          <CardContent className="flex flex-col items-center py-16">
            <ActivityIcon className="mb-4 h-10 w-10 text-zinc-300" />
            <p className="text-sm font-medium text-zinc-900">No activity yet</p>
            <p className="mt-1 text-xs text-zinc-500">
              Run a search and its history will show up here
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {logs.map((run) => (
            <Card key={run.id} className="border-zinc-200/80 shadow-sm transition-shadow hover:shadow-md">
              <CardContent className="flex items-center gap-3 p-4">
                {run.status === "success" ? (
                  <CheckCircle2 className="h-5 w-5 shrink-0 text-green-500" />
                ) : (
                  <AlertCircle className="h-5 w-5 shrink-0 text-amber-500" />
                )}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <Search className="h-3.5 w-3.5 text-zinc-400" />
                    {run.search_name ? (
                      <Link
                        to={`/searches/${run.search_id}`}
                        className="text-sm font-medium text-zinc-900 hover:underline"
                      >
                        {run.search_name}
                      </Link>
                    ) : (
                      <span className="text-sm font-medium text-zinc-900">
                        Search #{run.search_id}
                      </span>
                    )}
                  </div>
                  <p className="mt-0.5 text-xs text-zinc-500">
                    {run.message || (run.status === "success" ? "Scan completed" : "Scan encountered an issue")}
                  </p>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-zinc-400">
                    <span>{timeAgo(run.created_at)}</span>
                    <span className="text-zinc-300">·</span>
                    <span>{run.items_found} items scanned</span>
                    {run.duration_ms !== null && (
                      <>
                        <span className="text-zinc-300">·</span>
                        <span>
                          {run.duration_ms < 1000
                            ? `${run.duration_ms}ms`
                            : `${(run.duration_ms / 1000).toFixed(1)}s`}
                        </span>
                      </>
                    )}
                  </div>
                </div>
                <div className="flex shrink-0 gap-1.5">
                  {run.new_matches > 0 && (
                    <Badge
                      variant="outline"
                      className="bg-blue-50 text-blue-700 border-blue-200 text-xs"
                    >
                      {run.new_matches} new
                    </Badge>
                  )}
                  {run.price_drops > 0 && (
                    <Badge
                      variant="outline"
                      className="bg-green-50 text-green-700 border-green-200 text-xs"
                    >
                      {run.price_drops} price drop{run.price_drops > 1 ? "s" : ""}
                    </Badge>
                  )}
                  {run.sales > 0 && (
                    <Badge
                      variant="outline"
                      className="bg-orange-50 text-orange-700 border-orange-200 text-xs"
                    >
                      {run.sales} sale{run.sales > 1 ? "s" : ""}
                    </Badge>
                  )}
                  {run.restocks > 0 && (
                    <Badge
                      variant="outline"
                      className="bg-purple-50 text-purple-700 border-purple-200 text-xs"
                    >
                      {run.restocks} restock{run.restocks > 1 ? "s" : ""}
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
