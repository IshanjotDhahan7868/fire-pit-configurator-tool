from datetime import datetime
from sqlalchemy.orm import Session

from .auth import get_password_hash
from .models import PricingRuleSet, Product, Subscription, Tenant, User
from .pricing import DEFAULT_RULES


def seed_data(db: Session):
    tenant = db.query(Tenant).filter(Tenant.slug == "ember-outdoor").first()
    if not tenant:
        tenant = Tenant(
            name="Ember Outdoor Living",
            slug="ember-outdoor",
            brand_primary="#ea580c",
            brand_secondary="#1f2937",
        )
        db.add(tenant)
        db.flush()

    user = db.query(User).filter(User.email == "owner@ember-demo.com").first()
    if not user:
        db.add(
            User(
                email="owner@ember-demo.com",
                password_hash=get_password_hash("Demo1234!"),
                full_name="Demo Owner",
                tenant_id=tenant.id,
                role="owner",
            )
        )

    product = db.query(Product).filter(Product.tenant_id == tenant.id, Product.name == "Summit Signature Fire Pit").first()
    if not product:
        db.add(
            Product(
                tenant_id=tenant.id,
                name="Summit Signature Fire Pit",
                description="Premium customizable outdoor fire pit.",
                base_price=2895,
                config_schema={
                    "sizes": ["small", "medium", "large", "xl"],
                    "materials": ["steel", "corten", "concrete", "stone"],
                    "fuels": ["wood", "propane", "natural_gas"],
                    "accessories": ["cover", "wind_guard", "lid", "spark_screen", "grate"],
                },
            )
        )

    rules = db.query(PricingRuleSet).filter(PricingRuleSet.tenant_id == tenant.id).first()
    if not rules:
        db.add(PricingRuleSet(tenant_id=tenant.id, rules_json=DEFAULT_RULES, updated_at=datetime.utcnow()))

    sub = db.query(Subscription).filter(Subscription.tenant_id == tenant.id).first()
    if not sub:
        db.add(Subscription(tenant_id=tenant.id, provider="stripe", status="trialing", updated_at=datetime.utcnow()))

    db.commit()
