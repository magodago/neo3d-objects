#!/usr/bin/env python3
"""
NEO Objects — Store Finder via OpenStreetMap
Busca tiendas de regalo, decoración y lifestyle en ciudades de España.
OpenStreetMap es gratis, sin API key, 100% legal.
"""

import json, urllib.request, time, csv
from pathlib import Path

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
CITIES = [
    "Barcelona", "Madrid", "Valencia", "Sevilla", "Bilbao",
    "Málaga", "Zaragoza", "Palma de Mallorca", "Alicante", "Granada",
    "San Sebastián", "Santiago de Compostela", "Santa Cruz de Tenerife",
    "Gijón", "Córdoba", "Valladolid", "Murcia", "Pamplona", "La Coruña",
    "Vitoria", "Castellón", "Almería", "Burgos", "León", "Tarragona",
]

# Shop types relevant for selling 3D printed decorative objects
RELEVANT_TAGS = {
    "gift": "Tienda de regalos",
    "interior_decoration": "Decoración",
    "houseware": "Hogar",
    "art": "Arte/Galería",
    "craft": "Artesanía",
    "antiques": "Antigüedades",
    "homeware": "Artículos hogar",
    "variety_store": "Bazar/Boutique",
}


def query_overpass(city):
    """Query OpenStreetMap for shops in a city."""
    url = "https://overpass-api.de/api/interpreter"
    
    # Build query: find nodes/ways with specific shop tags in the city area
    # We search for ALL shops first, then filter client-side
    overpass_query = f"""
    [out:json];
    area["name"="{city}"][admin_level~"[468]"]->.searchArea;
    (
        node["shop"](area.searchArea);
        way["shop"](area.searchArea);
    );
    out center 20;
    """
    
    data = urllib.parse.urlencode({'data': overpass_query}).encode()
    req = urllib.request.Request(url, data=data, headers={
        'User-Agent': 'NEOObjects/1.0 (business research)'
    })
    
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        
        shops = []
        for elem in result.get('elements', []):
            tags = elem.get('tags', {})
            shop_type = tags.get('shop', '')
            name = tags.get('name', '')
            
            if not name:
                continue
            
            # Get coordinates
            lat = elem.get('lat') or (elem.get('center', {}) or {}).get('lat')
            lon = elem.get('lon') or (elem.get('center', {}) or {}).get('lon')
            
            shops.append({
                'name': name,
                'shop_type': shop_type,
                'category': RELEVANT_TAGS.get(shop_type, shop_type),
                'address': tags.get('addr:full', '') or f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(),
                'postcode': tags.get('addr:postcode', ''),
                'phone': tags.get('phone', ''),
                'website': tags.get('website', ''),
                'email': tags.get('email', ''),
                'city': city,
                'lat': lat,
                'lon': lon,
            })
        
        return shops
    except Exception as e:
        print(f"    ⚠ Error: {e}")
        return []


def main():
    print("=" * 50)
    print("  NEO Objects — Store Finder")
    print("  Powered by OpenStreetMap")
    print("=" * 50)
    
    all_stores = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for i, city in enumerate(CITIES, 1):
        print(f"\n[{i}/{len(CITIES)}] {city}...")
        shops = query_overpass(city)
        
        # Filter relevant types
        relevant = [s for s in shops if s['shop_type'] in RELEVANT_TAGS]
        print(f"    Total shops: {len(shops)} → Relevantes: {len(relevant)}")
        
        all_stores.extend(relevant)
        
        # Save incrementally
        output = OUTPUT_DIR / "tiendas_encontradas.json"
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(all_stores, f, indent=2, ensure_ascii=False)
        
        time.sleep(2)  # Rate limit
    
    # Deduplicate by name+city
    seen = set()
    unique = []
    for s in all_stores:
        key = f"{s['name']}|{s['city']}"
        if key not in seen:
            seen.add(key)
            unique.append(s)
    
    # Stats
    by_city = {}
    by_type = {}
    for s in unique:
        by_city[s['city']] = by_city.get(s['city'], 0) + 1
        by_type[s['category']] = by_type.get(s['category'], 0) + 1
    
    print(f"\n{'=' * 50}")
    print(f"  📊 TOTAL: {len(unique)} tiendas únicas encontradas")
    print(f"{'=' * 50}")
    print(f"\nPor ciudad:")
    for city, count in sorted(by_city.items(), key=lambda x: -x[1]):
        print(f"  {city}: {count}")
    print(f"\nPor tipo:")
    for typ, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {typ}: {count}")
    
    # Save CSV
    csv_path = OUTPUT_DIR / "tiendas_encontradas.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Tipo", "Ciudad", "Dirección", "Teléfono", "Web", "Email"])
        for s in unique:
            w.writerow([s['name'], s['category'], s['city'], 
                       s['address'], s['phone'], s['website'], s['email']])
    print(f"\n✅ CSV guardado: {csv_path}")
    print(f"✅ JSON guardado: {output}")


if __name__ == "__main__":
    main()
