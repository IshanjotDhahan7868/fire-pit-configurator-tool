CREATE TABLE IF NOT EXISTS schema_migrations (
  version VARCHAR(64) PRIMARY KEY,
  applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tenants (
  id INTEGER PRIMARY KEY,
  name VARCHAR(120) UNIQUE NOT NULL,
  slug VARCHAR(80) UNIQUE NOT NULL,
  brand_primary VARCHAR(20) NOT NULL DEFAULT '#d97706',
  brand_secondary VARCHAR(20) NOT NULL DEFAULT '#111827',
  logo_url VARCHAR(250),
  embed_enabled BOOLEAN NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  email VARCHAR(160) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(120) NOT NULL,
  tenant_id INTEGER NOT NULL,
  role VARCHAR(30) NOT NULL DEFAULT 'viewer',
  created_at DATETIME NOT NULL,
  FOREIGN KEY(tenant_id) REFERENCES tenants(id)
);

CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY,
  tenant_id INTEGER NOT NULL,
  name VARCHAR(120) NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  base_price FLOAT NOT NULL DEFAULT 1000.0,
  is_active BOOLEAN NOT NULL DEFAULT 1,
  config_schema JSON NOT NULL DEFAULT '{}',
  FOREIGN KEY(tenant_id) REFERENCES tenants(id)
);

CREATE TABLE IF NOT EXISTS pricing_rule_sets (
  id INTEGER PRIMARY KEY,
  tenant_id INTEGER UNIQUE NOT NULL,
  rules_json JSON NOT NULL DEFAULT '{}',
  updated_at DATETIME NOT NULL,
  FOREIGN KEY(tenant_id) REFERENCES tenants(id)
);

CREATE TABLE IF NOT EXISTS configurations (
  id INTEGER PRIMARY KEY,
  tenant_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  public_id VARCHAR(80) UNIQUE NOT NULL,
  customer_name VARCHAR(120),
  customer_email VARCHAR(160),
  config_json JSON NOT NULL,
  pricing_snapshot JSON NOT NULL,
  created_at DATETIME NOT NULL,
  FOREIGN KEY(tenant_id) REFERENCES tenants(id),
  FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY,
  tenant_id INTEGER NOT NULL,
  configuration_id INTEGER NOT NULL,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(160) NOT NULL,
  phone VARCHAR(50),
  message TEXT,
  stage VARCHAR(40) NOT NULL DEFAULT 'new',
  internal_notes TEXT NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL,
  FOREIGN KEY(tenant_id) REFERENCES tenants(id),
  FOREIGN KEY(configuration_id) REFERENCES configurations(id)
);

CREATE TABLE IF NOT EXISTS quotes (
  id INTEGER PRIMARY KEY,
  tenant_id INTEGER NOT NULL,
  lead_id INTEGER NOT NULL,
  status VARCHAR(40) NOT NULL DEFAULT 'draft',
  total FLOAT NOT NULL,
  line_items JSON NOT NULL,
  pdf_path VARCHAR(250),
  internal_notes TEXT NOT NULL DEFAULT '',
  created_at DATETIME NOT NULL,
  FOREIGN KEY(tenant_id) REFERENCES tenants(id),
  FOREIGN KEY(lead_id) REFERENCES leads(id)
);

CREATE TABLE IF NOT EXISTS subscriptions (
  id INTEGER PRIMARY KEY,
  tenant_id INTEGER UNIQUE NOT NULL,
  provider VARCHAR(40) NOT NULL DEFAULT 'stripe',
  status VARCHAR(40) NOT NULL DEFAULT 'trialing',
  external_customer_id VARCHAR(120),
  external_subscription_id VARCHAR(120),
  updated_at DATETIME NOT NULL,
  FOREIGN KEY(tenant_id) REFERENCES tenants(id)
);
