export type RuleInput = {
  basePrice: number;
  surcharges: { label: string; amount: number }[];
};

export function calculateTotal(input: RuleInput) {
  return input.basePrice + input.surcharges.reduce((sum, item) => sum + item.amount, 0);
}
