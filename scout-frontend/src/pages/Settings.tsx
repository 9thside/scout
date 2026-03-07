import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { DashboardStats } from "@/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Save, Phone, Bell, User, Shield, Activity, Search, Sparkles, TrendingDown } from "lucide-react";

export default function Settings() {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [smsEnabled, setSmsEnabled] = useState(user?.sms_enabled || false);
  const [whatsappEnabled, setWhatsappEnabled] = useState(user?.whatsapp_enabled || false);
  const [defaultFrequency, setDefaultFrequency] = useState("daily");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    api.getDashboard().then((s) => setStats(s as DashboardStats)).catch(console.error);
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await updateUser({
        name: name || null,
        phone: phone || null,
        sms_enabled: smsEnabled,
        whatsapp_enabled: whatsappEnabled,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">Settings</h1>
        <p className="text-sm text-zinc-500">Manage your account, notifications, and preferences</p>
      </div>

      {/* Profile */}
      <Card className="border-zinc-200/80 shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-zinc-500" />
            <CardTitle className="text-sm font-medium">Your profile</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" value={user?.email || ""} disabled className="bg-zinc-50" />
            <p className="text-xs text-zinc-400">Your login email (cannot be changed)</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="name">Display name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
            />
          </div>
        </CardContent>
      </Card>

      {/* Phone & Notifications */}
      <Card className="border-zinc-200/80 shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Phone className="h-4 w-4 text-zinc-500" />
            <CardTitle className="text-sm font-medium">Phone & notifications</CardTitle>
          </div>
          <CardDescription className="text-xs">
            Set up your phone to receive alerts when Scout finds something
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="phone">Phone number</Label>
            <Input
              id="phone"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1 (555) 000-0000"
              type="tel"
            />
            <p className="text-xs text-zinc-400">
              Include country code (e.g., +1 for US). Required for SMS alerts.
            </p>
          </div>
          <Separator />
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50">
                  <Bell className="h-4 w-4 text-blue-600" />
                </div>
                <div>
                  <Label>Text messages (SMS)</Label>
                  <p className="text-xs text-zinc-400">
                    Get notified by text when Scout finds a match
                  </p>
                </div>
              </div>
              <Switch checked={smsEnabled} onCheckedChange={setSmsEnabled} />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-green-50">
                  <Phone className="h-4 w-4 text-green-600" />
                </div>
                <div>
                  <Label>WhatsApp</Label>
                  <p className="text-xs text-zinc-400">
                    Get alerts on WhatsApp (coming soon)
                  </p>
                </div>
              </div>
              <Switch checked={whatsappEnabled} onCheckedChange={setWhatsappEnabled} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Default Preferences */}
      <Card className="border-zinc-200/80 shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Search className="h-4 w-4 text-zinc-500" />
            <CardTitle className="text-sm font-medium">Default search preferences</CardTitle>
          </div>
          <CardDescription className="text-xs">
            These defaults apply to new searches you create
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Default scan frequency</Label>
            <Select value={defaultFrequency} onValueChange={setDefaultFrequency}>
              <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="1h">Every hour</SelectItem>
                <SelectItem value="6h">Every 6 hours</SelectItem>
                <SelectItem value="daily">Once a day</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-zinc-400">
              How often Scout should check for new items by default
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Activity Summary */}
      {stats && (
        <Card className="border-zinc-200/80 shadow-sm">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-zinc-500" />
              <CardTitle className="text-sm font-medium">Account overview</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="rounded-xl bg-zinc-50 p-3 text-center">
                <Search className="mx-auto mb-1 h-4 w-4 text-zinc-400" />
                <p className="text-lg font-semibold text-zinc-900">{stats.total_active_searches}</p>
                <p className="text-xs text-zinc-500">Active searches</p>
              </div>
              <div className="rounded-xl bg-blue-50/50 p-3 text-center">
                <Bell className="mx-auto mb-1 h-4 w-4 text-blue-500" />
                <p className="text-lg font-semibold text-zinc-900">{stats.total_alerts_this_week}</p>
                <p className="text-xs text-zinc-500">Alerts this week</p>
              </div>
              <div className="rounded-xl bg-orange-50/50 p-3 text-center">
                <Sparkles className="mx-auto mb-1 h-4 w-4 text-orange-500" />
                <p className="text-lg font-semibold text-zinc-900">{stats.new_items_count}</p>
                <p className="text-xs text-zinc-500">New finds</p>
              </div>
              <div className="rounded-xl bg-green-50/50 p-3 text-center">
                <TrendingDown className="mx-auto mb-1 h-4 w-4 text-green-500" />
                <p className="text-lg font-semibold text-zinc-900">{stats.price_drops_count}</p>
                <p className="text-xs text-zinc-500">Price drops</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Twilio Setup Info */}
      <Card className="border-zinc-200/80 shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-zinc-500" />
            <CardTitle className="text-sm font-medium">Notification service setup</CardTitle>
          </div>
          <CardDescription className="text-xs">
            Connect Twilio to send real SMS and WhatsApp alerts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-xl bg-zinc-50 p-4">
            <p className="text-sm text-zinc-600">
              Scout uses Twilio to deliver SMS and WhatsApp notifications. To enable real alerts:
            </p>
            <ol className="mt-3 space-y-1.5 text-xs text-zinc-500">
              <li className="flex gap-2"><span className="font-medium text-zinc-600">1.</span> Create a free Twilio account at twilio.com</li>
              <li className="flex gap-2"><span className="font-medium text-zinc-600">2.</span> Get your Account SID, Auth Token, and a phone number</li>
              <li className="flex gap-2"><span className="font-medium text-zinc-600">3.</span> Set these environment variables on the backend:</li>
            </ol>
            <div className="mt-3 space-y-1.5">
              <code className="block rounded-lg bg-zinc-100 px-3 py-1.5 text-xs font-mono text-zinc-600">
                TWILIO_ACCOUNT_SID=your_account_sid
              </code>
              <code className="block rounded-lg bg-zinc-100 px-3 py-1.5 text-xs font-mono text-zinc-600">
                TWILIO_AUTH_TOKEN=your_auth_token
              </code>
              <code className="block rounded-lg bg-zinc-100 px-3 py-1.5 text-xs font-mono text-zinc-600">
                TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
              </code>
            </div>
            <p className="mt-3 text-xs text-zinc-400">
              Without Twilio credentials, notifications are logged to the console instead of being sent.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Save */}
      <div className="flex items-center justify-end gap-3 pb-8">
        {saved && (
          <span className="text-sm text-green-600 animate-in fade-in">Saved successfully</span>
        )}
        <Button onClick={handleSave} disabled={saving}>
          <Save className="mr-2 h-4 w-4" />
          {saving ? "Saving..." : "Save settings"}
        </Button>
      </div>
    </div>
  );
}
