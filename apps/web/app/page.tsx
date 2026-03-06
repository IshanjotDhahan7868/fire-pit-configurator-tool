import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-8">
      <section className="card p-10 bg-gradient-to-r from-slate-900 via-slate-800 to-orange-900 text-white">
        <p className="uppercase text-xs tracking-widest text-orange-300">White-label SaaS platform</p>
        <h1 className="text-4xl md:text-5xl font-bold mt-2 leading-tight">Sell More Custom Fire Features with a Branded 3D Buying Experience</h1>
        <p className="mt-4 max-w-2xl text-slate-100">
          Give prospects an interactive configurator with live pricing, then convert them into qualified leads with built-in quote workflows and CRM-ready admin tools.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link className="rounded bg-orange-600 text-white px-4 py-2" href="/t/ember-outdoor/configurator">Launch Demo Configurator</Link>
          <Link className="rounded bg-white/10 border border-white/30 text-white px-4 py-2" href="/t/ember-outdoor/configurator?embed=1">Preview Embed Mode</Link>
          <Link className="rounded bg-white text-slate-900 px-4 py-2" href="/admin">Open Admin Dashboard</Link>
          <Link className="rounded bg-white/10 border border-white/30 text-white px-4 py-2" href="/onboarding">View Onboarding Guide</Link>
        </div>
      </section>

      <section className="grid md:grid-cols-3 gap-4">
        {[
          ["Immersive 3D Configurator", "Shape, size, materials, fuel options, accessories, and shareable saved builds."],
          ["Smart Pricing & Rules", "Line-item pricing, compatibility notes, and configurable surcharge logic."],
          ["Lead-to-Quote Workflow", "Capture leads, manage pipeline stages, and deliver branded PDF quotes."]
        ].map(([title, text]) => (
          <div key={title} className="card p-4">
            <h3 className="font-semibold text-lg">{title}</h3>
            <p className="text-sm text-slate-600 mt-1">{text}</p>
          </div>
        ))}
      </section>

      <section className="card p-6">
        <h2 className="text-2xl font-semibold">Built for Fire Feature Businesses</h2>
        <div className="grid md:grid-cols-2 gap-4 mt-4 text-sm text-slate-700">
          <ul className="space-y-2">
            <li>✅ White-label tenant branding and embed snippet support</li>
            <li>✅ Prospect-facing configurator with instant price feedback</li>
            <li>✅ Tenant-isolated admin data, roles, and quote records</li>
          </ul>
          <ul className="space-y-2">
            <li>✅ Product + pricing rule administration in one dashboard</li>
            <li>✅ Branded PDF quote generation for client presentation</li>
            <li>✅ SaaS-ready scaffolding for billing and onboarding growth</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
