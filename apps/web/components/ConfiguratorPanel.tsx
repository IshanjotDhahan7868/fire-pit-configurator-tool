"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useConfigStore } from "@/lib/store";
import { ConfiguratorScene } from "./ConfiguratorScene";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const FIELD_OPTIONS: { field: "shape" | "size_preset" | "material" | "finish" | "fuel_type" | "burner" | "media" | "ignition"; options: string[] }[] = [
  { field: "shape", options: ["round", "square", "rectangular"] },
  { field: "size_preset", options: ["small", "medium", "large", "xl"] },
  { field: "material", options: ["steel", "corten", "concrete", "stone"] },
  { field: "finish", options: ["matte-black", "rust", "charcoal", "sandstone"] },
  { field: "fuel_type", options: ["wood", "propane", "natural_gas"] },
  { field: "burner", options: ["none", "ring", "linear", "h-burner"] },
  { field: "media", options: ["lava_rock", "fire_glass"] },
  { field: "ignition", options: ["manual", "push_button", "electronic"] }
];

export function ConfiguratorPanel({ tenantSlug, productId }: { tenantSlug: string; productId: number }) {
  const { config, setField, setConfig } = useConfigStore();
  const [pricing, setPricing] = useState<any>(null);
  const [savedId, setSavedId] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [copied, setCopied] = useState(false);
  const [quoteForm, setQuoteForm] = useState({ name: "", email: "", phone: "", message: "" });

  const shareUrl = useMemo(() => {
    if (!savedId) return "";
    const origin = typeof window === "undefined" ? "" : window.location.origin;
    return `${origin}/t/${tenantSlug}/configurator?config=${savedId}`;
  }, [savedId, tenantSlug]);

  useEffect(() => {
    const run = async () => {
      setLoadingPrice(true);
      const res = await fetch(`${API}/public/pricing`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tenant_slug: tenantSlug, product_id: productId, config })
      });
      setLoadingPrice(false);
      if (res.ok) setPricing(await res.json());
    };
    run();
  }, [config, tenantSlug, productId]);

  useEffect(() => {
    const configId = new URLSearchParams(window.location.search).get("config");
    if (!configId) return;
    const run = async () => {
      setLoading(true);
      const res = await fetch(`${API}/public/configurations/${configId}`);
      setLoading(false);
      if (!res.ok) return setStatus("Unable to load shared configuration.");
      const data = await res.json();
      setConfig(data.config);
      setPricing(data.pricing_snapshot);
      setSavedId(data.public_id);
      setStatus("Shared configuration loaded.");
    };
    run();
  }, [setConfig]);

  async function saveConfig() {
    setLoading(true);
    const res = await fetch(`${API}/public/configurations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_slug: tenantSlug, product_id: productId, config })
    });
    const data = await res.json();
    setLoading(false);
    if (!res.ok) return setStatus(data.detail || "Failed to save.");
    setSavedId(data.public_id);
    setPricing(data.pricing_snapshot);
    window.history.replaceState({}, "", `?config=${data.public_id}`);
    setStatus("Configuration saved.");
  }

  async function submitQuote(e: FormEvent) {
    e.preventDefault();
    if (!savedId) return setStatus("Save your configuration first.");
    setLoading(true);
    const res = await fetch(`${API}/public/quote-request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ configuration_public_id: savedId, ...quoteForm })
    });
    const data = await res.json();
    setLoading(false);
    if (!res.ok) return setStatus(data.detail || "Quote request failed.");
    setStatus(`Quote #${data.quote_id} requested successfully.`);
  }

  function toggleAccessory(accessory: string) {
    const active = new Set(config.accessories);
    if (active.has(accessory)) active.delete(accessory); else active.add(accessory);
    setField("accessories", Array.from(active));
  }

  return (
    <div className="grid gap-4 lg:grid-cols-5">
      <div className="lg:col-span-3"><ConfiguratorScene config={config} /></div>
      <div className="lg:col-span-2 space-y-4">
        <div className="card p-4 space-y-3">
          <h3 className="text-lg font-semibold">Customize your fire pit</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {FIELD_OPTIONS.map(({ field, options }) => (
              <label key={field} className="text-xs text-slate-600">{field.replaceAll("_", " ")}
                <select className="mt-1 w-full border rounded p-2 capitalize text-sm" value={config[field]} onChange={(e) => setField(field, e.target.value)}>
                  {options.map((v) => <option key={v} value={v}>{v.replaceAll("_", " ")}</option>)}
                </select>
              </label>
            ))}
          </div>

          <div>
            <p className="text-sm font-medium mb-1">Accessories</p>
            <div className="flex flex-wrap gap-2">
              {["cover", "wind_guard", "lid", "spark_screen", "grate"].map((a) => (
                <button key={a} onClick={() => toggleAccessory(a)} className={`px-2 py-1 rounded border text-sm ${config.accessories.includes(a) ? "bg-orange-600 text-white" : "bg-white"}`}>{a.replace("_", " ")}</button>
              ))}
            </div>
          </div>

          <button className="rounded bg-orange-600 text-white px-3 py-2" onClick={saveConfig} disabled={loading}>{loading ? "Saving..." : "Save Configuration"}</button>
          {savedId && (
            <div className="rounded border p-2 text-sm">
              <p className="font-medium">Share link</p>
              <p className="truncate text-slate-600">{shareUrl}</p>
              <button className="mt-1 text-xs underline" onClick={() => { navigator.clipboard.writeText(shareUrl); setCopied(true); }}>{copied ? "Copied" : "Copy link"}</button>
            </div>
          )}
        </div>

        <div className="card p-4 space-y-2">
          <div className="flex justify-between items-center"><h4 className="font-semibold">Live pricing</h4>{loadingPrice && <span className="text-xs text-slate-500">Updating…</span>}</div>
          <p className="text-2xl font-bold">${(pricing?.total ?? 0).toLocaleString()}</p>
          <ul className="text-sm space-y-1 max-h-40 overflow-auto">
            {pricing?.line_items?.map((item: any, idx: number) => <li key={idx} className="flex justify-between"><span>{item.label}</span><span>${Number(item.amount).toFixed(0)}</span></li>)}
          </ul>
          {pricing?.notes?.length ? <div className="rounded bg-amber-50 border border-amber-200 p-2 text-xs">{pricing.notes.map((n: string) => <p key={n}>• {n}</p>)}</div> : <p className="text-xs text-slate-500">No compatibility notes.</p>}
        </div>

        <form className="card p-4 space-y-2" onSubmit={submitQuote}>
          <h4 className="font-semibold">Request a Quote</h4>
          <input required placeholder="Name" className="w-full border rounded p-2" value={quoteForm.name} onChange={(e) => setQuoteForm({ ...quoteForm, name: e.target.value })} />
          <input required type="email" placeholder="Email" className="w-full border rounded p-2" value={quoteForm.email} onChange={(e) => setQuoteForm({ ...quoteForm, email: e.target.value })} />
          <input placeholder="Phone" className="w-full border rounded p-2" value={quoteForm.phone} onChange={(e) => setQuoteForm({ ...quoteForm, phone: e.target.value })} />
          <textarea placeholder="Message" className="w-full border rounded p-2" value={quoteForm.message} onChange={(e) => setQuoteForm({ ...quoteForm, message: e.target.value })} />
          <button className="rounded bg-slate-900 text-white px-3 py-2" disabled={loading}>{loading ? "Submitting..." : "Submit Quote Request"}</button>
          {status && <p className="text-sm text-emerald-700">{status}</p>}
        </form>
      </div>
    </div>
  );
}
