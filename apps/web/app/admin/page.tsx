"use client";

import { useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const parseJsonSafe = (text: string, fallback: any) => { try { return JSON.parse(text); } catch { return fallback; } };
const NAV = ["overview", "leads", "quotes", "catalog", "pricing", "settings"] as const;
type NavKey = typeof NAV[number];

export default function AdminPage() {
  const [creds, setCreds] = useState({ email: "owner@ember-demo.com", password: "Demo1234!" });
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [active, setActive] = useState<NavKey>("overview");

  const [me, setMe] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [onboarding, setOnboarding] = useState<any>(null);
  const [search, setSearch] = useState("");
  const [leads, setLeads] = useState<any[]>([]);
  const [quotes, setQuotes] = useState<any[]>([]);
  const [selectedQuote, setSelectedQuote] = useState<any>(null);
  const [products, setProducts] = useState<any[]>([]);
  const [rules, setRules] = useState<any>({});
  const [branding, setBranding] = useState<any>({ name: "", brand_primary: "#ea580c", brand_secondary: "#1f2937", logo_url: "" });
  const [embed, setEmbed] = useState<any>(null);
  const [subscription, setSubscription] = useState<any>(null);

  const authHeaders = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

  async function login() {
    setError("");
    setLoading(true);
    const r = await fetch(`${API}/auth/token`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(creds) });
    const data = await r.json();
    if (!r.ok) {
      setLoading(false);
      return setError(data.detail || "Login failed");
    }
    setToken(data.access_token);
    const meRes = await fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${data.access_token}` } });
    setMe(await meRes.json());
    await loadAll(data.access_token);
    setLoading(false);
  }

  async function loadAll(tok = token) {
    const h = { Authorization: `Bearer ${tok}` };
    const [leadsR, quotesR, productsR, rulesR, subR, embedR, tenantR, analyticsR, onboardingR] = await Promise.all([
      fetch(`${API}/admin/leads?search=${encodeURIComponent(search)}`, { headers: h }),
      fetch(`${API}/admin/quotes`, { headers: h }),
      fetch(`${API}/admin/products`, { headers: h }),
      fetch(`${API}/admin/pricing-rules`, { headers: h }),
      fetch(`${API}/admin/subscription`, { headers: h }),
      fetch(`${API}/admin/embed`, { headers: h }),
      fetch(`${API}/admin/tenant`, { headers: h }),
      fetch(`${API}/admin/analytics`, { headers: h }),
      fetch(`${API}/admin/onboarding`, { headers: h }),
    ]);
    setLeads(await leadsR.json());
    setQuotes(await quotesR.json());
    setProducts(await productsR.json());
    setRules((await rulesR.json()).rules_json || {});
    setSubscription(await subR.json());
    setEmbed(await embedR.json());
    const tenant = await tenantR.json();
    setBranding({ name: tenant.name, brand_primary: tenant.brand_primary, brand_secondary: tenant.brand_secondary, logo_url: tenant.logo_url || "" });
    setAnalytics(await analyticsR.json());
    setOnboarding(await onboardingR.json());
  }

  async function patchLead(lead: any) { await fetch(`${API}/admin/leads/${lead.id}`, { method: "PATCH", headers: authHeaders, body: JSON.stringify({ stage: lead.stage, internal_notes: lead.internal_notes || "" }) }); loadAll(); }
  async function patchQuote(quote: any) { await fetch(`${API}/admin/quotes/${quote.id}`, { method: "PATCH", headers: authHeaders, body: JSON.stringify({ status: quote.status, internal_notes: quote.internal_notes || "" }) }); loadAll(); }
  async function openQuote(quoteId: number) { const res = await fetch(`${API}/admin/quotes/${quoteId}`, { headers: { Authorization: `Bearer ${token}` } }); setSelectedQuote(await res.json()); setActive("quotes"); }
  async function downloadPdf(quoteId: number) { const res = await fetch(`${API}/admin/quotes/${quoteId}/pdf`, { headers: { Authorization: `Bearer ${token}` } }); if (!res.ok) return alert("Unable to open PDF"); window.open(URL.createObjectURL(await res.blob()), "_blank"); }
  async function saveProduct(product: any) { await fetch(`${API}/admin/products/${product.id}`, { method: "PUT", headers: authHeaders, body: JSON.stringify(product) }); loadAll(); }
  async function saveRules() { await fetch(`${API}/admin/pricing-rules`, { method: "PUT", headers: authHeaders, body: JSON.stringify({ rules_json: rules }) }); alert("Pricing rules saved"); }
  async function saveBranding() { await fetch(`${API}/admin/branding`, { method: "PUT", headers: authHeaders, body: JSON.stringify({ ...branding, logo_url: branding.logo_url || null }) }); alert("Branding saved"); loadAll(); }

  if (!token) return (
    <div className="max-w-md mx-auto mt-8 card p-6 space-y-3">
      <h1 className="text-2xl font-semibold">Admin Sign In</h1>
      <p className="text-sm text-slate-600">Manage catalog, leads, pricing, quotes, branding, and embeds.</p>
      <input className="w-full border rounded p-2" placeholder="Email" value={creds.email} onChange={(e) => setCreds({ ...creds, email: e.target.value })} />
      <input type="password" className="w-full border rounded p-2" placeholder="Password" value={creds.password} onChange={(e) => setCreds({ ...creds, password: e.target.value })} />
      <button className="rounded bg-slate-900 text-white px-4 py-2" disabled={loading} onClick={login}>{loading ? "Signing in..." : "Sign in"}</button>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <p className="text-xs text-slate-500">Demo: owner@ember-demo.com / Demo1234!</p>
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="card p-4 flex flex-wrap justify-between gap-3 items-center">
        <div>
          <h1 className="text-2xl font-semibold">Admin Workspace</h1>
          <p className="text-sm text-slate-600">{me?.email} • {me?.role}</p>
        </div>
        <button className="px-3 py-2 rounded bg-slate-900 text-white" onClick={() => loadAll()}>Refresh</button>
      </div>

      <div className="card p-2 flex flex-wrap gap-2">
        {NAV.map((item) => <button key={item} onClick={() => setActive(item)} className={`px-3 py-2 rounded capitalize ${active===item?"bg-slate-900 text-white":"bg-slate-100"}`}>{item}</button>)}
      </div>

      {active === "overview" && (
        <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
          {[ ["Leads", analytics?.leads_total], ["Quotes", analytics?.quotes_total], ["Avg Quote", `$${analytics?.avg_quote ?? 0}`], ["Quote Accept", `${analytics?.quote_accept_rate ?? 0}%`] ].map(([label,val]) => (
            <div key={String(label)} className="card p-4"><p className="text-xs text-slate-500 uppercase">{label}</p><p className="text-2xl font-semibold mt-1">{val ?? "-"}</p></div>
          ))}
          <div className="card p-4 md:col-span-2 xl:col-span-4">
            <p className="text-sm font-semibold">Onboarding progress: {onboarding?.progress_pct ?? 0}%</p>
            <div className="h-2 bg-slate-200 rounded mt-2"><div className="h-2 bg-orange-500 rounded" style={{ width: `${onboarding?.progress_pct ?? 0}%` }} /></div>
            <ul className="mt-3 text-sm space-y-1">{onboarding?.steps?.map((s: any) => <li key={s.key}>{s.done ? "✅" : "⬜"} {s.label}</li>)}</ul>
          </div>
        </div>
      )}

      {active === "leads" && (
        <section className="card p-4 space-y-2">
          <div className="flex gap-2"><input className="border rounded p-2 flex-1" placeholder="Search leads" value={search} onChange={(e) => setSearch(e.target.value)} /><button onClick={() => loadAll()} className="px-3 py-2 bg-slate-900 text-white rounded">Search</button></div>
          {leads.length === 0 ? <p className="text-sm text-slate-500">No leads yet.</p> : leads.map((lead) => (
            <div key={lead.id} className="border rounded p-2 text-sm space-y-1">
              <p className="font-medium">{lead.name} • {lead.email}</p>
              <select className="border rounded p-1" value={lead.stage} onChange={(e)=>setLeads(leads.map(l=>l.id===lead.id?{...l,stage:e.target.value}:l))}><option>new</option><option>qualified</option><option>quoted</option><option>won</option><option>lost</option></select>
              <textarea className="w-full border rounded p-1" placeholder="Internal notes" value={lead.internal_notes||""} onChange={(e)=>setLeads(leads.map(l=>l.id===lead.id?{...l,internal_notes:e.target.value}:l))}/>
              <button className="px-2 py-1 rounded bg-orange-600 text-white" onClick={()=>patchLead(lead)}>Update lead</button>
            </div>
          ))}
        </section>
      )}

      {active === "quotes" && (
        <section className="grid lg:grid-cols-2 gap-4">
          <div className="card p-4 space-y-2">
            {quotes.length === 0 ? <p className="text-sm text-slate-500">No quotes yet.</p> : quotes.map((quote) => (
              <div key={quote.id} className="border rounded p-2 text-sm space-y-1">
                <p className="font-medium">Quote #{quote.id} • ${quote.total}</p>
                <select className="border rounded p-1" value={quote.status} onChange={(e)=>setQuotes(quotes.map(q=>q.id===quote.id?{...q,status:e.target.value}:q))}><option>requested</option><option>draft</option><option>sent</option><option>accepted</option><option>declined</option></select>
                <textarea className="w-full border rounded p-1" placeholder="Internal notes" value={quote.internal_notes||""} onChange={(e)=>setQuotes(quotes.map(q=>q.id===quote.id?{...q,internal_notes:e.target.value}:q))}/>
                <div className="flex gap-2"><button className="px-2 py-1 rounded bg-orange-600 text-white" onClick={()=>patchQuote(quote)}>Save</button><button className="px-2 py-1 rounded bg-slate-900 text-white" onClick={()=>openQuote(quote.id)}>Detail</button><button className="underline" onClick={()=>downloadPdf(quote.id)}>PDF</button></div>
              </div>
            ))}
          </div>
          <div className="card p-4">{selectedQuote ? (<><h2 className="font-semibold">Quote Detail #{selectedQuote.id}</h2><p className="text-sm">Lead: {selectedQuote.lead?.name} ({selectedQuote.lead?.email})</p><ul className="mt-2 text-sm">{selectedQuote.line_items?.map((item: any, idx: number) => <li key={idx} className="flex justify-between"><span>{item.label}</span><span>${Number(item.amount).toFixed(2)}</span></li>)}</ul></>) : <p className="text-sm text-slate-500">Select a quote to view detail.</p>}</div>
        </section>
      )}

      {active === "catalog" && (
        <section className="card p-4 space-y-3">
          <h2 className="font-semibold">Catalog Editor</h2>
          {products.map((product)=>(
            <div key={product.id} className="border rounded p-2 space-y-1">
              <input className="w-full border rounded p-1" value={product.name} onChange={(e)=>setProducts(products.map(x=>x.id===product.id?{...x,name:e.target.value}:x))}/>
              <textarea className="w-full border rounded p-1" value={product.description} onChange={(e)=>setProducts(products.map(x=>x.id===product.id?{...x,description:e.target.value}:x))}/>
              <input className="w-full border rounded p-1" type="number" value={product.base_price} onChange={(e)=>setProducts(products.map(x=>x.id===product.id?{...x,base_price:Number(e.target.value)}:x))}/>
              <textarea className="w-full border rounded p-1 h-24" value={JSON.stringify(product.config_schema, null, 2)} onChange={(e)=>setProducts(products.map(x=>x.id===product.id?{...x,config_schema:parseJsonSafe(e.target.value||"{}", product.config_schema)}:x))}/>
              <button className="px-2 py-1 bg-slate-900 text-white rounded" onClick={()=>saveProduct(product)}>Save product</button>
            </div>
          ))}
        </section>
      )}

      {active === "pricing" && (
        <section className="card p-4 space-y-3">
          <h2 className="font-semibold">Pricing Rules</h2>
          <p className="text-sm text-slate-600">Edit JSON surcharges for size/material/fuel/accessory. Changes apply to live pricing immediately.</p>
          <textarea className="w-full border rounded p-2 h-56 font-mono text-sm" value={JSON.stringify(rules, null, 2)} onChange={(e)=>setRules(parseJsonSafe(e.target.value||"{}", rules))} />
          <button className="px-3 py-2 bg-slate-900 text-white rounded" onClick={saveRules}>Save pricing rules</button>
        </section>
      )}

      {active === "settings" && (
        <section className="card p-4 space-y-3">
          <h2 className="font-semibold">Brand, Embed & Billing</h2>
          <input className="w-full border rounded p-1" placeholder="Business name" value={branding.name} onChange={(e)=>setBranding({...branding,name:e.target.value})}/>
          <div className="grid sm:grid-cols-2 gap-2"><input className="w-full border rounded p-1" placeholder="#ea580c" value={branding.brand_primary} onChange={(e)=>setBranding({...branding,brand_primary:e.target.value})}/><input className="w-full border rounded p-1" placeholder="#1f2937" value={branding.brand_secondary} onChange={(e)=>setBranding({...branding,brand_secondary:e.target.value})}/></div>
          <input className="w-full border rounded p-1" placeholder="Logo URL" value={branding.logo_url||""} onChange={(e)=>setBranding({...branding,logo_url:e.target.value})}/>
          <button className="px-3 py-2 bg-orange-600 text-white rounded" onClick={saveBranding}>Save branding</button>
          <div className="text-xs text-slate-600">Embed URL: {embed?.embed_url}</div>
          <textarea className="w-full border rounded p-2 h-24 text-xs" readOnly value={embed?.snippet || ""} />
          <div className="text-sm">Billing: <span className="font-medium">{subscription?.provider}</span> • {subscription?.status}</div>
        </section>
      )}
    </div>
  );
}
