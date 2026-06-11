#!/usr/bin/env python3
"""
NEO Objects — Google Maps Store Scraper
Usa Playwright para extraer datos de contacto de tiendas en Google Maps.
"""
import json, csv, re, time, os
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
OUTPUT_FILE = OUTPUT_DIR / "google_maps_stores.json"
CSV_FILE = OUTPUT_DIR / "google_maps_stores.csv"

# Categories to search in Madrid
SEARCHES = [
    ("floristerías Madrid", "Floristería"),
    ("tiendas de regalos Madrid", "Tienda de regalos"),
    ("tiendas de decoración Madrid", "Decoración"),
    ("jugueterías Madrid", "Juguetería"),
    ("tiendas de hogar Madrid", "Hogar"),
    ("floristerías Alcalá de Henares", "Floristería"),
    ("floristerías Fuenlabrada", "Floristería"),
    ("floristerías Torrejón de Ardoz", "Floristería"),
    ("floristerías Las Rozas", "Floristería"),
    ("floristerías Collado Villalba", "Floristería"),
    ("floristerías Móstoles", "Floristería"),
    ("floristerías Getafe", "Floristería"),
    ("tiendas de regalos Alcalá de Henares", "Tienda de regalos"),
    ("tiendas de decoración Pozuelo", "Decoración"),
]


def extract_contact(page):
    """Extract contact info from the currently open Google Maps place panel."""
    info = {"phone": "", "website": "", "address": "", "name": ""}
    
    try:
        # Name
        name_el = page.query_selector('h1')
        if name_el:
            info["name"] = name_el.inner_text()
        
        # Phone - look for buttons with phone numbers
        phone_els = page.query_selector_all('[data-tooltip*="teléfono"], [data-tooltip*="phone"], [aria-label*="teléfono"], [aria-label*="phone"]')
        for el in phone_els:
            text = el.get_attribute('aria-label') or el.get_attribute('data-tooltip') or ''
            phone = re.search(r'(\+34\s*)?\d{9}', text)
            if phone:
                info["phone"] = phone.group(0)
                break
        
        # Also check for phone links
        if not info["phone"]:
            tel_links = page.query_selector_all('a[href^="tel:"]')
            for link in tel_links:
                href = link.get_attribute('href', '')
                info["phone"] = href.replace('tel:', '')
                break
        
        # Website
        web_els = page.query_selector_all('a[href^="http"]:not([href*="google.com"]):not([href*="maps.google"])')
        for el in web_els:
            href = el.get_attribute('href', '')
            if href and 'http' in href and not any(x in href for x in ['google.com/maps', 'maps.google']):
                info["website"] = href
                break
        
        # Address
        addr_el = page.query_selector('[class*="address"], button[class*="address"]')
        if addr_el:
            info["address"] = addr_el.inner_text()
        
    except Exception as e:
        pass
    
    return info


def scrape_category(page, search_query, category, max_stores=50):
    """Search Google Maps and extract store contacts."""
    print(f"\n🔍 Buscando: {search_query}")
    
    stores = []
    
    try:
        # Navigate to Google Maps
        page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}/", 
                  timeout=30000, wait_until='domcontentloaded')
        time.sleep(3)
        
        # Wait for results panel
        try:
            page.wait_for_selector('div[role="feed"]', timeout=10000)
        except:
            try:
                page.wait_for_selector('a[href*="place"], [class*="result"]', timeout=5000)
            except:
                print("   ⚠ No se encontraron resultados")
                return stores
        
        # Scroll to load more results
        for scroll in range(5):
            page.evaluate('document.querySelector(\'div[role="feed"]\')?.scrollBy(0, 500)')
            time.sleep(1)
        
        # Get all result items
        results = page.query_selector_all('a[href*="place"]')
        print(f"   Resultados encontrados: {len(results)}")
        
        visited = set()
        
        for i, result in enumerate(results[:max_stores]):
            try:
                # Click to open place panel
                result.click()
                time.sleep(2)
                
                # Extract contact info
                info = extract_contact(page)
                
                if info["name"] and info["name"] not in visited:
                    visited.add(info["name"])
                    info["category"] = category
                    info["source"] = "google_maps"
                    stores.append(info)
                    
                    has_phone = "📞" if info["phone"] else "  "
                    has_web = "🌐" if info["website"] else "  "
                    print(f"   [{len(stores)}] {info['name']} {has_phone} {has_web}")
                    
                    # Save incrementally
                    if len(stores) % 10 == 0:
                        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                            json.dump(stores, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                pass
        
        time.sleep(2)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return stores


def main():
    print("=" * 50)
    print("  NEO — Google Maps Store Scraper")
    print("=" * 50)
    
    all_stores = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )
        page = context.new_page()
        
        # First navigate to google to accept cookies if needed
        page.goto("https://www.google.com/maps", timeout=20000)
        time.sleep(2)
        
        for search_query, category in SEARCHES:
            stores = scrape_category(page, search_query, category)
            all_stores.extend(stores)
            
            # Save after each category
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_stores, f, indent=2, ensure_ascii=False)
        
        browser.close()
    
    # Final stats
    with_phone = sum(1 for s in all_stores if s.get('phone'))
    with_web = sum(1 for s in all_stores if s.get('website'))
    
    print(f"\n{'='*50}")
    print(f"  📊 TOTAL: {len(all_stores)} tiendas extraídas")
    print(f"  📞 Con teléfono: {with_phone}")
    print(f"  🌐 Con web: {with_web}")
    
    # Save CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Teléfono", "Web", "Dirección"])
        for s in all_stores:
            w.writerow([s.get('name',''), s.get('category',''), 
                       s.get('phone',''), s.get('website',''), s.get('address','')])
    
    print(f"  💾 CSV: {CSV_FILE}")
    print(f"  💾 JSON: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
