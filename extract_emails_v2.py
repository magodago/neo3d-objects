#!/usr/bin/env python3
"""
NEO Objects — Email extractor from websites
Toma el CSV de google_maps_stores.csv, visita cada web y extrae emails de contacto.
"""
import json, csv, re, time, functools
from pathlib import Path
from urllib.parse import urlparse
import requests

print = functools.partial(print, flush=True)

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
INPUT_CSV = OUTPUT_DIR / "google_maps_stores.csv"
OUTPUT_JSON = OUTPUT_DIR / "stores_with_emails.json"
OUTPUT_CSV = OUTPUT_DIR / "stores_with_emails.csv"

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
BLOCKED_DOMAINS = {'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'x.com',
                   'instagram.com', 'linkedin.com', 'pinterest.com', 'tiktok.com',
                   'youtu.be', 'wa.me', 'api.whatsapp.com'}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
}


def extract_emails_from_url(url, timeout=10):
    """Visit a URL and extract email addresses."""
    if not url or not url.startswith('http'):
        return set()
    
    domain = urlparse(url).netloc.lower()
    # Skip social media / known non-email sites
    if any(b in domain for b in BLOCKED_DOMAINS):
        return set()
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code != 200:
            return set()
        
        emails = set(EMAIL_REGEX.findall(r.text))
        
        # Filter out false positives
        valid = set()
        for e in emails:
            local, dom = e.split('@')
            dom = dom.lower()
            # Skip generic/no-reply, image extensions, common false positives
            if local in ('user', 'username', 'yourname', 'name', 'email', 'mail',
                         'example', 'test', 'admin', 'root', 'webmaster',
                         'noreply', 'no-reply', 'notifications', 'nobody',
                         'info', 'contact', 'hello', 'hola', 'hi', 'support',
                         'facebook', 'twitter', 'instagram'):
                continue
            if any(skip in dom for skip in BLOCKED_DOMAINS):
                continue
            if dom.count('.') < 1:
                continue
            valid.add(e.lower())
        
        return valid
    except Exception:
        return set()


def main():
    # Read stores from CSV
    stores = []
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Nombre', '').strip()
                website = row.get('Web', '').strip()
                phone = row.get('Teléfono', '').strip()
                category = row.get('Categoría', '').strip()
                if name:
                    stores.append({
                        'name': name, 'website': website,
                        'phone': phone, 'category': category,
                        'emails': []
                    })
    except FileNotFoundError:
        print(f"❌ No se encuentra {INPUT_CSV}. Ejecuta primero scrape_maps_v3.py")
        return
    
    print(f"📊 {len(stores)} tiendas cargadas")
    print(f"🌐 Con web: {sum(1 for s in stores if s['website'])}")
    
    # Process each store with a website
    with_web = [s for s in stores if s['website']]
    print(f"\n🔍 Extrayendo emails de {len(with_web)} webs...\n")
    
    for i, store in enumerate(with_web, 1):
        url = store['website']
        emails = extract_emails_from_url(url)
        store['emails'] = sorted(emails)
        
        has_email = "📧" if emails else "  "
        email_str = ', '.join(list(emails)[:3])
        print(f"   [{i}/{len(with_web)}] {store['name'][:30]:30s} {has_email} {email_str}")
        
        # Rate limit: be nice to servers
        time.sleep(1.5)
        
        # Save incrementally
        if i % 20 == 0:
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(stores, f, indent=2, ensure_ascii=False)
    
    # Save final
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(stores, f, indent=2, ensure_ascii=False)
    
    # CSV with emails
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Teléfono", "Web", "Email", "Todos los emails"])
        for s in stores:
            w.writerow([s['name'], s['category'], s['phone'],
                       s['website'], s['emails'][0] if s['emails'] else '',
                       '; '.join(s['emails'])])
    
    with_email = sum(1 for s in stores if s['emails'])
    total_emails = sum(len(s['emails']) for s in stores)
    
    print(f"\n{'='*50}")
    print(f"✅ {len(stores)} tiendas procesadas")
    print(f"📧 Con email: {with_email}")
    print(f"📨 Total emails únicos: {total_emails}")
    print(f"💾 JSON: {OUTPUT_JSON}")
    print(f"💾 CSV: {OUTPUT_CSV}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
