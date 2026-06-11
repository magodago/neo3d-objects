#!/usr/bin/env python3
"""
NEO Objects — Email Templating System for Store Outreach
Genera emails personalizados para cada tienda con enlace al catálogo PDF.
"""
import json, csv, os
from pathlib import Path
from string import Template
from datetime import datetime

BASE_DIR = Path.home() / "gema_store" / "neo3d"

# ─── Email templates ───

EMAIL_TEMPLATES = {
    "regalos": {
        "subject": "Catálogo NEO 3D — Productos únicos para tu tienda de regalos",
        "body": """Hola {name},

Soy David, fundador de NEO Objects — un estudio de diseño e impresión 3D premium ubicado en Madrid.

Creo que nuestros productos encajarían perfectamente en tu tienda de regalos. Trabajamos con materiales de alta calidad (PLA, PETG y resina) y ofrecemos acabados premium con capa de 0.08mm.

Algunas de nuestras categorías:

• Figuras decorativas: bustos, animales, esculturas abstractas
• Joyeros y bandejas decorativas
• Jarrones y portavelas de diseño
• Regalos personalizados: llaveros, imanes, marcapáginas
• Colección navideña y estacional

📎 Te adjunto nuestro catálogo comercial con todas las categorías y condiciones mayoristas.
Precios desde 5€ (PVP recomendado) con margen para tienda del 40-60%.

¿Te interesaría recibir una muestra física o tener una llamada rápida para contarte más?

Un saludo,
David
NEO Objects
📧 formulasia76@gmail.com
🌐 https://magodago.github.io/neo3d-objects/
"""
    },
    "floristeria": {
        "subject": "Complementos únicos para floristerías — NEO 3D Objects",
        "body": """Hola {name},

Soy David, fundador de NEO Objects — un estudio de diseño 3D premium en Madrid.

He pensado que nuestros productos podrían ser un complemento ideal para tu floristería:

• 🏺 Jarrones de diseño (altos, escultóricos, sets de 3)
• 🌱 Maceteros geométricos y colgantes
• 🕯️ Portavelas decorativos
• 🎁 Detalles para regalar con flores

Todos fabricados con materiales premium y acabado de alta calidad.

📎 Te adjunto nuestro catálogo mayorista con precios especiales para tiendas.

¿Quéieres que te prepare un pack de muestra o prefieres que te llame para explicarte?

Gracias por tu tiempo,

David
NEO Objects
📧 formulasia76@gmail.com
🌐 https://magodago.github.io/neo3d-objects/
"""
    },
    "jugueteria": {
        "subject": "Figuras 3D únicas para tu juguetería — NEO Objects",
        "body": """Hola {name},

Soy David, de NEO Objects. Creamos figuras y juguetes impresos en 3D con diseño premium.

Para tu juguetería tenemos:

• 🐉 Figuras articuladas (dragones, animales, dinosaurios)
• 🎨 Figuras decorativas (animales, bustos clásicos)
• 🧩 Puzles 3D y sets apilables
• 🏠 Miniaturas y adornos
• 🎁 Detalles y regalos originales

Fabricación bajo pedido, sin stock mínimo. Envío a península en 24-72h.

📎 Te adjunto nuestro catálogo con precios mayoristas.

¿Te interesa? Podemos preparar una muestra o hablar por teléfono.

Saludos,

David
NEO Objects
📧 formulasia76@gmail.com
"""
    },
    "decoracion": {
        "subject": "Nueva colección de decoración 3D premium para tiendas",
        "body": """Hola {name},

Soy David, de NEO Objects. Somos un estudio especializado en diseño y fabricación 3D de productos de decoración.

Creo que nuestras piezas encajarían perfectamente en tu tienda:

• 🏺 Jarrones escultóricos y sets decorativos
• 🖼️ Adornos de pared 3D y paneles geométricos
• 🕯️ Portavelas y candelabros de diseño
• 📦 Bandejas y organizadores decorativos
• 🎄 Colección navideña contemporánea

Fabricamos con materiales premium (PLA, PETG, resina) y capa de 0.08mm. Producto bajo pedido, sin stock mínimo.

📎 Aquí tienes nuestro catálogo mayorista completo.

¿Te gustaría que te enviara una muestra o prefieres una llamada?

Un saludo,

David
NEO Objects
📧 formulasia76@gmail.com
🌐 https://magodago.github.io/neo3d-objects/
"""
    },
    "general": {
        "subject": "Catálogo de productos 3D premium para tiendas — NEO Objects",
        "body": """Hola {name},

Soy David, fundador de NEO Objects. Somos un pequeño estudio de diseño 3D en Madrid.

Creemos que nuestros productos encajarían muy bien en tu establecimiento:

🏺 Maceteros y jarrones de diseño
🕯️ Portavelas y candelabros
🐉 Figuras decorativas y articuladas
📦 Organizadores y bandejas
💍 Joyeros y expositores
🎨 Decoración de pared 3D
🎁 Regalos y detalles personalizados

Trabajamos bajo pedido (sin stock mínimo), con materiales premium y acabados de alta calidad.

📎 Te adjunto nuestro catálogo comercial con condiciones para tiendas.

¿Te parece bien si te llamo esta semana o prefieres que te escriba por WhatsApp?

Gracias,

David
NEO Objects
📧 formulasia76@gmail.com
🌐 https://magodago.github.io/neo3d-objects/
"""
    },
}

# ─── Mapping de categorías de tienda a templates ───
CATEGORY_TEMPLATE_MAP = {
    "Floristería": "floristeria",
    "Centro jardinería": "floristeria",
    "Juguetería": "jugueteria",
    "Tienda de regalos": "regalos",
    "Decoración": "decoracion",
    "Hogar": "decoracion",
    "Artículos hogar": "decoracion",
    "Muebles": "decoracion",
    "Diseño": "decoracion",
    "Interiorismo": "decoracion",
    "Bazar/Boutique": "regalos",
    "Arte/Galería": "decoracion",
    "Artesanía": "regalos",
    "Antigüedades": "regalos",
    "Vintage": "regalos",
    "Librería": "regalos",
    "Boutique": "regalos",
    "Joyería": "regalos",
    "Belleza/Perfumería": "regalos",
    "Grandes almacenes": "general",
}


def get_template(store_category):
    """Get the best email template for a store category."""
    template_key = CATEGORY_TEMPLATE_MAP.get(store_category, "general")
    return EMAIL_TEMPLATES[template_key]


def _g(store, *keys):
    """Get value from store dict using any of the provided keys."""
    for k in keys:
        v = store.get(k)
        if v and v.strip():
            return v.strip()
    return ""

def generate_email(store, catalog_url="https://magodago.github.io/neo3d-objects/"):
    """Generate a personalized email for a store."""
    category = _g(store, "category", "Categoría")
    template = get_template(category)
    
    # Prepare variables for template
    name = _g(store, "name", "Nombre", "to_name", "store")
    name_clean = name.replace("Zona ", "").strip()
    if not name_clean:
        name_clean = "tienda"
    
    body = template["body"].format(name=name_clean)
    
    return {
        "to_name": name_clean,
        "to_email": _g(store, "email", "Email"),
        "subject": template["subject"],
        "body": body.strip(),
        "store_category": category,
        "store_city": _g(store, "city", "Ciudad"),
    }


def generate_all_emails(stores_csv=None):
    """Generate emails for all stores in the database."""
    if stores_csv is None:
        stores_csv = BASE_DIR / "madrid_stores_with_email.csv"
    
    if not os.path.exists(stores_csv):
        print(f"⚠ No se encuentra {stores_csv}")
        return []
    
    emails = []
    with open(stores_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Email"):
                email_data = generate_email(row)
                emails.append(email_data)
    
    return emails


def save_email_report(emails):
    """Save all generated emails to a file for review."""
    output = BASE_DIR / "email_campaign_report.txt"
    with open(output, 'w', encoding='utf-8') as f:
        f.write(f"NEO Objects — Campaña de Email\n")
        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total emails: {len(emails)}\n")
        f.write("=" * 60 + "\n\n")
        
        for i, e in enumerate(emails, 1):
            f.write(f"[{i}] {e['to_name']} ({e['store_city']})\n")
            f.write(f"    → {e['to_email']}\n")
            f.write(f"    Asunto: {e['subject']}\n")
            f.write(f"    Categoría: {e['store_category']}\n")
            f.write(f"{'─' * 40}\n\n")
    
    print(f"✅ Reporte guardado: {output}")
    return output


def export_to_mailerlite_csv(emails, group_name="Tiendas Madrid"):
    """Export emails to MailerLite-compatible CSV."""
    output = BASE_DIR / "mailerlite_import.csv"
    with open(output, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["email", "name", "city", "store_type"])
        for e in emails:
            w.writerow([
                e['to_email'],
                e['to_name'],
                e['store_city'],
                e['store_category'],
            ])
    print(f"✅ MailerLite CSV: {output}")
    return output


if __name__ == "__main__":
    import sys
    
    csv_path = sys.argv[1] if len(sys.argv) > 1 else str(BASE_DIR / "madrid_stores_with_email.csv")
    
    print("=" * 50)
    print("  NEO Objects — Generador de Emails")
    print("=" * 50)
    
    emails = generate_all_emails(csv_path)
    print(f"\n📧 Emails generados: {len(emails)}")
    
    if emails:
        save_email_report(emails)
        export_to_mailerlite_csv(emails)
    
    # Preview first 3
    print(f"\n📝 Vista previa (primeros 3):")
    for e in emails[:3]:
        print(f"\n{'─' * 40}")
        print(f"  Para: {e['to_name']} <{e['to_email']}>")
        print(f"  Asunto: {e['subject']}")
        print(f"  {e['body'][:200]}...")
