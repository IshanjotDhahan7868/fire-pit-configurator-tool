from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_happy_path_configuration_to_quote():
    tenant = client.get("/public/tenant/ember-outdoor")
    assert tenant.status_code == 200

    products = client.get("/public/tenant/ember-outdoor/products")
    product_id = products.json()[0]["id"]

    payload = {
        "tenant_slug": "ember-outdoor",
        "product_id": product_id,
        "config": {
            "shape": "round",
            "size_preset": "medium",
            "material": "corten",
            "finish": "rust",
            "fuel_type": "wood",
            "burner": "none",
            "media": "lava_rock",
            "ignition": "manual",
            "accessories": ["spark_screen"],
        },
    }

    priced = client.post("/public/pricing", json=payload)
    assert priced.status_code == 200

    saved = client.post("/public/configurations", json=payload)
    assert saved.status_code == 200
    public_id = saved.json()["public_id"]

    quote = client.post(
        "/public/quote-request",
        json={
            "configuration_public_id": public_id,
            "name": "Test Buyer",
            "email": "buyer@example.com",
            "message": "Need install timeline",
        },
    )
    assert quote.status_code == 200
    assert quote.json()["quote_id"] > 0
