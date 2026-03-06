from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, HttpUrl

Role = Literal["owner", "admin", "sales", "viewer"]
LeadStage = Literal["new", "qualified", "quoted", "won", "lost"]
QuoteStatus = Literal["requested", "draft", "sent", "accepted", "declined"]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserContext(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    tenant_id: int


class TenantOut(BaseModel):
    id: int
    name: str
    slug: str
    brand_primary: str
    brand_secondary: str
    logo_url: str | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    base_price: float
    is_active: bool
    config_schema: dict[str, Any]


class ProductUpdate(BaseModel):
    name: str = Field(min_length=2)
    description: str = ""
    base_price: float = Field(ge=0)
    is_active: bool = True
    config_schema: dict[str, Any] = Field(default_factory=dict)


class ConfigInput(BaseModel):
    shape: Literal["round", "square", "rectangular"]
    size_preset: str
    material: str
    finish: str
    fuel_type: str
    burner: str
    media: str
    ignition: str
    accessories: list[str] = Field(default_factory=list)


class PriceBreakdown(BaseModel):
    subtotal: float
    surcharges: list[dict[str, Any]]
    line_items: list[dict[str, Any]]
    total: float
    notes: list[str]


class SaveConfigurationInput(BaseModel):
    tenant_slug: str
    product_id: int
    config: ConfigInput


class ConfigurationOut(BaseModel):
    public_id: str
    pricing_snapshot: PriceBreakdown
    created_at: datetime


class ConfigurationFullOut(BaseModel):
    public_id: str
    config: ConfigInput
    pricing_snapshot: PriceBreakdown
    created_at: datetime


class QuoteRequestInput(BaseModel):
    configuration_public_id: str
    name: str = Field(min_length=2)
    email: EmailStr
    phone: str | None = None
    message: str | None = None


class LeadOut(BaseModel):
    id: int
    name: str
    email: str
    stage: LeadStage
    internal_notes: str
    created_at: datetime


class LeadUpdate(BaseModel):
    stage: LeadStage
    internal_notes: str = ""


class QuoteOut(BaseModel):
    id: int
    status: QuoteStatus
    total: float
    pdf_path: str | None
    internal_notes: str


class QuoteDetailOut(BaseModel):
    id: int
    status: QuoteStatus
    total: float
    internal_notes: str
    pdf_path: str | None
    line_items: list[dict[str, Any]]
    lead: dict[str, Any]


class QuoteUpdate(BaseModel):
    status: QuoteStatus
    internal_notes: str = ""


class PricingRulesUpdate(BaseModel):
    rules_json: dict[str, Any]


class BrandingUpdate(BaseModel):
    name: str = Field(min_length=2)
    brand_primary: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    brand_secondary: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    logo_url: HttpUrl | None = None


class SubscriptionOut(BaseModel):
    provider: str
    status: str
    external_customer_id: str | None
