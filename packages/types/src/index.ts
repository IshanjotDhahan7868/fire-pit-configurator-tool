export type TenantRole = "owner" | "admin" | "sales" | "viewer";

export interface PricingSnapshot {
  subtotal: number;
  total: number;
  notes: string[];
}
