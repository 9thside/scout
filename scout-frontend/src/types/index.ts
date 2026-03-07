export interface User {
  id: number;
  email: string;
  name: string | null;
  phone: string | null;
  sms_enabled: boolean;
  whatsapp_enabled: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SavedSearch {
  id: number;
  user_id: number;
  name: string;
  query: string;
  category: string | null;
  style_profile: string | null;
  budget_preference: string | null;
  min_price: number | null;
  max_price: number | null;
  condition: string | null;
  preferred_brands: string[] | null;
  excluded_brands: string[] | null;
  clothing_size: string | null;
  shoe_size: string | null;
  color: string | null;
  material: string | null;
  dimensions: string | null;
  gender_fit: string | null;
  notify_sms: boolean;
  notify_whatsapp: boolean;
  notify_new_matches: boolean;
  notify_price_drops: boolean;
  notify_sales: boolean;
  notify_restocks: boolean;
  digest_frequency: string;
  search_frequency: string;
  status: string;
  last_checked_at: string | null;
  last_run_status: string | null;
  last_run_message: string | null;
  match_count: number;
  created_at: string;
  updated_at: string | null;
}

export interface Product {
  id: number;
  title: string;
  source: string | null;
  brand: string | null;
  category: string | null;
  price: number | null;
  original_price: number | null;
  discount_percent: number | null;
  currency: string;
  image_url: string | null;
  product_url: string | null;
  availability: string;
  condition: string;
  size: string | null;
  color: string | null;
  material: string | null;
  description: string | null;
  is_on_sale: boolean;
  first_seen_at: string | null;
  last_seen_at: string | null;
  relevance_score?: number | null;
  match_reason?: string | null;
  user_action?: string | null;
}

export interface Alert {
  id: number;
  user_id: number;
  search_id: number | null;
  product_id: number | null;
  alert_type: string;
  title: string;
  message: string | null;
  details: Record<string, unknown> | null;
  is_read: boolean;
  is_dismissed: boolean;
  created_at: string;
  product: Product | null;
  search_name: string | null;
}

export interface DashboardStats {
  total_active_searches: number;
  total_alerts_this_week: number;
  price_drops_count: number;
  new_items_count: number;
  saved_items_count: number;
}

export interface PriceHistory {
  id: number;
  product_id: number;
  price: number;
  original_price: number | null;
  recorded_at: string;
}

export interface SearchRunLog {
  id: number;
  search_id: number;
  user_id: number;
  status: string;
  items_found: number;
  new_matches: number;
  price_drops: number;
  sales: number;
  restocks: number;
  message: string | null;
  duration_ms: number | null;
  created_at: string;
  search_name: string | null;
}

export interface SavedSearchForm {
  name: string;
  query: string;
  category: string;
  style_profile: string;
  budget_preference: string;
  min_price: string;
  max_price: string;
  condition: string;
  preferred_brands: string;
  excluded_brands: string;
  clothing_size: string;
  shoe_size: string;
  color: string;
  material: string;
  dimensions: string;
  gender_fit: string;
  notify_sms: boolean;
  notify_whatsapp: boolean;
  notify_new_matches: boolean;
  notify_price_drops: boolean;
  notify_sales: boolean;
  notify_restocks: boolean;
  digest_frequency: string;
  search_frequency: string;
}

export const CATEGORIES = [
  "Outerwear",
  "Shoes",
  "Furniture",
  "Watches",
  "Bags",
  "Electronics",
  "Home Decor",
  "General",
] as const;

export const STYLE_PROFILES = [
  { value: "everyday", label: "Everyday" },
  { value: "trend-forward", label: "Trend-Forward" },
  { value: "niche", label: "Niche / Enthusiast" },
  { value: "premium-brand", label: "Premium Brand" },
  { value: "designer", label: "Designer / Luxury" },
  { value: "open", label: "Open to Anything" },
] as const;

export const BUDGET_PREFERENCES = [
  { value: "any", label: "Any Budget" },
  { value: "value", label: "Value" },
  { value: "mid-range", label: "Mid-Range" },
  { value: "premium", label: "Premium" },
  { value: "luxury", label: "Luxury" },
] as const;

export const CONDITIONS = [
  { value: "new_only", label: "New Only" },
  { value: "new_resale", label: "New + Resale" },
  { value: "resale_only", label: "Resale Only" },
] as const;

export const DIGEST_FREQUENCIES = [
  { value: "instant", label: "Instant" },
  { value: "daily", label: "Daily Summary" },
  { value: "weekly", label: "Weekly Summary" },
] as const;

export const SEARCH_FREQUENCIES = [
  { value: "1h", label: "Every Hour" },
  { value: "6h", label: "Every 6 Hours" },
  { value: "daily", label: "Once a Day" },
] as const;
