#!/usr/bin/env python3
"""
NEO Objects — Google Maps Store Scraper v4 (funcional comprobado)
Extrae contactos de tiendas de Google Maps usando los selectores correctos.
"""
import json, csv, re, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
OUTPUT_FILE = OUTPUT_DIR / "gmaps_contacts.json"

SEARCHES = [
    ("floristerías Madrid", "Floristería"),
    ("floristerías Alcalá de Henares", "Floristería"),
    ("floristerías Fuenlabrada", "Floristería"),
    ("floristerías Torrejón de Ardoz", "Floristería"),
    ("floristerías Móstoles", "Floristería"),
    ("floristerías Getafe", "Floristería"),
    ("floristerías Las Rozas", "Floristería"),
    ("floristerías Collado Villalba", "Floristería"),
    ("tiendas de regalos Madrid", "Tienda de regalos"),
    ("tiendas de regalos Alcalá de Henares", "Tienda de regalos"),
    ("tiendas de regalos Fuenlabrada", "Tienda de regalos"),
    ("tiendas de decoración Madrid", "Decoración"),
    ("tiendas de decoración Pozuelo", "Decoración"),
    ("tiendas de decoración Las Rozas", "Decoración"),
    ("tiendas de decoración Majadahonda", "Decoración"),
]


def extract_phone_from_page(page):
    """Extract phone from the open store panel."""
    # Try tel: links
    tel = page.query_selector('a[href^="tel:"]')
    if tel:
        href = tel.get_attribute('href')
        if href:
            return href.replace('tel:', '').strip()
    
    # Try buttons with phone data
    for btn in page.query_selector_all('button'):
        text = btn.inner_text()
        if re.search(r'\d{9}', text):
            nums = re.findall(r'\d{9}', text)
            if nums:
                return nums[0]
    
    return ""


def extract_website_from_page(page):
    """Extract website from the open store panel."""
    for a in page.query_selector_all('a'):
        href = a.get_attribute('href')
        if href and '://' in href and 'google.com' not in href:
            return href
    return ""


def scrape():
    all_stores = []
    seen = set()
    
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--no-sandbox'])
        ctx = browser.new_context(viewport={'width': 1400, 'height': 900}, locale='es-ES')
        page = ctx.new_page()
        
        # Init + accept cookies
        page.goto("https://www.google.com/maps", timeout=15000)
        page.wait_for_timeout(2000)
        for txt in ["Aceptar", "Accept", "Acepto todo", "Rechazar"]:
            try:
                btn = page.query_selector(f'button:has-text("{txt}")')
                if btn: btn.click(); page.wait_for_timeout(500); break
            except: pass
        
        for query, category in SEARCHES:
            print(f"\n🔍 {query}")
            
            try:
                page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}/", timeout=15000)
                page.wait_for_timeout(4000)
                
                # Scroll to load results
                for _ in range(6):
                    page.evaluate('document.querySelector(\'[role="feed"]\')?.scrollBy(0, 600)')
                    page.wait_for_timeout(500)
                
                # Get store cards - correct selector from debug output
                cards = page.query_selector_all('a.hfpxzc')
                print(f"   Tarjetas: {len(cards)}")
                
                count = 0
                for card in cards:
                    if count >= 20:
                        break
                    
                    try:
                        # Get store name from aria-label
                        name = card.get_attribute('aria-label')
                        if not name or name in seen or len(name) < 3:
                            continue
                        
                        seen.add(name)
                        
                        # Click the card
                        card.click()
                        page.wait_for_timeout(1500)
                        
                        phone = extract_phone_from_page(page)
                        website = extract_website_from_page(page)
                        
                        store = {
                            "name": name,
                            "category": category,
                            "phone": phone,
                            "website": website,
                            "source": "google_maps"
                        }
                        all_stores.append(store)
                        count += 1
                        
                        p = "📞" if phone else "  "
                        w = "🌐" if website else "  "
                        print(f"   [{count:2d}] {name[:30]:30s} {p} {w}")
                        
                        if count % 10 == 0:
                            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                                json.dump(all_stores, f, indent=2, ensure_ascii=False)
                    
                    except Exception as e:
                        pass
                
            except Exception as e:
                print(f"   ❌ {e}")
        
        browser.close()
    
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_stores, f, indent=2, ensure_ascii=False)
    
    csv_path = OUTPUT_DIR / "gmaps_contacts.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Teléfono", "Web"])
        for s in all_stores:
            w.writerow([s['name'], s['category'], s.get('phone',''), s.get('website','')])
    
    wp = sum(1 for s in all_stores if s.get('phone'))
    ww = sum(1 for s in all_stores if s.get('website'))
    
    print(f"\n{'='*50}")
    print(f"  ✅ {len(all_stores)} tiendas · 📞{wp} · 🌐{ww}")
    print(f"  💾 {csv_path}")
    
    return all_stores


if __name__ == "__main__":
    scrape()
