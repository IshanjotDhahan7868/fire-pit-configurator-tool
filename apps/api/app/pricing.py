from .schemas import ConfigInput, PriceBreakdown

SIZE_PRICING = {
    "small": 0,
    "medium": 350,
    "large": 800,
    "xl": 1200,
}
MATERIAL_PRICING = {
    "steel": 0,
    "corten": 400,
    "concrete": 700,
    "stone": 950,
}
FUEL_PRICING = {
    "wood": 0,
    "propane": 600,
    "natural_gas": 800,
}
ACCESSORY_PRICING = {
    "cover": 120,
    "wind_guard": 180,
    "lid": 90,
    "spark_screen": 150,
    "grate": 130,
}


def evaluate_price(base_price: float, config: ConfigInput) -> PriceBreakdown:
    subtotal = base_price
    surcharges: list[dict[str, float | str]] = []
    notes: list[str] = []

    for label, amount in [
        (f"Size: {config.size_preset}", SIZE_PRICING.get(config.size_preset, 0)),
        (f"Material: {config.material}", MATERIAL_PRICING.get(config.material, 0)),
        (f"Fuel: {config.fuel_type}", FUEL_PRICING.get(config.fuel_type, 0)),
    ]:
        if amount:
            subtotal += amount
            surcharges.append({"label": label, "amount": amount})

    if config.fuel_type == "wood" and config.ignition != "manual":
        notes.append("Wood systems require manual ignition.")

    if config.material == "stone" and config.shape == "round":
        stone_round_surcharge = 300
        subtotal += stone_round_surcharge
        surcharges.append({"label": "Stone round fabrication", "amount": stone_round_surcharge})

    for accessory in config.accessories:
        amount = ACCESSORY_PRICING.get(accessory, 0)
        if amount:
            subtotal += amount
            surcharges.append({"label": f"Accessory: {accessory}", "amount": amount})

    if config.fuel_type in {"propane", "natural_gas"} and config.burner == "none":
        notes.append("Gas configurations require a burner selection.")

    return PriceBreakdown(subtotal=subtotal, surcharges=surcharges, total=subtotal, notes=notes)
