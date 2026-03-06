from datetime import datetime
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import authenticate_user, create_access_token, get_current_user, require_roles
from .config import settings
from .database import get_db
from .migrations import run_migrations
from .models import Configuration, Lead, PricingRuleSet, Product, Quote, Subscription, Tenant
from .pricing import DEFAULT_RULES, evaluate_price
from .schemas import (
    BrandingUpdate,
    ConfigurationFullOut,
    ConfigurationOut,
    LeadOut,
    LeadUpdate,
    LoginInput,
    PriceBreakdown,
    PricingRulesUpdate,
    ProductOut,
    ProductUpdate,
    QuoteDetailOut,
    QuoteOut,
    QuoteRequestInput,
    QuoteUpdate,
    SaveConfigurationInput,
    SubscriptionOut,
    TenantOut,
    Token,
    UserContext,
)
from .seed import seed_data
from .services import EmailService, PDFService

app = FastAPI(title="Fire Pit Configurator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

email_service = EmailService()
pdf_service = PDFService()


@app.on_event("startup")
def on_startup():
    run_migrations()
    db = next(get_db())
    seed_data(db)
    db.close()


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}


@app.post("/auth/token", response_model=Token)
def token(form: LoginInput, db: Session = Depends(get_db)):
    user = authenticate_user(db, form.email, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id), "tenant_id": user.tenant_id, "role": user.role})
    return Token(access_token=access_token)


@app.get("/auth/me", response_model=UserContext)
def me(current_user=Depends(get_current_user)):
    return UserContext(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        tenant_id=current_user.tenant_id,
    )


@app.get("/public/tenant/{slug}", response_model=TenantOut)
def get_tenant(slug: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.slug == slug).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@app.get("/public/tenant/{slug}/products", response_model=list[ProductOut])
def get_products(slug: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.slug == slug).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return db.query(Product).filter(Product.tenant_id == tenant.id, Product.is_active.is_(True)).all()


def get_tenant_rules(db: Session, tenant_id: int) -> dict:
    rules = db.query(PricingRuleSet).filter(PricingRuleSet.tenant_id == tenant_id).first()
    return rules.rules_json if rules else DEFAULT_RULES


@app.post("/public/pricing", response_model=PriceBreakdown)
def price(input_data: SaveConfigurationInput, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.slug == input_data.tenant_slug).first()
    product = db.query(Product).filter(Product.id == input_data.product_id).first()
    if not tenant or not product or product.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Tenant or product not found")
    return evaluate_price(product.base_price, input_data.config, get_tenant_rules(db, tenant.id))


@app.post("/public/configurations", response_model=ConfigurationOut)
def save_configuration(input_data: SaveConfigurationInput, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.slug == input_data.tenant_slug).first()
    product = db.query(Product).filter(Product.id == input_data.product_id).first()
    if not tenant or not product or product.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Tenant or product missing")

    pricing = evaluate_price(product.base_price, input_data.config, get_tenant_rules(db, tenant.id))
    public_id = f"{tenant.slug}-{uuid4().hex[:12]}"
    config = Configuration(
        tenant_id=tenant.id,
        product_id=product.id,
        public_id=public_id,
        config_json=input_data.config.model_dump(),
        pricing_snapshot=pricing.model_dump(),
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    return ConfigurationOut(public_id=config.public_id, pricing_snapshot=pricing, created_at=config.created_at)


@app.get("/public/configurations/{public_id}", response_model=ConfigurationFullOut)
def get_configuration(public_id: str, db: Session = Depends(get_db)):
    config = db.query(Configuration).filter(Configuration.public_id == public_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {
        "public_id": config.public_id,
        "config": config.config_json,
        "pricing_snapshot": config.pricing_snapshot,
        "created_at": config.created_at,
    }


@app.post("/public/quote-request")
def quote_request(input_data: QuoteRequestInput, db: Session = Depends(get_db)):
    config = db.query(Configuration).filter(Configuration.public_id == input_data.configuration_public_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    lead = Lead(
        tenant_id=config.tenant_id,
        configuration_id=config.id,
        name=input_data.name,
        email=input_data.email,
        phone=input_data.phone,
        message=input_data.message,
    )
    db.add(lead)
    db.flush()

    quote = Quote(
        tenant_id=config.tenant_id,
        lead_id=lead.id,
        status="requested",
        total=float(config.pricing_snapshot.get("total", 0)),
        line_items=config.pricing_snapshot.get("line_items", []),
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)

    tenant = db.query(Tenant).filter(Tenant.id == config.tenant_id).first()
    pdf_path = pdf_service.generate_quote_pdf(tenant.name, quote.id, lead.name, quote.total, quote.line_items, tenant.brand_primary, tenant.brand_secondary)
    quote.pdf_path = pdf_path
    db.commit()

    email_service.send_quote_received(tenant.slug, lead.email, f"We received your quote request #{quote.id}.")

    return {"lead_id": lead.id, "quote_id": quote.id, "pdf_path": quote.pdf_path}


@app.get("/admin/leads", response_model=list[LeadOut])
def admin_leads(search: str | None = Query(default=None), current_user=Depends(require_roles("owner", "admin", "sales", "viewer")), db: Session = Depends(get_db)):
    q = db.query(Lead).filter(Lead.tenant_id == current_user.tenant_id)
    if search:
        q = q.filter(Lead.name.contains(search) | Lead.email.contains(search))
    return q.order_by(Lead.created_at.desc()).all()


@app.patch("/admin/leads/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, payload: LeadUpdate, current_user=Depends(require_roles("owner", "admin", "sales")), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == current_user.tenant_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.stage = payload.stage
    lead.internal_notes = payload.internal_notes
    db.commit()
    db.refresh(lead)
    return lead


@app.get("/admin/quotes", response_model=list[QuoteOut])
def admin_quotes(current_user=Depends(require_roles("owner", "admin", "sales", "viewer")), db: Session = Depends(get_db)):
    return db.query(Quote).filter(Quote.tenant_id == current_user.tenant_id).order_by(Quote.created_at.desc()).all()


@app.patch("/admin/quotes/{quote_id}", response_model=QuoteOut)
def update_quote(quote_id: int, payload: QuoteUpdate, current_user=Depends(require_roles("owner", "admin", "sales")), db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == current_user.tenant_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    quote.status = payload.status
    quote.internal_notes = payload.internal_notes
    db.commit()
    db.refresh(quote)
    return quote


@app.get("/admin/products", response_model=list[ProductOut])
def admin_products(current_user=Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.tenant_id == current_user.tenant_id).all()


@app.put("/admin/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, current_user=Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.tenant_id == current_user.tenant_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@app.get("/admin/pricing-rules")
def get_pricing_rules(current_user=Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    rules = db.query(PricingRuleSet).filter(PricingRuleSet.tenant_id == current_user.tenant_id).first()
    return {"rules_json": rules.rules_json if rules else DEFAULT_RULES}


@app.put("/admin/pricing-rules")
def update_pricing_rules(payload: PricingRulesUpdate, current_user=Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    rules = db.query(PricingRuleSet).filter(PricingRuleSet.tenant_id == current_user.tenant_id).first()
    if not rules:
        rules = PricingRuleSet(tenant_id=current_user.tenant_id, rules_json=payload.rules_json, updated_at=datetime.utcnow())
        db.add(rules)
    else:
        rules.rules_json = payload.rules_json
        rules.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}


@app.put("/admin/branding", response_model=TenantOut)
def update_branding(payload: BrandingUpdate, current_user=Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    tenant.name = payload.name
    tenant.brand_primary = payload.brand_primary
    tenant.brand_secondary = payload.brand_secondary
    tenant.logo_url = payload.logo_url
    db.commit()
    db.refresh(tenant)
    return tenant


@app.get("/admin/tenant", response_model=TenantOut)
def admin_tenant(current_user=Depends(require_roles("owner", "admin", "sales", "viewer")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@app.get("/admin/subscription", response_model=SubscriptionOut)
def get_subscription(current_user=Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.tenant_id == current_user.tenant_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


@app.get("/admin/analytics")
def admin_analytics(current_user=Depends(require_roles("owner", "admin", "sales", "viewer")), db: Session = Depends(get_db)):
    tenant_id = current_user.tenant_id
    leads_total = db.query(func.count(Lead.id)).filter(Lead.tenant_id == tenant_id).scalar() or 0
    quotes_total = db.query(func.count(Quote.id)).filter(Quote.tenant_id == tenant_id).scalar() or 0
    won_leads = db.query(func.count(Lead.id)).filter(Lead.tenant_id == tenant_id, Lead.stage == "won").scalar() or 0
    avg_quote = db.query(func.avg(Quote.total)).filter(Quote.tenant_id == tenant_id).scalar() or 0
    accepted_quotes = db.query(func.count(Quote.id)).filter(Quote.tenant_id == tenant_id, Quote.status == "accepted").scalar() or 0
    return {
        "leads_total": int(leads_total),
        "quotes_total": int(quotes_total),
        "won_leads": int(won_leads),
        "accepted_quotes": int(accepted_quotes),
        "avg_quote": round(float(avg_quote), 2),
        "lead_to_quote_rate": round((quotes_total / leads_total) * 100, 1) if leads_total else 0,
        "quote_accept_rate": round((accepted_quotes / quotes_total) * 100, 1) if quotes_total else 0,
    }


@app.get("/admin/onboarding")
def admin_onboarding(current_user=Depends(require_roles("owner", "admin", "sales", "viewer")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    product_count = db.query(func.count(Product.id)).filter(Product.tenant_id == current_user.tenant_id).scalar() or 0
    rules = db.query(PricingRuleSet).filter(PricingRuleSet.tenant_id == current_user.tenant_id).first()
    sub = db.query(Subscription).filter(Subscription.tenant_id == current_user.tenant_id).first()
    steps = [
        {"key": "tenant_profile", "label": "Complete brand profile", "done": bool(tenant and tenant.name and tenant.brand_primary and tenant.brand_secondary)},
        {"key": "catalog", "label": "Add at least one active product", "done": product_count > 0},
        {"key": "pricing", "label": "Review pricing rules", "done": bool(rules and rules.rules_json)},
        {"key": "billing", "label": "Connect billing", "done": bool(sub and sub.status in {"trialing", "active"})},
        {"key": "embed", "label": "Install embed snippet", "done": bool(tenant and tenant.embed_enabled)},
    ]
    completed = sum(1 for s in steps if s["done"])
    return {"steps": steps, "completed": completed, "total": len(steps), "progress_pct": round((completed/len(steps))*100,1)}

@app.get("/admin/embed")
def get_embed_info(current_user=Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    return {
        "embed_url": f"http://localhost:3000/t/{tenant.slug}/configurator?embed=1",
        "snippet": f'<iframe src="http://localhost:3000/t/{tenant.slug}/configurator?embed=1" style="width:100%;height:800px;border:0;" loading="lazy"></iframe>'
    }


@app.get("/admin/quotes/{quote_id}", response_model=QuoteDetailOut)
def quote_detail(quote_id: int, current_user=Depends(require_roles("owner", "admin", "sales", "viewer")), db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == current_user.tenant_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    lead = db.query(Lead).filter(Lead.id == quote.lead_id, Lead.tenant_id == current_user.tenant_id).first()
    return {
        "id": quote.id,
        "status": quote.status,
        "total": quote.total,
        "internal_notes": quote.internal_notes,
        "pdf_path": quote.pdf_path,
        "line_items": quote.line_items,
        "lead": {
            "id": lead.id if lead else None,
            "name": lead.name if lead else None,
            "email": lead.email if lead else None,
            "stage": lead.stage if lead else None,
        },
    }

@app.get("/admin/quotes/{quote_id}/pdf")
def quote_pdf(quote_id: int, current_user=Depends(require_roles("owner", "admin", "sales", "viewer")), db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id, Quote.tenant_id == current_user.tenant_id).first()
    if not quote or not quote.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(quote.pdf_path, media_type="application/pdf")
