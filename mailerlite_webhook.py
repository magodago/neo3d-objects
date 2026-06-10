"""
NEO Objects - MailerLite Webhook Server
Receives lead data from the web form and adds to MailerLite + CSV.
Start: python3 mailerlite_webhook.py
Then update index.html to POST to http://localhost:8892/add-lead
"""

import os, json, csv
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# MailerLite config
ML_API_KEY = ""
ML_API_URL = "https://connect.mailerlite.com/api/subscribers"
GROUP_ID = os.environ.get("MAILERLITE_GROUP_ID", "")

# CSV path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "leads.csv")


@app.post("/add-lead")
async def add_lead(request: Request):
    try:
        data = await request.json()
    except:
        return {"status": "error", "message": "JSON invalido"}
    
    name = data.get("name", "")
    email = data.get("email", "")
    company = data.get("company", data.get("tienda", ""))
    phone = data.get("phone", data.get("telefono", ""))
    source = data.get("source", "web-form")
    tipo = data.get("tipo", "")
    
    if not email:
        return {"status": "error", "message": "Email requerido"}
    
    results = {"mailerlite": False, "csv": False}
    
    # 1. MailerLite
    if ML_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {ML_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            payload = {
                "email": email,
                "name": name,
                "fields": {
                    "company": company,
                    "phone": phone,
                    "source": source,
                    "tipo_negocio": tipo,
                },
                "groups": [GROUP_ID] if GROUP_ID else [],
            }
            resp = requests.post(ML_API_URL, headers=headers, json=payload, timeout=10)
            if resp.status_code in (200, 201):
                results["mailerlite"] = True
            elif resp.status_code == 409:
                results["mailerlite"] = True  # ya existe
        except Exception as e:
            print(f"MailerLite error: {e}")
    
    # 2. CSV backup
    try:
        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Fecha", "Nombre", "Email", "Tienda", "Telefono", "Tipo", "Origen"])
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                name, email, company, phone, tipo, source
            ])
        results["csv"] = True
    except Exception as e:
        print(f"CSV error: {e}")
    
    return {"status": "ok", "results": results}


@app.get("/health")
def health():
    has_key = bool(ML_API_KEY)
    csv_exists = os.path.exists(CSV_PATH)
    csv_count = 0
    if csv_exists:
        with open(CSV_PATH) as f:
            csv_count = sum(1 for _ in f) - 1  # minus header
    return {
        "status": "ok",
        "mailerlite": has_key,
        "leads_csv": csv_exists,
        "leads_count": max(0, csv_count),
    }


@app.get("/leads")
def get_leads(limit: int = 100):
    """Return latest leads from CSV"""
    if not os.path.exists(CSV_PATH):
        return {"leads": []}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    return {"leads": leads[-limit:]}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8892))
    print(f"\n  NEO Objects - Lead Sync API")
    print(f"  Port: {port}")
    print(f"  MailerLite: {'Configurado' if ML_API_KEY else 'SIN API KEY'}")
    print(f"  CSV: {CSV_PATH}")
    print()
    uvicorn.run(app, host="0.0.0.0", port=port)
