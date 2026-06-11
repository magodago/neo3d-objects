#!/usr/bin/env python3
"""
NEO Objects — Prospector Masivo de Comunidad de Madrid
Busca TIENDAS en TODOS los municipios de Madrid usando OpenStreetMap,
con tipos de tienda relevantes para vender productos 3D impresos.
"""
import json, urllib.request, urllib.parse, time, csv, re, os
from pathlib import Path

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── TODOS los municipios de la Comunidad de Madrid (>20k habitantes) ───
MADRID_TOWNS = [
    "Madrid", "Móstoles", "Alcalá de Henares", "Fuenlabrada", "Leganés",
    "Getafe", "Alcorcón", "Torrejón de Ardoz", "Parla", "Alcobendas",
    "Las Rozas de Madrid", "San Sebastián de los Reyes", "Pozuelo de Alarcón",
    "Rivas-Vaciamadrid", "Majadahonda", "Coslada", "Valdemoro", "Collado Villalba",
    "Aranjuez", "Boadilla del Monte", "Pinto", "Colmenar Viejo",
    "Tres Cantos", "San Fernando de Henares", "Villanueva de la Cañada",
    "Villaviciosa de Odón", "Moralzarzal", "Torrelodones", "Galapagar",
    "Algete", "Mejorada del Campo", "Navalcarnero", "Ciempozuelos",
    "San Martín de la Vega", "El Escorial", "Guadarrama", "Cercedilla",
    "Manzanares el Real", "Miraflores de la Sierra", "Becerril de la Sierra",
    "Hoyo de Manzanares", "Las Matas", "Las Tablas", "Montecarmelo",
    "Sanchinarro", "El Goloso", "Fuencarral", "Carabanchel",
    "Vallecas", "Villaverde", "Usera", "Latina", "Hortaleza",
    "Barajas", "Ciudad Lineal", "Salamanca", "Chamartín", "Tetúan",
    "Chamberí", "Moncloa-Aravaca", "Retiro", "Arganzuela", "Centro",
    "Vicálvaro", "Villa de Vallecas", "Puente de Vallecas",
    "Alcobendas", "San Agustín del Guadalix", "El Molar",
    "Pedrezuela", "San Sebastián de los Reyes",
]

# ─── Tipos de tienda que nos interesan ───
SHOP_TAGS = {
    "gift": "Tienda de regalos",
    "florist": "Floristería",
    "toy": "Juguetería",
    "interior_decoration": "Decoración",
    "houseware": "Hogar",
    "homeware": "Artículos hogar",
    "variety_store": "Bazar/Boutique",
    "art": "Arte/Galería",
    "craft": "Artesanía",
    "garden_centre": "Centro jardinería",
    "design": "Diseño",
    "interior_design": "Interiorismo",
    "books": "Librería",
    "boutique": "Boutique",
    "jewelry": "Joyería",
}

def query_overpass_city(city):
    """Query OpenStreetMap for relevant shops in a city."""
    url = "https://overpass-api.de/api/interpreter"
    
    # Build shop type filter
    # Only search for specific relevant shop types
    overpass_query = f"""
    [out:json][timeout:60];
    area["name"="{city}"][admin_level~"[468]"]->.searchArea;
    (
        node["shop"="gift"](area.searchArea);
        node["shop"="florist"](area.searchArea);
        node["shop"="toy"](area.searchArea);
        node["shop"="interior_decoration"](area.searchArea);
        node["shop"="houseware"](area.searchArea);
        node["shop"="homeware"](area.searchArea);
        node["shop"="variety_store"](area.searchArea);
        node["shop"="art"](area.searchArea);
        node["shop"="craft"](area.searchArea);
        node["shop"="garden_centre"](area.searchArea);
        node["shop"="design"](area.searchArea);
        node["shop"="interior_design"](area.searchArea);
        node["shop"="books"](area.searchArea);
        node["shop"="boutique"](area.searchArea);
        node["shop"="jewelry"](area.searchArea);
        way["shop"="gift"](area.searchArea);
        way["shop"="florist"](area.searchArea);
        way["shop"="toy"](area.searchArea);
        way["shop"="interior_decoration"](area.searchArea);
        way["shop"="houseware"](area.searchArea);
        way["shop"="homeware"](area.searchArea);
        way["shop"="variety_store"](area.searchArea);
        way["shop"="art"](area.searchArea);
        way["shop"="craft"](area.searchArea);
        way["shop"="garden_centre"](area.searchArea);
        way["shop"="design"](area.searchArea);
        way["shop"="interior_design"](area.searchArea);
        way["shop"="books"](area.searchArea);
        way["shop"="boutique"](area.searchArea);
        way["shop"="jewelry"](area.searchArea);
    );
    out center 30;
    """
    
    data = urllib.parse.urlencode({'data': overpass_query}).encode()
    req = urllib.request.Request(url, data=data, headers={
        'User-Agent': 'NEOObjects/2.0 (business research; formulasia76@gmail.com)'
    })
    
    try:
        resp = urllib.request.urlopen(req, timeout=90)
        result = json.loads(resp.read())
        
        shops = []
        for elem in result.get('elements', []):
            tags = elem.get('tags', {})
            shop_type = tags.get('shop', '')
            name = tags.get('name', '').strip()
            
            if not name:
                continue
            
            # Get coordinates
            lat = elem.get('lat') or (elem.get('center', {}) or {}).get('lat')
            lon = elem.get('lon') or (elem.get('center', {}) or {}).get('lon')
            
            # Build address
            addr_parts = []
            if tags.get('addr:street'):
                addr_parts.append(tags['addr:street'])
            if tags.get('addr:housenumber'):
                addr_parts.append(tags['addr:housenumber'])
            address = ' '.join(addr_parts) or tags.get('addr:full', '')
            postcode = tags.get('addr:postcode', '')
            
            # Phone & email (rare in OSM but worth checking)
            phone = tags.get('phone', '')
            email = tags.get('email', '')
            website = tags.get('website', '')
            
            shops.append({
                'name': name,
                'shop_type': shop_type,
                'category': SHOP_TAGS.get(shop_type, shop_type),
                'address': address,
                'postcode': postcode,
                'city': city,
                'phone': phone,
                'website': website,
                'email': email,
                'lat': lat,
                'lon': lon,
            })
        
        return shops
    except urllib.error.HTTPError as e:
        print(f"    ⚠ HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"    ⚠ Error: {e}")
        return []


def extract_emails_from_web(store_name, city):
    """Try to find email for a store via web search."""
    # This is a simple placeholder - in practice we'd use web_search
    # Returns None for now, we'll handle it later
    return None


def main():
    print("=" * 60)
    print("  NEO Objects — Prospector COMUNIDAD DE MADRID")
    print("  Buscando tiendas objetivo en todos los municipios")
    print("=" * 60)
    
    all_stores = []
    
    for i, city in enumerate(MADRID_TOWNS, 1):
        print(f"\n[{i}/{len(MADRID_TOWNS)}] {city}...", end="", flush=True)
        shops = query_overpass_city(city)
        
        print(f" → {len(shops)} tiendas", flush=True)
        all_stores.extend(shops)
        
        # Save incrementally
        output = OUTPUT_DIR / "madrid_stores_raw.json"
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(all_stores, f, indent=2, ensure_ascii=False)
        
        time.sleep(1.5)  # Rate limit
    
    # ─── Deduplicate ───
    seen = set()
    unique = []
    for s in all_stores:
        key = f"{s['name']}|{s['city']}|{s['address']}"
        if key not in seen:
            seen.add(key)
            unique.append(s)
    
    # ─── Stats ───
    by_type = {}
    by_city = {}
    for s in unique:
        by_type[s['category']] = by_type.get(s['category'], 0) + 1
        by_city[s['city']] = by_city.get(s['city'], 0) + 1
    
    print(f"\n{'=' * 60}")
    print(f"  📊 TOTAL: {len(unique)} tiendas únicas en Comunidad de Madrid")
    print(f"{'=' * 60}")
    
    print(f"\n📂 Por tipo de tienda:")
    for typ, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {typ}: {count}")
    
    print(f"\n📍 Por municipio (top 20):")
    for city, count in sorted(by_city.items(), key=lambda x: -x[1])[:20]:
        print(f"  {city}: {count}")
    
    # ─── Save CSV (todas) ───
    csv_path = OUTPUT_DIR / "madrid_stores_all.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Ciudad", "Dirección", "Teléfono", "Web", "Email"])
        for s in unique:
            w.writerow([s['name'], s['category'], s['city'],
                       s['address'], s['phone'], s['website'], s['email']])
    print(f"\n💾 CSV guardado: {csv_path}")
    
    # ─── Save CSV (solo con email) ───
    with_email = [s for s in unique if s.get('email')]
    csv_email = OUTPUT_DIR / "madrid_stores_with_email.csv"
    with open(csv_email, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Categoría", "Ciudad", "Email", "Teléfono", "Web"])
        for s in with_email:
            w.writerow([s['name'], s['category'], s['city'],
                       s['email'], s['phone'], s['website']])
    print(f"💾 CSV con emails: {csv_email} ({len(with_email)} tiendas)")
    
    # ─── JSON final ───
    final_json = OUTPUT_DIR / "madrid_stores.json"
    with open(final_json, 'w', encoding='utf-8') as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    print(f"💾 JSON guardado: {final_json}")
    
    print(f"\n{'=' * 60}")
    print(f"  ✅ PROSPECCIÓN COMPLETADA")
    print(f"  Siguiente paso: buscar emails de tiendas sin contacto")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
