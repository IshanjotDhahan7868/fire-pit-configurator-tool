from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import authenticate_user, create_access_token, get_current_user
from .database import Base, engine, get_db
from .models import Configuration, Lead, Product, Quote, Tenant
from .pricing import evaluate_price
from .schemas import (
    ConfigurationOut,
    LeadOut,
    LoginInput,
    PriceBreakdown,
    ProductOut,
    QuoteOut,
    QuoteRequestInput,
    SaveConfigurationInput,
    TenantOut,
    Token,
)
from .seed import seed_data
from .services import EmailService, PDFService

app = FastAPI(title="Fire Pit Configurator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

email_service = EmailService()
pdf_service = PDFService()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    seed_data(db)
    db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/token", response_model=Token)
def token(form: LoginInput, db: Session = Depends(get_db)):
    user = authenticate_user(db, form.email, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.id, "tenant_id": user.tenant_id, "role": user.role})
    return Token(access_token=access_token)


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


@app.post("/public/pricing", response_model=PriceBreakdown)
def price(input_data: SaveConfigurationInput, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == input_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return evaluate_price(product.base_price, input_data.config)


@app.post("/public/configurations", response_model=ConfigurationOut)
def save_configuration(input_data: SaveConfigurationInput, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.slug == input_data.tenant_slug).first()
    product = db.query(Product).filter(Product.id == input_data.product_id).first()
    if not tenant or not product:
        raise HTTPException(status_code=404, detail="Tenant or product missing")

    pricing = evaluate_price(product.base_price, input_data.config)
    config = Configuration(
        tenant_id=tenant.id,
        product_id=product.id,
        public_id=input_data.tenant_slug + "-" + str(product.id) + "-" + str(abs(hash(str(input_data.config))) % 1000000),
        config_json=input_data.config.model_dump(),
        pricing_snapshot=pricing.model_dump(),
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    return ConfigurationOut(public_id=config.public_id, pricing_snapshot=pricing, created_at=config.created_at)


@app.get("/public/configurations/{public_id}")
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

    line_items = config.pricing_snapshot.get("surcharges", [])
    line_items = [{"label": "Base + options total", "amount": config.pricing_snapshot.get("total", 0)}] + line_items

    quote = Quote(
        tenant_id=config.tenant_id,
        lead_id=lead.id,
        status="requested",
        total=config.pricing_snapshot.get("total", 0),
        line_items=line_items,
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)

    tenant = db.query(Tenant).filter(Tenant.id == config.tenant_id).first()
    pdf_path = pdf_service.generate_quote_pdf(tenant.name, quote.id, lead.name, quote.total, quote.line_items)
    quote.pdf_path = pdf_path
    db.commit()

    email_service.send_quote_received(tenant.slug, lead.email, f"We received your quote request #{quote.id}.")

    return {"lead_id": lead.id, "quote_id": quote.id, "pdf_path": quote.pdf_path}


@app.get("/admin/leads", response_model=list[LeadOut])
def admin_leads(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Lead).filter(Lead.tenant_id == current_user.tenant_id).order_by(Lead.created_at.desc()).all()


@app.get("/admin/quotes", response_model=list[QuoteOut])
def admin_quotes(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Quote).filter(Quote.tenant_id == current_user.tenant_id).order_by(Quote.created_at.desc()).all()
