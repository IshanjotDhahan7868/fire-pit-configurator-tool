import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-6">
      <section className="card p-8">
        <h1 className="text-3xl font-bold">Fire Pit Configurator Platform</h1>
        <p className="text-slate-600 mt-2">White-label SaaS for custom outdoor fire feature businesses.</p>
        <div className="mt-4 flex gap-3">
          <Link className="rounded bg-orange-600 text-white px-4 py-2" href="/t/ember-outdoor/configurator">Launch Demo Configurator</Link>
          <Link className="rounded bg-slate-900 text-white px-4 py-2" href="/admin">Open Admin Dashboard</Link>
        </div>
      </section>
    </div>
  );
}
