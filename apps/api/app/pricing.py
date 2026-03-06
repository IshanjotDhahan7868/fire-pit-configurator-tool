from .schemas import ConfigInput, PriceBreakdown

DEFAULT_RULES = {
    "size": {"small": 0, "medium": 350, "large": 800, "xl": 1200},
    "material": {"steel": 0, "corten": 400, "concrete": 700, "stone": 950},
    "fuel": {"wood": 0, "propane": 600, "natural_gas": 800},
    "accessory": {"cover": 120, "wind_guard": 180, "lid": 90, "spark_screen": 150, "grate": 130},
}


def evaluate_price(base_price: float, config: ConfigInput, rules: dict | None = None) -> PriceBreakdown:
    resolved = rules or DEFAULT_RULES
    size_rules = resolved.get("size", {})
    material_rules = resolved.get("material", {})
    fuel_rules = resolved.get("fuel", {})
    accessory_rules = resolved.get("accessory", {})

    subtotal = base_price
    line_items: list[dict[str, float | str]] = [{"label": "Base product", "amount": base_price}]
    notes: list[str] = []

    for label, amount in [
        (f"Size: {config.size_preset}", float(size_rules.get(config.size_preset, 0))),
        (f"Material: {config.material}", float(material_rules.get(config.material, 0))),
        (f"Fuel: {config.fuel_type}", float(fuel_rules.get(config.fuel_type, 0))),
    ]:
        if amount:
            subtotal += amount
            line_items.append({"label": label, "amount": amount})

    if config.fuel_type == "wood" and config.ignition != "manual":
        notes.append("Wood systems require manual ignition.")

    if config.material == "stone" and config.shape == "round":
        stone_round_surcharge = 300.0
        subtotal += stone_round_surcharge
        line_items.append({"label": "Stone round fabrication", "amount": stone_round_surcharge})

    for accessory in config.accessories:
        amount = float(accessory_rules.get(accessory, 0))
        if amount:
            subtotal += amount
            line_items.append({"label": f"Accessory: {accessory}", "amount": amount})

    if config.fuel_type in {"propane", "natural_gas"} and config.burner == "none":
        notes.append("Gas configurations require a burner selection.")

    return PriceBreakdown(subtotal=subtotal, surcharges=line_items[1:], line_items=line_items, total=subtotal, notes=notes)
