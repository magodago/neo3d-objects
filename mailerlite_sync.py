"""
NEO Objects - MailerLite Lead Sync
Simple script that adds leads to MailerLite group.
Can be called from the command line or used as a module.

Usage:
  python3 mailerlite_sync.py "name" "email" "tienda" "telefono" "tipo"
"""

import os
import sys
import json
import requests
from datetime import datetime

# Read API key from env or .env
API_KEY = os.environ.get("MAILERLITE_API_KEY", "")
if not API_KEY:
    # Try reading from .hermes .env
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("MAILERLITE_API_KEY="):
                    API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

API_URL = "https://connect.mailerlite.com/api/subscribers"
GROUP_ID = os.environ.get("MAILERLITE_GROUP_ID", "")

# CSV path for backup
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leads.csv")


def add_subscriber(name, email, company="", phone="", source="web-form"):
    """Add a subscriber to MailerLite and append to CSV"""
    results = {"mailerlite": False, "csv": False}
    
    # 1. Add to MailerLite
    if API_KEY:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        data = {
            "email": email,
            "name": name,
            "fields": {
                "company": company,
                "phone": phone,
                "source": source,
            },
            "groups": [GROUP_ID] if GROUP_ID else [],
        }
        try:
            resp = requests.post(API_URL, headers=headers, json=data, timeout=10)
            if resp.status_code in (200, 201):
                print(f"  ✅ MailerLite: {email} añadido")
                results["mailerlite"] = True
            elif resp.status_code == 409:
                print(f"  ℹ️  MailerLite: {email} ya existe")
                results["mailerlite"] = True
            else:
                print(f"  ⚠️  MailerLite error {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"  ❌ MailerLite connection error: {e}")
    else:
        print(f"  ⚠️  No MailerLite API key configured")
    
    # 2. Append to CSV
    try:
        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            if not file_exists:
                f.write("Fecha,Nombre,Email,Tienda,Telefono,Tipo,Origen\n")
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
            # Escape CSV fields
            def esc(v):
                v = str(v or "").replace('"', '""')
                return f'"{v}"'
            line = f'{esc(fecha)},{esc(name)},{esc(email)},{esc(company)},{esc(phone)},{esc("")},{esc(source)}\n'
            f.write(line)
        print(f"  ✅ CSV: {email} guardado en leads.csv")
        results["csv"] = True
    except Exception as e:
        print(f"  ❌ CSV error: {e}")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 mailerlite_sync.py 'name' 'email' ['company'] ['phone'] ['source']")
        sys.exit(1)
    
    name = sys.argv[1]
    email = sys.argv[2]
    company = sys.argv[3] if len(sys.argv) > 3 else ""
    phone = sys.argv[4] if len(sys.argv) > 4 else ""
    source = sys.argv[5] if len(sys.argv) > 5 else "web-form"
    
    print(f"\n  📋 Añadiendo lead: {name} <{email}>")
    add_subscriber(name, email, company, phone, source)
    print()
