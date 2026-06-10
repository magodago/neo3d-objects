"""
NEO Objects - Stripe Checkout Backend
======================================
FastAPI server that creates Stripe Checkout Sessions.

Usage:
  1. Set STRIPE_SECRET_KEY env var
  2. python3 stripe_checkout.py
  3. Frontend POSTs to /create-checkout-session

Requires: pip install stripe fastapi uvicorn
"""

import os
import json
import stripe
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NEO Objects Checkout")

# Allow requests from GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")


@app.get("/health")
def health():
    """Health check endpoint"""
    has_key = bool(stripe.api_key)
    return {
        "status": "ok",
        "stripe_configured": has_key,
        "message": "NEO Objects Checkout API running"
    }


@app.post("/create-checkout-session")
async def create_checkout(request: Request):
    """
    Create a Stripe Checkout Session from cart data.

    Request body:
    {
        "items": [
            {"name": "Jarrón Espiral", "price": 22, "qty": 2},
            {"name": "Macetero Geo", "price": 14, "qty": 1}
        ],
        "success_url": "https://magodago.github.io/neo3d-objects/success.html",
        "cancel_url": "https://magodago.github.io/neo3d-objects/",
        "customer_email": "cliente@email.com"
    }

    Returns:
    {
        "url": "https://checkout.stripe.com/pay/..."
    }
    """
    if not stripe.api_key:
        return JSONResponse(
            status_code=500,
            content={"error": "Stripe no configurado. El administrador debe establecer STRIPE_SECRET_KEY."}
        )

    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "JSON inválido"})

    items = data.get("items", [])
    if not items:
        return JSONResponse(status_code=400, content={"error": "Carrito vacío"})

    # Build Stripe line_items
    line_items = []
    for item in items:
        line_items.append({
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": item.get("name", "Producto NEO Objects"),
                    "description": f"Impresión 3D Premium - {item.get('category', 'Decoración')}",
                },
                "unit_amount": int(round(item.get("price", 0) * 100)),  # cents
            },
            "quantity": item.get("qty", 1),
        })

    # Add shipping as a line item if applicable
    shipping = data.get("shipping", 0)
    if shipping > 0:
        line_items.append({
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": "Envío a península",
                    "description": "Correos / agencia - 24-72h",
                },
                "unit_amount": int(round(shipping * 100)),
            },
            "quantity": 1,
        })

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=data.get("success_url", "https://magodago.github.io/neo3d-objects/success.html?session_id={CHECKOUT_SESSION_ID}"),
            cancel_url=data.get("cancel_url", "https://magodago.github.io/neo3d-objects/"),
            customer_email=data.get("customer_email"),
            shipping_address_collection={
                "allowed_countries": ["ES"],
            },
            phone_number_collection={"enabled": True},
            billing_address_collection="required",
            locale="es",
        )

        return {"url": session.url}

    except stripe.error.StripeError as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Error de Stripe: {str(e)}"}
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8890))
    print(f"\n  🚀 NEO Objects Checkout API")
    print(f"  📡 http://localhost:{port}")
    print(f"  💳 Stripe: {'✅ Configurado' if stripe.api_key else '❌ Sin clave - pon STRIPE_SECRET_KEY'}")
    print()
    uvicorn.run(app, host="0.0.0.0", port=port)
