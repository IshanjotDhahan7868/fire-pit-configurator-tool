"use client";

import { useEffect, useState } from "react";
import { useConfigStore } from "@/lib/store";
import { ConfiguratorScene } from "./ConfiguratorScene";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ConfiguratorPanel({ tenantSlug, productId }: { tenantSlug: string; productId: number }) {
  const { config, setField } = useConfigStore();
  const [price, setPrice] = useState<number>(0);
  const [savedId, setSavedId] = useState<string>("");
  const [quoteStatus, setQuoteStatus] = useState<string>("");

  useEffect(() => {
    const run = async () => {
      const res = await fetch(`${API}/public/pricing`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tenant_slug: tenantSlug, product_id: productId, config })
      });
      if (res.ok) {
        const data = await res.json();
        setPrice(data.total);
      }
    };
    run();
  }, [config, tenantSlug, productId]);

  async function saveConfig() {
    const res = await fetch(`${API}/public/configurations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_slug: tenantSlug, product_id: productId, config })
    });
    const data = await res.json();
    setSavedId(data.public_id);
    window.history.replaceState({}, "", `?config=${data.public_id}`);
  }

  async function requestQuote() {
    if (!savedId) return setQuoteStatus("Save your configuration first.");
    const res = await fetch(`${API}/public/quote-request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        configuration_public_id: savedId,
        name: "Website Customer",
        email: "customer@example.com",
        message: "Please contact me with a formal quote"
      })
    });
    const data = await res.json();
    setQuoteStatus(`Quote #${data.quote_id} requested.`);
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <ConfiguratorScene config={config} />
      <div className="card p-4 space-y-3">
        <h3 className="text-lg font-semibold">Customize your fire pit</h3>
        <select className="w-full border rounded p-2" value={config.shape} onChange={(e) => setField("shape", e.target.value)}>
          <option value="round">Round</option><option value="square">Square</option><option value="rectangular">Rectangular</option>
        </select>
        <select className="w-full border rounded p-2" value={config.material} onChange={(e) => setField("material", e.target.value)}>
          <option value="steel">Steel</option><option value="corten">Corten</option><option value="concrete">Concrete</option><option value="stone">Stone</option>
        </select>
        <select className="w-full border rounded p-2" value={config.size_preset} onChange={(e) => setField("size_preset", e.target.value)}>
          <option value="small">Small</option><option value="medium">Medium</option><option value="large">Large</option><option value="xl">XL</option>
        </select>
        <div className="text-xl font-bold">Live price: ${price.toLocaleString()}</div>
        <div className="flex gap-2">
          <button className="rounded bg-orange-600 text-white px-3 py-2" onClick={saveConfig}>Save & Share</button>
          <button className="rounded bg-slate-900 text-white px-3 py-2" onClick={requestQuote}>Request Quote</button>
        </div>
        {savedId && <p className="text-sm text-slate-600">Saved config: {savedId}</p>}
        {quoteStatus && <p className="text-sm text-emerald-700">{quoteStatus}</p>}
      </div>
    </div>
  );
}
