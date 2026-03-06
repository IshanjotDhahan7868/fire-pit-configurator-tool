import { ConfiguratorPanel } from "@/components/ConfiguratorPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getData(slug: string) {
  const tenant = await fetch(`${API}/public/tenant/${slug}`, { cache: "no-store" });
  if (!tenant.ok) throw new Error("Tenant missing");
  const products = await fetch(`${API}/public/tenant/${slug}/products`, { cache: "no-store" });
  const list = await products.json();
  return { tenant: await tenant.json(), product: list[0] };
}

export default async function ConfiguratorPage({ params, searchParams }: { params: { tenantSlug: string }, searchParams: { embed?: string } }) {
  const { tenant, product } = await getData(params.tenantSlug);
  const embed = searchParams.embed === "1";
  return (
    <div className="space-y-4">
      {!embed ? (
        <div className="card p-4" style={{ borderTop: `6px solid ${tenant.brand_primary}` }}>
          <h2 className="text-2xl font-semibold" style={{ color: tenant.brand_secondary }}>{tenant.name}</h2>
          <p className="text-slate-600">{product.name}</p>
        </div>
      ) : (
        <div className="text-xs text-slate-500">Embedded Configurator • {tenant.name}</div>
      )}
      <ConfiguratorPanel tenantSlug={params.tenantSlug} productId={product.id} />
    </div>
  );
}
