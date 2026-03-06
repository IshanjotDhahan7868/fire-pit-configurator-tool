import { ConfiguratorPanel } from "@/components/ConfiguratorPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getProduct(slug: string) {
  const tenant = await fetch(`${API}/public/tenant/${slug}`, { cache: "no-store" });
  if (!tenant.ok) throw new Error("Tenant missing");
  const products = await fetch(`${API}/public/tenant/${slug}/products`, { cache: "no-store" });
  const list = await products.json();
  return { tenant: await tenant.json(), product: list[0] };
}

export default async function ConfiguratorPage({ params }: { params: { tenantSlug: string } }) {
  const { tenant, product } = await getProduct(params.tenantSlug);
  return (
    <div className="space-y-4">
      <div className="card p-4">
        <h2 className="text-2xl font-semibold">{tenant.name}</h2>
        <p className="text-slate-600">{product.name}</p>
      </div>
      <ConfiguratorPanel tenantSlug={params.tenantSlug} productId={product.id} />
    </div>
  );
}
