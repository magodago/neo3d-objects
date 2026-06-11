#!/usr/bin/env python3
"""
NEO Objects — Email Finder Masivo
Usa cloudscraper + Google + directorios para encontrar emails de tiendas.
Estrategias: 
1. Búsqueda directa en Google (store name + city + email)
2. Directorios específicos
3. Páginas Amarillas con cloudscraper
"""
import json, csv, re, time, os
from pathlib import Path
from urllib.parse import quote_plus

import cloudscraper
from bs4 import BeautifulSoup

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
OSM_FILE = OUTPUT_DIR / "madrid_stores_raw.json"
OUTPUT_FILE = OUTPUT_DIR / "madrid_stores_with_contacts_v2.json"
CSV_FILE = OUTPUT_DIR / "madrid_stores_emails_v2.csv"

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

# Load OSM stores
stores = json.load(open(OSM_FILE))
print(f"📥 Cargadas {len(stores)} tiendas de OSM")

# ─── Strategy 1: Search Google for each store's contact info ───
def search_store_google(name, city):
    """Search for store contact info using DuckDuckGo's HTML interface."""
    query = f'"{name}" {city} Madrid email contacto'
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        r = scraper.get(url, timeout=15)
        if r.status_code != 200:
            return None
        
        soup = BeautifulSoup(r.text, 'lxml')
        results = []
        
        for result in soup.select('.result') or soup.select('.result__body'):
            snippet_el = result.select_one('.result__snippet') or result.select_one('.snippet')
            link_el = result.select_one('a.result__a') or result.select_one('a')
            
            if snippet_el:
                text = snippet_el.get_text()
                # Extract email
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                phone = re.findall(r'(?:\+34)?[-\s]?(\d{9})', text)
                
                if emails:
                    return {
                        "email": emails[0],
                        "snippet": text[:200],
                    }
        
        # Also check for website links
        for a in soup.select('a[href^="http"]'):
            href = a.get('href', '')
            # DuckDuckGo wraps URLs
            if 'uddg=' in href:
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                if 'uddg' in parsed:
                    href = parsed['uddg'][0]
            
            if any(s in href.lower() for s in ['.es', '.com', '.org']) and \
               not any(s in href.lower() for s in ['google.com', 'facebook.com', 'twitter.com', 'instagram.com']):
                # Try to fetch the website for email
                try:
                    r2 = scraper.get(href, timeout=10)
                    if r2.status_code == 200:
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r2.text)
                        valid = [e for e in emails if not any(x in e for x in ['example.com', 'domain.com', '.png', '.jpg'])]
                        if valid:
                            return {"email": valid[0], "website": href, "source": "website"}
                except:
                    pass
        
        return None
    except Exception as e:
        return None


# ─── Strategy 2: Try Páginas Amarillas with cloudscraper ───
def search_paginas_amarillas(category, city="Madrid"):
    """Search Páginas Amarillas for stores with contact info."""
    # Try different subdomains/formats
    urls = [
        f"https://www.paginasamarillas.es/a/{category}/{city}/",
        f"https://www.paginasamarillas.es/buscar/{category}/madrid/",
    ]
    
    for url in urls:
        try:
            r = scraper.get(url, timeout=20)
            if r.status_code == 200 and len(r.text) > 1000:
                soup = BeautifulSoup(r.text, 'lxml')
                stores_found = []
                
                # Extract store cards
                for card in soup.select('[class*="anuncio"]') or soup.select('[class*="resultado"]') or soup.select('article'):
                    name_el = card.select_one('h2, h3, [class*="nombre"], [class*="title"], a[class*="nombre"]')
                    if not name_el:
                        continue
                    
                    name = name_el.get_text(strip=True)
                    if not name or len(name) < 3:
                        continue
                    
                    store = {"name": name, "phone": "", "email": "", "website": ""}
                    
                    # Phone
                    phone_el = card.select_one('[class*="telefono"], [href^="tel:"]')
                    if phone_el:
                        store["phone"] = phone_el.get_text(strip=True) or phone_el.get('href', '').replace('tel:', '')
                    
                    # Email (rare in PA but check anyway)
                    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', str(card))
                    if email_match:
                        store["email"] = email_match.group(0)
                    
                    # Website
                    web_el = card.select_one('[href^="http"]:not([href*="paginasamarillas"])')
                    if web_el:
                        store["website"] = web_el.get('href', '')
                    
                    stores_found.append(store)
                
                if stores_found:
                    return stores_found
            
            time.sleep(2)
        except:
            continue
    
    return None


# ─── Process stores ───
def find_emails():
    # First, categorize stores by type for PA search
    categories_to_search = {
        "Floristería": "floristerias",
        "Tienda de regalos": "tiendas-de-regalos",
        "Decoración": "decoracion",
        "Hogar": "articulos-de-hogar",
    }
    
    all_stores = {}
    for s in stores:
        key = f"{s['name']}|{s['city']}"
        all_stores[key] = s
    
    emails_found = 0
    
    # For each category, search PA for stores
    for cat_name, pa_cat in categories_to_search.items():
        print(f"\n🔍 Buscando {cat_name} en Páginas Amarillas...")
        pa_stores = search_paginas_amarillas(pa_cat)
        
        if pa_stores:
            print(f"   Encontradas {len(pa_stores)} tiendas")
            
            # Try to match with our OSM data
            for pa_store in pa_stores:
                name = pa_store["name"].lower().strip()
                
                # Find matching OSM store
                for key, osm_store in all_stores.items():
                    osm_name = osm_store["name"].lower().strip()
                    
                    # Fuzzy match
                    if (name in osm_name or osm_name in name) and \
                       osm_store["category"] == cat_name:
                        
                        # Add contact info if not already present
                        if pa_store.get("email") and not osm_store.get("email"):
                            osm_store["email"] = pa_store["email"]
                            osm_store["source"] = "paginas_amarillas"
                            emails_found += 1
                            print(f"   ✅ {osm_store['name']}: {pa_store['email']}")
                        
                        if pa_store.get("phone") and not osm_store.get("phone"):
                            osm_store["phone"] = pa_store["phone"]
                        
                        if pa_store.get("website") and not osm_store.get("website"):
                            osm_store["website"] = pa_store["website"]
    
    # For remaining stores without email, try Google search
    no_email = [s for s in stores if not s.get('email')]
    print(f"\n🔍 Buscando {len(no_email)} tiendas sin email vía Google...")
    
    for i, store in enumerate(no_email):
        if i >= 50:  # Limit to 50 searches for now
            print(f"   Límite alcanzado ({i} búsquedas)")
            break
        
        name = store['name']
        city = store['city']
        
        print(f"   [{i+1}/50] {name} ({city})...", end=" ", flush=True)
        
        result = search_store_google(name, city)
        if result and result.get("email"):
            store["email"] = result["email"]
            store["source"] = "google"
            emails_found += 1
            print(f"✅ {result['email']}")
        else:
            print("❌")
        
        time.sleep(1)  # Rate limit
    
    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(stores, f, indent=2, ensure_ascii=False)
    
    with_email = [s for s in stores if s.get('email')]
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Ciudad", "Email", "Teléfono", "Web", "Dirección", "Fuente"])
        for s in with_email:
            w.writerow([
                s['name'], s['category'], s['city'],
                s.get('email', ''), s.get('phone', ''), s.get('website', ''),
                s.get('address', ''), s.get('source', 'osm')
            ])
    
    print(f"\n{'='*50}")
    print(f"  📊 RESULTADOS FINALES")
    print(f"  Total tiendas: {len(stores)}")
    print(f"  Con email: {len(with_email)} ({len(with_email)/len(stores)*100:.1f}%)")
    print(f"  Emails nuevos: {emails_found}")
    print(f"  CSV: {CSV_FILE}")


if __name__ == "__main__":
    find_emails()
