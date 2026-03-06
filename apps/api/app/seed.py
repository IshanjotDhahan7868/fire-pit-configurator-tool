from sqlalchemy.orm import Session

from .auth import get_password_hash
from .models import Product, Tenant, User


def seed_data(db: Session):
    existing = db.query(Tenant).filter(Tenant.slug == "ember-outdoor").first()
    if existing:
        return

    tenant = Tenant(
        name="Ember Outdoor Living",
        slug="ember-outdoor",
        brand_primary="#ea580c",
        brand_secondary="#1f2937",
    )
    db.add(tenant)
    db.flush()

    db.add(
        User(
            email="owner@ember-demo.com",
            password_hash=get_password_hash("Demo1234!"),
            full_name="Demo Owner",
            tenant_id=tenant.id,
            role="owner",
        )
    )

    db.add(
        Product(
            tenant_id=tenant.id,
            name="Summit Signature Fire Pit",
            description="Premium customizable outdoor fire pit.",
            base_price=2895,
        )
    )

    db.commit()
