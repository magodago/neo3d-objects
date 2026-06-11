#!/usr/bin/env python3
"""
NEO Objects — Scraper masivo de Empresite
Extrae empresas de Madrid por categoría (tiendas de regalos, floristerías, decoración).
Cada perfil puede tener teléfono y web para encontrar email.
"""
import urllib.request, urllib.parse, json, re, csv, time, os, ssl
from pathlib import Path
from collections import defaultdict

OUTPUT = Path.home() / "gema_store" / "neo3d" / "empresite_data.json"
OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"

# Categories to scrape (slug from Empresite URLs)
CATEGORIES = {
    "TIENDAS-DE-REGALOS": "Tienda de regalos",
    "FLORISTERIAS": "Floristería",
    "DECORACION": "Decoración",
    "ARTICULOS-HOGAR": "Hogar",
    "REGALOS-PUBLICIDAD": "Regalos/Publicidad",
    "JOYERIAS": "Joyería",
    "BAZARES": "Bazar",
    "ARTESANIA": "Artesanía",
    "JUGUETES": "Juguetería",
    "LIBRERIAS": "Librería",
}

BASE_URL = "https://empresite.eleconomista.es/Actividad/{cat}/provincia/MADRID/"
PROFILE_URL = "https://empresite.eleconomista.es{path}"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(url, retries=3):
    """Fetch URL with retries."""
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:
            if i < retries - 1:
                time.sleep(2)
            else:
                return None


def extract_company_links(html):
    """Extract company profile links from category page."""
    if not html:
        return []
    # Find links to company profiles
    links = re.findall(r'href="(/[A-Z0-9][^"]*\.html)"[^>]*title="Ver perfil de ([^"]*)"', html)
    # Also find links from cards
    cards = re.findall(r'href="(https://empresite\.eleconomista\.es/[A-Z0-9][^"]*\.html)"', html)
    
    all_links = []
    for path, title in links:
        all_links.append({"path": path, "name": title.strip(), "url": PROFILE_URL.format(path=path)})
    
    return all_links


def get_next_page(html):
    """Get next page URL from pagination."""
    if not html:
        return None
    # Look for "Siguiente" or "›" link
    match = re.search(r'class="[^"]*next[^"]*"[^>]*href="([^"]+)"', html)
    if match:
        return match.group(1)
    # Try alternative pagination pattern
    match = re.search(r'href="(/Actividad/[^"]+)"[^>]*rel="next"', html)
    if match:
        return "https://empresite.eleconomista.es" + match.group(1)
    return None


def extract_profile_data(html, name):
    """Extract contact data from a company profile page."""
    if not html:
        return {}
    
    data = {"name": name, "phone": "", "website": "", "email": "", "address": ""}
    
    # Extract phone
    phone_matches = re.findall(r'(?:\+34|0034)?[-\s]?(\d{9})', html)
    if phone_matches:
        # Filter out non-phone numbers (like dates, IDs)
        valid = [p for p in phone_matches if p[0] in '679' and len(p) == 9]
        if valid:
            data["phone"] = valid[0]
    
    # Extract website
    web_match = re.search(r'https?://(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s"\'<>]*)?', html)
    if web_match:
        url = web_match.group(0)
        # Filter out google/facebook/twitter/etc
        if not any(s in url.lower() for s in ['google.com', 'facebook.com', 'twitter.com', 'youtube.com', 'instagram.com', 'linkedin.com']):
            data["website"] = url
    
    # Extract email (rare in Empresite but worth checking)
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
    if email_match:
        email = email_match.group(0).lower()
        if not any(s in email for s in ['example.com', 'domain.com', '@jpg', '@png']):
            data["email"] = email
    
    # Extract address
    addr_match = re.search(r'(?:Calle|Av\.?|Plaza|Carrer|Paseo|Ronda)[^<,]{10,100}', html)
    if addr_match:
        data["address"] = addr_match.group(0).strip()
    
    return data


def scrape_category(cat_slug, cat_name, max_pages=5):
    """Scrape all companies in a category, paginating."""
    print(f"\n📂 {cat_name} ({cat_slug})")
    
    url = BASE_URL.format(cat=cat_slug)
    all_companies = []
    
    for page in range(max_pages):
        print(f"   Página {page+1}...", end=" ", flush=True)
        html = fetch(url)
        
        if not html:
            print("❌ No response")
            break
        
        # Extract company links
        links = extract_company_links(html)
        print(f"{len(links)} empresas encontradas")
        
        for link in links:
            all_companies.append(link)
        
        # Get next page
        next_url = get_next_page(html)
        if not next_url or next_url == url:
            break
        url = next_url
        time.sleep(1)
    
    print(f"   Total: {len(all_companies)} empresas")
    
    # Now visit each profile for contact details
    print(f"   Extrayendo datos de contacto...")
    companies_with_data = []
    
    for i, company in enumerate(all_companies):
        if i % 10 == 0:
            print(f"      {i}/{len(all_companies)}...", flush=True)
        
        html = fetch(company["url"])
        profile = extract_profile_data(html, company["name"])
        profile["category"] = cat_name
        profile["source_url"] = company["url"]
        companies_with_data.append(profile)
        
        time.sleep(0.5)
    
    return companies_with_data


def main():
    print("=" * 50)
    print("  NEO Objects — Scraper Empresite Madrid")
    print("=" * 50)
    
    all_data = []
    
    for cat_slug, cat_name in CATEGORIES.items():
        companies = scrape_category(cat_slug, cat_name, max_pages=3)
        all_data.extend(companies)
        
        # Save incrementally
        with open(OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    # Stats
    with_phone = sum(1 for c in all_data if c.get('phone'))
    with_web = sum(1 for c in all_data if c.get('website'))
    with_email = sum(1 for c in all_data if c.get('email'))
    
    print(f"\n{'='*50}")
    print(f"  📊 TOTAL: {len(all_data)} empresas")
    print(f"  📞 Con teléfono: {with_phone}")
    print(f"  🌐 Con web: {with_web}")
    print(f"  📧 Con email: {with_email}")
    
    # Save CSV
    csv_path = OUTPUT_DIR / "empresite_contacts.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Teléfono", "Web", "Email", "Dirección"])
        for c in all_data:
            w.writerow([c['name'], c['category'], c.get('phone',''), c.get('website',''), c.get('email',''), c.get('address','')])
    
    print(f"  💾 CSV: {csv_path}")
    print(f"  💾 JSON: {OUTPUT}")


if __name__ == "__main__":
    main()
