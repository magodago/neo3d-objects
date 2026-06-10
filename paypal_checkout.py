"""
NEO Objects - PayPal Checkout Backend
======================================
FastAPI server that creates PayPal orders for dynamic cart totals.

Usage:
  1. pip install fastapi uvicorn paypalrestsdk
  2. export PAYPAL_CLIENT_ID="xxx"
  3. export PAYPAL_SECRET="xxx"
  4. python3 paypal_checkout.py
  5. Frontend POSTs to /create-paypal-order

The frontend then captures the order and shows success.
"""

import os
import json
import requests
import base64
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NEO Objects PayPal Checkout")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_SECRET = os.environ.get("PAYPAL_SECRET", "")
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "live")  # "sandbox" for testing

def get_paypal_base():
    return "https://api-m.paypal.com" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com"

def get_access_token():
    """Get PayPal OAuth2 access token"""
    url = f"{get_paypal_base()}/v1/oauth2/token"
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    resp = requests.post(url, headers=headers, data=data, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


@app.get("/health")
def health():
    return {
        "status": "ok",
        "paypal_configured": bool(PAYPAL_CLIENT_ID and PAYPAL_SECRET),
        "mode": PAYPAL_MODE,
    }


@app.post("/create-paypal-order")
async def create_paypal_order(request: Request):
    """
    Create a PayPal order from cart data.

    Request: { "items": [{"name":"...", "price":22, "qty":2}], "shipping": 6 }

    Returns: { "orderID": "xxx" }
    """
    if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
        return JSONResponse(status_code=500, content={"error": "PayPal no configurado. El administrador debe establecer PAYPAL_CLIENT_ID y PAYPAL_SECRET."})

    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "JSON inválido"})

    items = data.get("items", [])
    if not items:
        return JSONResponse(status_code=400, content={"error": "Carrito vacío"})

    # Calculate totals
    subtotal = sum(item.get("price", 0) * item.get("qty", 1) for item in items)
    shipping = data.get("shipping", 0)
    total = subtotal + shipping

    # Build PayPal order items
    paypal_items = []
    for item in items:
        paypal_items.append({
            "name": item.get("name", "Producto NEO"),
            "description": "Impresión 3D Premium",
            "quantity": str(item.get("qty", 1)),
            "unit_amount": {"currency_code": "EUR", "value": f"{item.get('price', 0):.2f}"},
            "category": "PHYSICAL_GOODS",
        })

    if shipping > 0:
        paypal_items.append({
            "name": "Envío a península",
            "description": "Correos / agencia - 24-72h",
            "quantity": "1",
            "unit_amount": {"currency_code": "EUR", "value": f"{shipping:.2f}"},
            "category": "PHYSICAL_GOODS",
        })

    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": f"NEO-{int(__import__('time').time())}",
            "description": "Pedido NEO Objects",
            "items": paypal_items,
            "amount": {
                "currency_code": "EUR",
                "value": f"{total:.2f}",
                "breakdown": {
                    "item_total": {"currency_code": "EUR", "value": f"{subtotal:.2f}"},
                    "shipping": {"currency_code": "EUR", "value": f"{shipping:.2f}"},
                }
            },
        }],
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                    "landing_page": "LOGIN",
                    "user_action": "PAY_NOW",
                    "return_url": data.get("success_url", "https://magodago.github.io/neo3d-objects/success.html"),
                    "cancel_url": data.get("cancel_url", "https://magodago.github.io/neo3d-objects/"),
                }
            }
        }
    }

    try:
        token = get_access_token()
        url = f"{get_paypal_base()}/v2/checkout/orders"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": f"NEO-{int(__import__('time').time())}",
        }
        resp = requests.post(url, headers=headers, json=order_data, timeout=15)
        resp.raise_for_status()
        order = resp.json()
        return {"orderID": order["id"]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error PayPal: {str(e)}"})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8891))
    print(f"\n  🚀 NEO Objects PayPal Checkout API")
    print(f"  📡 http://localhost:{port}")
    print(f"  💳 PayPal: {'✅ Configurado' if PAYPAL_CLIENT_ID else '❌ Sin claves'} | Modo: {PAYPAL_MODE}")
    print()
    uvicorn.run(app, host="0.0.0.0", port=port)
