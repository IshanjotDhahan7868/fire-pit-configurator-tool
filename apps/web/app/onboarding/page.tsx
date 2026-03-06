import Link from "next/link";

export default function OnboardingPage() {
  const steps = [
    { title: "Create your tenant", description: "Provision your tenant slug, owner account, and role memberships." },
    { title: "Brand your experience", description: "Set company name, logo URL, and brand colors for configurator + quote PDF." },
    { title: "Configure catalog and pricing", description: "Add products and adjust size/material/fuel/accessory pricing rules." },
    { title: "Install embed", description: "Place iframe snippet on your marketing site and begin collecting leads." },
  ];

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h1 className="text-3xl font-semibold">Tenant Onboarding Guide</h1>
        <p className="text-slate-600 mt-2">Use this flow to bring new fire feature businesses live in under 30 minutes.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {steps.map((step, idx) => (
          <div key={step.title} className="card p-4">
            <p className="text-xs text-slate-500 uppercase">Step {idx + 1}</p>
            <h2 className="font-semibold mt-1">{step.title}</h2>
            <p className="text-sm text-slate-600 mt-1">{step.description}</p>
          </div>
        ))}
      </div>

      <div className="card p-4 flex flex-wrap gap-3">
        <Link className="rounded bg-slate-900 text-white px-4 py-2" href="/admin">Go to Admin</Link>
        <Link className="rounded bg-orange-600 text-white px-4 py-2" href="/t/ember-outdoor/configurator">View Configurator Demo</Link>
      </div>
    </div>
  );
}
