const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken(): string | null {
  return localStorage.getItem("scout_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  // Auth
  register: (data: { email: string; password: string; name?: string }) =>
    request("/api/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request("/api/auth/login", { method: "POST", body: JSON.stringify(data) }),
  getMe: () => request("/api/auth/me"),
  updateMe: (data: Record<string, unknown>) =>
    request("/api/auth/me", { method: "PUT", body: JSON.stringify(data) }),

  // Searches
  getSearches: (status?: string) =>
    request(`/api/searches${status ? `?status=${status}` : ""}`),
  createSearch: (data: Record<string, unknown>) =>
    request("/api/searches", { method: "POST", body: JSON.stringify(data) }),
  getSearch: (id: number) => request(`/api/searches/${id}`),
  updateSearch: (id: number, data: Record<string, unknown>) =>
    request(`/api/searches/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteSearch: (id: number) =>
    request(`/api/searches/${id}`, { method: "DELETE" }),
  duplicateSearch: (id: number) =>
    request(`/api/searches/${id}/duplicate`, { method: "POST" }),
  runSearch: (id: number) =>
    request(`/api/searches/${id}/run`, { method: "POST" }),
  getSearchMatches: (id: number) => request(`/api/searches/${id}/matches`),
  getSearchAlerts: (id: number) => request(`/api/searches/${id}/alerts`),
  getSearchPriceHistory: (id: number) =>
    request(`/api/searches/${id}/price-history`),
  getSearchActivity: (id: number) =>
    request(`/api/searches/${id}/activity`),

  // Dashboard
  getDashboard: () => request("/api/dashboard"),

  // Alerts
  getAlerts: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return request(`/api/alerts${qs}`);
  },
  updateAlert: (id: number, data: Record<string, unknown>) =>
    request(`/api/alerts/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  markAllRead: () =>
    request("/api/alerts/mark-all-read", { method: "POST" }),

  // Products
  getProducts: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return request(`/api/products${qs}`);
  },
  getProduct: (id: number) => request(`/api/products/${id}`),
  getProductPriceHistory: (id: number) =>
    request(`/api/products/${id}/price-history`),

  // Item Actions
  createItemAction: (data: { product_id: number; action: string }) =>
    request("/api/item-actions", { method: "POST", body: JSON.stringify(data) }),
  getItemActions: (action?: string) =>
    request(`/api/item-actions${action ? `?action=${action}` : ""}`),

  // Activity
  getActivity: () => request("/api/activity"),

  // Jobs
  runAllSearches: () =>
    request("/api/jobs/run-all", { method: "POST" }),
  runDueSearches: () =>
    request("/api/jobs/run-searches", { method: "POST" }),
};
