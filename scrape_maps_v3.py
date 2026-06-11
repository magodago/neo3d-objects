#!/usr/bin/env python3
"""
NEO Objects — Google Maps Store Scraper v3
Extrae contactos de tiendas de Google Maps con Playwright.
Estrategia: 1) busca y extrae todas las URLs de /place/ 2) visita cada una y extrae teléfono/web
"""
import json, csv, re, time, functools
from pathlib import Path

from playwright.sync_api import sync_playwright

print = functools.partial(print, flush=True)

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
JSON_FILE = OUTPUT_DIR / "google_maps_stores.json"
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


def get_stores_from_search(page, query):
    """Search Google Maps and return list of {name, href} from the feed."""
    try:
        page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}/", timeout=20000)
        page.wait_for_timeout(3000)

        # Accept consent if needed
        btn = page.query_selector('button:has-text("Aceptar todo"), button:has-text("Rechazar todo")')
        if btn:
            btn.click()
            page.wait_for_timeout(2000)

        # Wait for feed
        try:
            page.wait_for_selector('[role="feed"]', timeout=8000)
        except Exception:
            return 0, []

        # Scroll to load results
        for _ in range(8):
            page.evaluate('document.querySelector("[role=feed]")?.scrollBy(0, 800)')
            page.wait_for_timeout(600)

        # Extract all store cards via JS
        data = page.evaluate("""() => {
            const cards = document.querySelectorAll('[role="feed"] a[href*="/place/"]');
            const results = [];
            const seen = new Set();
            cards.forEach(a => {
                const href = a.getAttribute('href');
                const ariaLabel = a.getAttribute('aria-label') || '';
                let name = '';
                if (ariaLabel) {
                    name = ariaLabel.split('·')[0].trim();
                } else {
                    const spans = a.querySelectorAll('span');
                    spans.forEach(s => { if (s.innerText && !name) name = s.innerText.trim(); });
                }
                if (!name || seen.has(name) || name.length < 2) return;
                seen.add(name);
                results.push({ name, href: href || '' });
            });
            return JSON.stringify(results);
        }""")
        stores = json.loads(data)
        return len(stores), stores
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0, []


def scrape_store_details(page, href):
    """Visit a place page and extract phone + website."""
    try:
        if href.startswith('/'):
            href = 'https://www.google.com' + href

        # Use the URL directly (faster than clicking)
        page.goto(href, timeout=20000)
        page.wait_for_timeout(1500)

        phone = ""
        tel_els = page.query_selector_all('a[href^="tel:"]')
        for el in tel_els:
            phone = el.get_attribute('href') or ''
            phone = phone.replace('tel:', '')
            phone = re.sub(r'[^\d+]', '', phone)
            if phone:
                break

        website = ""
        web_els = page.query_selector_all('a[href*="://"]:not([href*="google.com"]):not([href*="tel:"]):not([href*="maps"]):not([href*="youtube"]):not([href*="blogger"])')
        for el in web_els:
            href_attr = el.get_attribute('href') or ''
            if href_attr and '://' in href_attr and 'google.com' not in href_attr:
                # Skip Google product links
                if any(skip in href_attr for skip in ['google.es/intl', 'policies.google', 'support.google']):
                    continue
                website = href_attr
                break

        # Get address
        address = ""
        addr_els = page.query_selector_all('[class*="address"], button[class*="address"]')
        for el in addr_els:
            text = el.inner_text().strip()
            if text and len(text) > 10:
                address = text
                break

        return phone, website, address
    except Exception as e:
        return "", "", ""


def scrape_all():
    all_stores = []
    seen_phones = set()
    seen_websites = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        ctx = browser.new_context(viewport={'width': 1920, 'height': 1080}, locale='es-ES')
        page = ctx.new_page()

        # Phase 1: collect all store URLs from all searches
        all_hrefs = {}  # href -> {name, category, query}
        for query in SEARCHES:
            category = "Floristería" if "floristería" in query.lower() else \
                       "Tienda de regalos" if "regalos" in query.lower() else "Decoración"
            print(f"\n🔍 Buscando: {query}")
            count, stores = get_stores_from_search(page, query)
            print(f"   Resultados: {count}")
            for s in stores:
                if s['href'] not in all_hrefs:
                    all_hrefs[s['href']] = {
                        'name': s['name'], 'category': category, 'query': query,
                        'phone': '', 'website': '', 'address': ''
                    }
            print(f"   Únicas acumuladas: {len(all_hrefs)}")

        print(f"\n{'='*50}")
        print(f"📊 TOTAL ÚNICAS: {len(all_hrefs)} tiendas")
        print(f"{'='*50}")

        # Phase 2: visit each store page for details
        hrefs_list = list(all_hrefs.items())
        for i, (href, store) in enumerate(hrefs_list, 1):
            phone, website, address = scrape_store_details(page, href)
            store['phone'] = phone
            store['website'] = website
            store['address'] = address

            has_phone = "📞" if phone else "  "
            has_web = "🌐" if website else "  "
            print(f"   [{i}/{len(hrefs_list)}] {store['name'][:35]:35s} {has_phone} {has_web}")

            # Save incrementally every 10
            if i % 10 == 0:
                flat = [{
                    'name': v['name'], 'category': v['category'],
                    'phone': v['phone'], 'website': v['website'], 'address': v['address'],
                    'source': 'google_maps'
                } for v in all_hrefs.values()]
                with open(JSON_FILE, 'w', encoding='utf-8') as f:
                    json.dump(flat, f, indent=2, ensure_ascii=False)

        browser.close()

    # Save final
    flat = [{
        'name': v['name'], 'category': v['category'],
        'phone': v['phone'], 'website': v['website'], 'address': v['address'],
        'source': 'google_maps'
    } for v in all_hrefs.values()]

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(flat, f, indent=2, ensure_ascii=False)

    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Teléfono", "Web", "Dirección"])
        for s in flat:
            w.writerow([s['name'], s['category'], s['phone'], s['website'], s['address']])

    with_phone = sum(1 for s in flat if s.get('phone'))
    with_web = sum(1 for s in flat if s.get('website'))

    print(f"\n{'='*50}")
    print(f"✅ TOTAL: {len(flat)} tiendas")
    print(f"📞 Con teléfono: {with_phone}")
    print(f"🌐 Con web: {with_web}")
    print(f"💾 JSON: {JSON_FILE}")
    print(f"💾 CSV: {CSV_FILE}")
    print(f"{'='*50}")


if __name__ == "__main__":
    scrape_all()
