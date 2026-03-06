from app.auth import get_password_hash
from app.database import SessionLocal
from app.main import app
from app.models import Configuration, Lead, Product, Tenant, User
from fastapi.testclient import TestClient

client = TestClient(app)


def test_admin_leads_are_tenant_scoped():
    db = SessionLocal()
    other = db.query(Tenant).filter(Tenant.slug == "other-tenant").first()
    if not other:
        other = Tenant(name="Other Tenant", slug="other-tenant", brand_primary="#111111", brand_secondary="#222222")
        db.add(other)
        db.flush()
        db.add(User(email="admin@other.com", password_hash=get_password_hash("Demo1234!"), full_name="Other Admin", tenant_id=other.id, role="owner"))
        product = db.query(Product).filter(Product.tenant_id == other.id).first()
        if not product:
            product = Product(tenant_id=other.id, name="Other Product", description="", base_price=1000, is_active=True, config_schema={})
            db.add(product)
            db.flush()
        config = Configuration(tenant_id=other.id, product_id=product.id, public_id="other-config-1", config_json={"shape":"round","size_preset":"small","material":"steel","finish":"x","fuel_type":"wood","burner":"none","media":"lava_rock","ignition":"manual","accessories":[]}, pricing_snapshot={"total":1000,"line_items":[],"surcharges":[],"notes":[],"subtotal":1000})
        db.add(config)
        db.flush()
        db.add(Lead(tenant_id=other.id, configuration_id=config.id, name="Other Lead", email="other@example.com", stage="new"))
        db.commit()
    db.close()

    login = client.post("/auth/token", json={"email": "owner@ember-demo.com", "password": "Demo1234!"})
    token = login.json()["access_token"]
    leads = client.get("/admin/leads", headers={"Authorization": f"Bearer {token}"})
    assert leads.status_code == 200
    assert all("other@example.com" != l["email"] for l in leads.json())
