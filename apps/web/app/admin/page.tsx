"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [leads, setLeads] = useState<any[]>([]);
  const [quotes, setQuotes] = useState<any[]>([]);

  async function loginAndLoad() {
    const loginRes = await fetch(`${API}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "owner@ember-demo.com", password: "Demo1234!" })
    });
    const login = await loginRes.json();
    setToken(login.access_token);

    const [leadRes, quoteRes] = await Promise.all([
      fetch(`${API}/admin/leads`, { headers: { Authorization: `Bearer ${login.access_token}` } }),
      fetch(`${API}/admin/quotes`, { headers: { Authorization: `Bearer ${login.access_token}` } })
    ]);

    setLeads(await leadRes.json());
    setQuotes(await quoteRes.json());
  }

  return (
    <div className="space-y-4">
      <div className="card p-4">
        <h1 className="text-2xl font-semibold">Admin Dashboard</h1>
        <p className="text-slate-600">Demo credentials are pre-seeded for Ember Outdoor Living.</p>
        <button className="rounded bg-slate-900 text-white px-4 py-2 mt-3" onClick={loginAndLoad}>Load Leads & Quotes</button>
        {token && <p className="text-xs break-all mt-2">Auth token: {token.slice(0, 40)}...</p>}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="card p-4">
          <h2 className="font-semibold mb-3">Leads ({leads.length})</h2>
          <ul className="space-y-2 text-sm">
            {leads.map((lead) => <li key={lead.id} className="border-b pb-2">{lead.name} • {lead.email} • {lead.stage}</li>)}
          </ul>
        </div>
        <div className="card p-4">
          <h2 className="font-semibold mb-3">Quotes ({quotes.length})</h2>
          <ul className="space-y-2 text-sm">
            {quotes.map((quote) => <li key={quote.id} className="border-b pb-2">Quote #{quote.id} • ${quote.total} • {quote.status}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}
