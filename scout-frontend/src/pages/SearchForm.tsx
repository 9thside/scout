import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "@/lib/api";
import {
  SavedSearch,
  SavedSearchForm,
  CATEGORIES,
  STYLE_PROFILES,
  BUDGET_PREFERENCES,
  CONDITIONS,
  DIGEST_FREQUENCIES,
  SEARCH_FREQUENCIES,
} from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowLeft, Save } from "lucide-react";

const DEFAULT_FORM: SavedSearchForm = {
  name: "",
  query: "",
  category: "",
  style_profile: "open",
  budget_preference: "any",
  min_price: "",
  max_price: "",
  condition: "new_only",
  preferred_brands: "",
  excluded_brands: "",
  clothing_size: "",
  shoe_size: "",
  color: "",
  material: "",
  dimensions: "",
  gender_fit: "",
  notify_sms: true,
  notify_whatsapp: false,
  notify_new_matches: true,
  notify_price_drops: true,
  notify_sales: true,
  notify_restocks: true,
  digest_frequency: "instant",
  search_frequency: "daily",
};

export default function SearchForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = Boolean(id);
  const [form, setForm] = useState<SavedSearchForm>(DEFAULT_FORM);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isEdit && id) {
      setLoading(true);
      api
        .getSearch(Number(id))
        .then((s) => {
          const search = s as SavedSearch;
          setForm({
            name: search.name,
            query: search.query,
            category: search.category || "",
            style_profile: search.style_profile || "open",
            budget_preference: search.budget_preference || "any",
            min_price: search.min_price?.toString() || "",
            max_price: search.max_price?.toString() || "",
            condition: search.condition || "new_only",
            preferred_brands: (search.preferred_brands || []).join(", "),
            excluded_brands: (search.excluded_brands || []).join(", "),
            clothing_size: search.clothing_size || "",
            shoe_size: search.shoe_size || "",
            color: search.color || "",
            material: search.material || "",
            dimensions: search.dimensions || "",
            gender_fit: search.gender_fit || "",
            notify_sms: search.notify_sms,
            notify_whatsapp: search.notify_whatsapp,
            notify_new_matches: search.notify_new_matches,
            notify_price_drops: search.notify_price_drops,
            notify_sales: search.notify_sales,
            notify_restocks: search.notify_restocks,
            digest_frequency: search.digest_frequency,
            search_frequency: search.search_frequency,
          });
        })
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [id, isEdit]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    const payload: Record<string, unknown> = {
      name: form.name,
      query: form.query,
      category: form.category || null,
      style_profile: form.style_profile || null,
      budget_preference: form.budget_preference || null,
      min_price: form.min_price ? parseFloat(form.min_price) : null,
      max_price: form.max_price ? parseFloat(form.max_price) : null,
      condition: form.condition,
      preferred_brands: form.preferred_brands
        ? form.preferred_brands.split(",").map((b) => b.trim()).filter(Boolean)
        : null,
      excluded_brands: form.excluded_brands
        ? form.excluded_brands.split(",").map((b) => b.trim()).filter(Boolean)
        : null,
      clothing_size: form.clothing_size || null,
      shoe_size: form.shoe_size || null,
      color: form.color || null,
      material: form.material || null,
      dimensions: form.dimensions || null,
      gender_fit: form.gender_fit || null,
      notify_sms: form.notify_sms,
      notify_whatsapp: form.notify_whatsapp,
      notify_new_matches: form.notify_new_matches,
      notify_price_drops: form.notify_price_drops,
      notify_sales: form.notify_sales,
      notify_restocks: form.notify_restocks,
      digest_frequency: form.digest_frequency,
      search_frequency: form.search_frequency,
    };

    try {
      if (isEdit && id) {
        await api.updateSearch(Number(id), payload);
        navigate(`/searches/${id}`);
      } else {
        const result = (await api.createSearch(payload)) as SavedSearch;
        navigate(`/searches/${result.id}`);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center py-16 text-zinc-500">Loading...</div>;
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            {isEdit ? "Edit search" : "Create a new search"}
          </h1>
          <p className="text-sm text-zinc-500">
            {isEdit
              ? "Fine-tune what Scout looks for"
              : "Tell Scout what you want and it will keep searching for you"}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <Card className="border-zinc-200/80 shadow-sm">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-zinc-700">What are you looking for?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Give it a name</Label>
              <Input
                id="name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g., Winter Jacket, Loafers, Coffee Table"
                required
              />
              <p className="text-xs text-zinc-400">A short label so you can recognize this search later</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="query">Describe what you want</Label>
              <Textarea
                id="query"
                value={form.query}
                onChange={(e) => setForm({ ...form, query: e.target.value })}
                placeholder="e.g., black shiny puffer faux fur trim, relaxed fit selvedge denim"
                required
                rows={2}
              />
              <p className="text-xs text-zinc-400">
                Use natural language — be as specific as you like
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Category</Label>
                <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v })}>
                  <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map((c) => (
                      <SelectItem key={c} value={c}>{c}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Style Profile</Label>
                <Select value={form.style_profile} onValueChange={(v) => setForm({ ...form, style_profile: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {STYLE_PROFILES.map((s) => (
                      <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Budget & Condition */}
        <Card className="border-zinc-200/80 shadow-sm">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-zinc-700">Budget & condition</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <Label>Budget Preference</Label>
                <Select value={form.budget_preference} onValueChange={(v) => setForm({ ...form, budget_preference: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {BUDGET_PREFERENCES.map((b) => (
                      <SelectItem key={b.value} value={b.value}>{b.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="min_price">Min Price</Label>
                <Input
                  id="min_price"
                  type="number"
                  value={form.min_price}
                  onChange={(e) => setForm({ ...form, min_price: e.target.value })}
                  placeholder="$0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_price">Max Price</Label>
                <Input
                  id="max_price"
                  type="number"
                  value={form.max_price}
                  onChange={(e) => setForm({ ...form, max_price: e.target.value })}
                  placeholder="No limit"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Condition</Label>
              <Select value={form.condition} onValueChange={(v) => setForm({ ...form, condition: v })}>
                <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {CONDITIONS.map((c) => (
                    <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Brands */}
        <Card className="border-zinc-200/80 shadow-sm">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-zinc-700">Brand preferences</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="preferred_brands">Brands you love</Label>
              <Input
                id="preferred_brands"
                value={form.preferred_brands}
                onChange={(e) => setForm({ ...form, preferred_brands: e.target.value })}
                placeholder="e.g., Nike, Adidas, Common Projects"
              />
              <p className="text-xs text-zinc-400">Comma-separated list</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="excluded_brands">Brands to skip</Label>
              <Input
                id="excluded_brands"
                value={form.excluded_brands}
                onChange={(e) => setForm({ ...form, excluded_brands: e.target.value })}
                placeholder="e.g., Shein, Fashion Nova"
              />
              <p className="text-xs text-zinc-400">Comma-separated list</p>
            </div>
          </CardContent>
        </Card>

        {/* Size & Variants */}
        <Card className="border-zinc-200/80 shadow-sm">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-zinc-700">Size & details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="clothing_size">Clothing Size</Label>
                <Input
                  id="clothing_size"
                  value={form.clothing_size}
                  onChange={(e) => setForm({ ...form, clothing_size: e.target.value })}
                  placeholder="e.g., M, L, XL"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="shoe_size">Shoe Size</Label>
                <Input
                  id="shoe_size"
                  value={form.shoe_size}
                  onChange={(e) => setForm({ ...form, shoe_size: e.target.value })}
                  placeholder="e.g., 10, 10.5"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gender_fit">Gender / Fit</Label>
                <Input
                  id="gender_fit"
                  value={form.gender_fit}
                  onChange={(e) => setForm({ ...form, gender_fit: e.target.value })}
                  placeholder="e.g., Men's, Unisex"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="color">Color</Label>
                <Input
                  id="color"
                  value={form.color}
                  onChange={(e) => setForm({ ...form, color: e.target.value })}
                  placeholder="e.g., Black, Navy"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="material">Material</Label>
                <Input
                  id="material"
                  value={form.material}
                  onChange={(e) => setForm({ ...form, material: e.target.value })}
                  placeholder="e.g., Leather, Denim"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dimensions">Dimensions</Label>
                <Input
                  id="dimensions"
                  value={form.dimensions}
                  onChange={(e) => setForm({ ...form, dimensions: e.target.value })}
                  placeholder="e.g., 48x24 inches"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card className="border-zinc-200/80 shadow-sm">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-zinc-700">How should Scout notify you?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Text messages (SMS)</Label>
                <p className="text-xs text-zinc-400">Get alerts sent to your phone</p>
              </div>
              <Switch checked={form.notify_sms} onCheckedChange={(v) => setForm({ ...form, notify_sms: v })} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>WhatsApp</Label>
                <p className="text-xs text-zinc-400">Get alerts on WhatsApp (coming soon)</p>
              </div>
              <Switch checked={form.notify_whatsapp} onCheckedChange={(v) => setForm({ ...form, notify_whatsapp: v })} />
            </div>
            <Separator />
            <div className="space-y-3">
              <Label className="text-xs text-zinc-500 uppercase tracking-wider">What to alert you about</Label>
              <div className="flex items-center justify-between">
                <Label className="font-normal">New discoveries</Label>
                <Switch checked={form.notify_new_matches} onCheckedChange={(v) => setForm({ ...form, notify_new_matches: v })} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="font-normal">Price drops</Label>
                <Switch checked={form.notify_price_drops} onCheckedChange={(v) => setForm({ ...form, notify_price_drops: v })} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="font-normal">Items going on sale</Label>
                <Switch checked={form.notify_sales} onCheckedChange={(v) => setForm({ ...form, notify_sales: v })} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="font-normal">Back in stock</Label>
                <Switch checked={form.notify_restocks} onCheckedChange={(v) => setForm({ ...form, notify_restocks: v })} />
              </div>
            </div>
            <Separator />
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>How often to notify</Label>
                <Select value={form.digest_frequency} onValueChange={(v) => setForm({ ...form, digest_frequency: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {DIGEST_FREQUENCIES.map((d) => (
                      <SelectItem key={d.value} value={d.value}>{d.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>How often to scan</Label>
                <Select value={form.search_frequency} onValueChange={(v) => setForm({ ...form, search_frequency: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {SEARCH_FREQUENCIES.map((f) => (
                      <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Submit */}
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Cancel
          </Button>
          <Button type="submit" disabled={saving}>
            <Save className="mr-2 h-4 w-4" />
            {saving ? "Saving..." : isEdit ? "Save changes" : "Start searching"}
          </Button>
        </div>
      </form>
    </div>
  );
}
