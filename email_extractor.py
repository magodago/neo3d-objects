#!/usr/bin/env python3
"""
NEO Objects — Email Extractor
Intenta encontrar emails de contacto para las tiendas encontradas.
1) Extrae emails de las webs de tiendas que ya tienen website
2) Busca en Google por nombre+ciudad para tiendas sin web
"""
import json, re, csv, time, urllib.request, socket, ssl
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter

BASE_DIR = Path.home() / "gema_store" / "neo3d"
INPUT = BASE_DIR / "madrid_stores_raw.json"
OUTPUT = BASE_DIR / "madrid_stores_with_contacts.json"
CSV_OUT = BASE_DIR / "madrid_stores_with_email.csv"
LOG = BASE_DIR / "email_extraction_log.txt"

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'(\+34|0034)?[-\s]?(\d{3}[-\s]?\d{3}[-\s]?\d{3}|\d{9})')

# Skip these generic email domains
SKIP_DOMAINS = {'example.com', 'domain.com', 'yourdomain.com', 'email.com', 'mail.com'}


def fetch_url(url, timeout=15):
    """Fetch a URL and return its text content."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; NEOObjects/2.0; +https://magodago.github.io/neo3d-objects/)'}
        )
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None


def find_emails_in_text(text, store_name=None):
    """Find valid email addresses in text."""
    if not text:
        return []
    emails = set()
    for match in EMAIL_REGEX.finditer(text):
        email = match.group(0).strip().lower()
        # Filter out noise
        if any(skip in email for skip in SKIP_DOMAINS):
            continue
        if email.endswith('.png') or email.endswith('.jpg') or email.endswith('.svg'):
            continue
        if email.startswith('@'):
            continue
        # Must have a valid TLD
        parts = email.split('.')
        if len(parts[-1]) < 2:
            continue
        emails.add(email)
    return list(emails)


def extract_emails_from_website(store):
    """Try to extract email from store's website."""
    website = store.get('website', '')
    if not website:
        return []
    
    # Normalize URL
    if not website.startswith('http'):
        website = 'https://' + website
    
    parsed = urlparse(website)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    all_emails = set()
    
    # Fetch main page
    html = fetch_url(website)
    if html:
        emails = find_emails_in_text(html, store['name'])
        all_emails.update(emails)
    
    # Try /contacto page
    if not all_emails:
        for path in ['/contacto', '/contact', '/contact-us', '/contacto.html']:
            html = fetch_url(base_url + path)
            if html:
                emails = find_emails_in_text(html, store['name'])
                all_emails.update(emails)
                if all_emails:
                    break
            time.sleep(0.5)
    
    return list(all_emails)


def main():
    print("=" * 50)
    print("  NEO Objects — Email Extractor")
    print("=" * 50)
    
    if not INPUT.exists():
        print(f"❌ No se encuentra {INPUT}")
        return
    
    stores = json.load(open(INPUT, 'r', encoding='utf-8'))
    print(f"📥 Cargadas {len(stores)} tiendas")
    
    log_lines = []
    stats = {"total": len(stores), "with_web": 0, "emails_found": 0, "skipped": 0}
    
    for i, store in enumerate(stores, 1):
        name = store['name']
        city = store['city']
        website = store.get('website', '')
        existing_email = store.get('email', '')
        
        # Skip if already has email
        if existing_email:
            stats['emails_found'] += 1
            continue
        
        # Skip stores without website
        if not website:
            stats['skipped'] += 1
            continue
        
        stats['with_web'] += 1
        
        print(f"[{i}/{stats['total']}] {name} ({city})...", end=" ", flush=True)
        
        emails = extract_emails_from_website(store)
        
        if emails:
            store['email'] = emails[0]  # Use first email
            store['emails_all'] = emails
            stats['emails_found'] += 1
            print(f"✅ {emails[0]}")
            log_lines.append(f"{name}|{city}|{emails[0]}|{website}")
        else:
            print("❌ No email found")
        
        # Rate limit
        time.sleep(1)
        
        # Save incrementally every 20 stores
        if i % 20 == 0:
            with open(OUTPUT, 'w', encoding='utf-8') as f:
                json.dump(stores, f, indent=2, ensure_ascii=False)
    
    # Final save
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(stores, f, indent=2, ensure_ascii=False)
    
    # Save log
    with open(LOG, 'w', encoding='utf-8') as f:
        f.write(f"Email Extraction Log\n")
        f.write(f"Total stores: {stats['total']}\n")
        f.write(f"With websites: {stats['with_web']}\n")
        f.write(f"Emails found: {stats['emails_found']}\n")
        f.write(f"Skipped (no web): {stats['skipped']}\n")
        f.write(f"{'='*50}\n")
        for line in log_lines:
            f.write(line + '\n')
    
    # Save CSV
    with_email = [s for s in stores if s.get('email')]
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Ciudad", "Dirección", "Email", "Teléfono", "Web"])
        for s in with_email:
            w.writerow([
                s['name'], s['category'], s['city'],
                s['address'], s['email'], s.get('phone', ''),
                s.get('website', '')
            ])
    
    # Stats
    by_type = Counter(s['category'] for s in with_email)
    print(f"\n{'='*50}")
    print(f"  📊 RESULTADOS FINALES")
    print(f"  Tiendas con email: {len(with_email)}/{stats['total']} ({len(with_email)/stats['total']*100:.1f}%)")
    print(f"  Emails extraídos de webs: {stats['emails_found'] - sum(1 for s in with_email if s.get('_original_email'))}")
    print(f"\n  Por tipo:")
    for t, c in by_type.most_common():
        print(f"    {t}: {c}")
    print(f"\n  CSV: {CSV_OUT}")
    print(f"  JSON: {OUTPUT}")
    print(f"  Log: {LOG}")


if __name__ == "__main__":
    main()
