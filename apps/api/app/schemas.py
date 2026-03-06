from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TenantOut(BaseModel):
    id: int
    name: str
    slug: str
    brand_primary: str
    brand_secondary: str


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    base_price: float


class ConfigInput(BaseModel):
    shape: str = Field(pattern="^(round|square|rectangular)$")
    size_preset: str
    material: str
    finish: str
    fuel_type: str
    burner: str
    media: str
    ignition: str
    accessories: list[str] = []


class PriceBreakdown(BaseModel):
    subtotal: float
    surcharges: list[dict[str, Any]]
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


class QuoteRequestInput(BaseModel):
    configuration_public_id: str
    name: str
    email: EmailStr
    phone: str | None = None
    message: str | None = None


class LeadOut(BaseModel):
    id: int
    name: str
    email: str
    stage: str
    created_at: datetime


class QuoteOut(BaseModel):
    id: int
    status: str
    total: float
    pdf_path: str | None
