#!/usr/bin/env python3
"""
NEO Objects — Google Maps Store Scraper v2
Extrae contactos de tiendas de Google Maps con Playwright.
"""
import json, csv, re, time, functools
from pathlib import Path
from playwright.sync_api import sync_playwright

print = functools.partial(print, flush=True)

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
OUTPUT_FILE = OUTPUT_DIR / "google_maps_stores.json"
CSV_FILE = OUTPUT_DIR / "google_maps_stores.csv"

SEARCHES = [
    "floristerías Madrid", "floristerías Alcalá de Henares",
    "floristerías Fuenlabrada", "floristerías Torrejón de Ardoz",
    "floristerías Las Rozas", "floristerías Móstoles", "floristerías Getafe",
    "tiendas de regalos Madrid", "tiendas de regalos Alcalá de Henares",
    "tiendas de regalos Fuenlabrada", "tiendas de regalos Torrejón de Ardoz",
    "tiendas de decoración Madrid", "tiendas de decoración Pozuelo",
    "tiendas de decoración Las Rozas",
]


def scrape_all():
    all_stores = []
    seen_names = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        ctx = browser.new_context(viewport={'width': 1920, 'height': 1080}, locale='es-ES')
        page = ctx.new_page()
        
        # Go to Google Maps
        page.goto("https://www.google.com/maps", timeout=20000)
        page.wait_for_timeout(3000)
        
        # Accept cookies
        cookie_btn = page.query_selector('button:has-text("Aceptar todo"), button:has-text("Rechazar todo"), button:has-text("Accept all"), button:has-text("Aceptar"), button:has-text("Accept")')
        if cookie_btn:
            cookie_btn.click()
            page.wait_for_timeout(2000)
        
        for query in SEARCHES:
            print(f"\n🔍 Buscando: {query}")
            category = "Floristería" if "floristería" in query.lower() else \
                       "Tienda de regalos" if "regalos" in query.lower() else \
                       "Decoración"
            
            try:
                # Search
                search_box = page.query_selector('input[name="q"]')
                if not search_box:
                    search_box = page.query_selector('[aria-label*="Buscar"], [aria-label*="Search"]')
                
                if search_box:
                    search_box.click()
                    search_box.fill("")
                    page.keyboard.type(query, delay=50)
                    page.keyboard.press("Enter")
                else:
                    page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}/", timeout=20000)
                
                page.wait_for_timeout(4000)
                
                # Wait for results panel
                try:
                    page.wait_for_selector('[role="feed"]', timeout=8000)
                except:
                    pass
                
                # Scroll results
                for _ in range(8):
                    page.evaluate('document.querySelector(\'[role="feed"]\')?.scrollBy(0, 800)')
                    page.wait_for_timeout(800)
                
                # Get all result links
                results = page.query_selector_all('[role="feed"] a, a[href*="/place/"]')
                print(f"   Resultados: {len(results)}")
                
                count = 0
                for i, result in enumerate(results):
                    if count >= 30:
                        break
                    
                    try:
                        href = result.get_attribute('href') or ''
                        if '/place/' not in href:
                            continue
                        
                        result.click()
                        page.wait_for_timeout(2000)
                        
                        # Extract data
                        name_el = page.query_selector('h1')
                        name = name_el.inner_text().strip() if name_el else ""
                        
                        if not name or name in seen_names:
                            continue
                        seen_names.add(name)
                        
                        # Phone
                        phone = ""
                        tel_els = page.query_selector_all('a[href^="tel:"]')
                        for el in tel_els:
                            href_attr = el.get_attribute('href') or ''
                            phone = href_attr.replace('tel:', '')
                            phone = re.sub(r'[^\d+]', '', phone)
                            break
                        
                        # Website
                        website = ""
                        web_els = page.query_selector_all('a[href*="://"]:not([href*="google.com"])')
                        for el in web_els:
                            href_attr = el.get_attribute('href') or ''
                            if href_attr and '://' in href_attr and 'google.com' not in href_attr:
                                website = href_attr
                                break
                        
                        # Address
                        address = ""
                        addr_btn = page.query_selector('button[class*="address"]')
                        if addr_btn:
                            address = addr_btn.inner_text().strip()
                        
                        store = {
                            "name": name, "category": category,
                            "phone": phone, "website": website, "address": address,
                            "source": "google_maps"
                        }
                        all_stores.append(store)
                        count += 1
                        
                        has = "📞" if phone else "  "
                        print(f"   [{count}] {name[:35]:35s} {has}")
                        
                        # Save incrementally
                        if count % 10 == 0:
                            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                                json.dump(all_stores, f, indent=2, ensure_ascii=False)
                        
                    except Exception as e:
                        pass
                
            except Exception as e:
                print(f"   ❌ Error en búsqueda: {e}")
            
            time.sleep(2)
        
        browser.close()
    
    # Save final
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_stores, f, indent=2, ensure_ascii=False)
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Teléfono", "Web", "Dirección"])
        for s in all_stores:
            w.writerow([s['name'], s['category'], s.get('phone',''), s.get('website',''), s.get('address','')])
    
    print(f"\n✅ TOTAL: {len(all_stores)} tiendas")
    print(f"📞 Con teléfono: {sum(1 for s in all_stores if s.get('phone'))}")
    print(f"🌐 Con web: {sum(1 for s in all_stores if s.get('website'))}")
    print(f"💾 CSV: {CSV_FILE}")


if __name__ == "__main__":
    scrape_all()
