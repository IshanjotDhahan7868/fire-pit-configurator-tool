from app.pricing import evaluate_price
from app.schemas import ConfigInput


def test_price_includes_material_and_accessories():
    config = ConfigInput(
        shape="square",
        size_preset="large",
        material="stone",
        finish="charcoal",
        fuel_type="propane",
        burner="linear",
        media="lava_rock",
        ignition="electronic",
        accessories=["cover", "wind_guard"],
    )
    result = evaluate_price(2000, config)
    assert result.total == 2000 + 800 + 950 + 600 + 120 + 180
    assert any(item["label"] == "Material: stone" for item in result.surcharges)
