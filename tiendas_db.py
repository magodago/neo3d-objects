#!/usr/bin/env python3
"""
NEO Objects — Base de datos de tiendas potenciales
Conoce las zonas comerciales de cada ciudad.
"""

import json, csv
from pathlib import Path

# Zonas comerciales conocidas + tiendas tipo en cada ciudad
SHOPPING_AREAS = {
    "Barcelona": [
        "Passeig de Gràcia", "Rambla de Catalunya", "El Born", 
        "Gràcia", "Eixample", "Tuset", "Diagonal"
    ],
    "Madrid": [
        "Salamanca", "Chueca", "Malasaña", "Barrio de las Letras",
        "Calle Serrano", "Calle Fuencarral", "Calle Velázquez"
    ],
    "Valencia": [
        "El Carmen", "Ruzafa", "Calle Colón", "Calle Poeta Querol"
    ],
    "Bilbao": [
        "Indautxu", "Abando", "Calle Ercilla", "Calle Ledesma"
    ],
    "Sevilla": [
        "Calle Sierpes", "Calle Tetuán", "Alameda de Hércules"
    ],
    "Málaga": [
        "Calle Larios", "Soho", "Muelle Uno"
    ],
    "Zaragoza": [
        "Calle Alfonso I", "Paseo Independencia", "El Tubo"
    ],
    "Palma": [
        "Paseo del Borne", "Santa Catalina", "Jaime III"
    ],
    "Alicante": [
        "Calle Castaños", "Explanada de España", "Centro"
    ],
    "Granada": [
        "Calle Reyes Católicos", "Albaicín", "Centro"
    ],
    "San Sebastián": [
        "Parte Vieja", "Amara", "Calle Getaria"
    ],
    "Santiago": [
        "Casco Histórico", "Ensanche", "Rúa do Vilar"
    ],
}

# Tiendas reales conocidas (ejemplos que podemos contactar)
KNOWN_STORES = [
    # Barcelona
    {"name": "Vinçon", "city": "Barcelona", "address": "Passeig de Gràcia 96", "type": "Hogar/Diseño"},
    {"name": "BD Barcelona Design", "city": "Barcelona", "address": "Carrer de Mallorca 291", "type": "Diseño"},
    {"name": "Gotham", "city": "Barcelona", "address": "Carrer de Ferran 42", "type": "Regalos"},
    {"name": "Muji", "city": "Barcelona", "address": "Passeig de Gràcia 13", "type": "Hogar/Diseño"},
    
    # Madrid
    {"name": "El Corte Inglés Hogar", "city": "Madrid", "address": "Calle Serrano 52", "type": "Grandes almacenes"},
    {"name": "Fun & Basics", "city": "Madrid", "address": "Calle Velázquez 44", "type": "Diseño/Hogar"},
    {"name": "Tienda Museo Reina Sofía", "city": "Madrid", "address": "Calle Santa Isabel 52", "type": "Museo/Regalos"},
    
    # Valencia
    {"name": "Imagina", "city": "Valencia", "address": "Calle Colón 54", "type": "Regalos/Diseño"},
    {"name": "La Casa de la Abuela", "city": "Valencia", "address": "Calle del Mar 12", "type": "Decoración"},
    
    # Bilbao
    {"name": "Museo Guggenheim Shop", "city": "Bilbao", "address": "Abandoibarra Etorbidea 2", "type": "Museo/Regalos"},
]

def build_database():
    output = []
    
    # Add known stores
    for s in KNOWN_STORES:
        s["source"] = "curada"
        s["has_website"] = True
        output.append(s)
    
    # Add shopping areas as leads
    for city, areas in SHOPPING_AREAS.items():
        for area in areas:
            output.append({
                "name": f"Zona {area}",
                "city": city,
                "address": f"{area}, {city}",
                "type": "Zona comercial",
                "source": "shopping_area",
                "estimated_stores": 10
            })
    
    return output


def main():
    Path("/home/dorti/gema_store/neo3d").mkdir(parents=True, exist_ok=True)
    
    db = build_database()
    
    # Save JSON
    with open("/home/dorti/gema_store/neo3d/tiendas_potenciales.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    # Calculate estimates
    known = [s for s in db if s["source"] == "curada"]
    zones = [s for s in db if s["source"] == "shopping_area"]
    estimated_total = len(known) + sum(z.get("estimated_stores", 10) for z in zones)
    
    print(f"Tiendas curadas: {len(known)}")
    print(f"Zonas comerciales: {len(zones)}")
    print(f"Estimación clientes potenciales: {estimated_total}")
    
    # Save CSV  
    with open("/home/dorti/gema_store/neo3d/tiendas_potenciales.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Nombre", "Ciudad", "Dirección", "Tipo", "Fuente"])
        for s in known:
            w.writerow([s["name"], s["city"], s["address"], s["type"], s["source"]])
    
    print("\n✅ Base de datos creada")


if __name__ == "__main__":
    main()
