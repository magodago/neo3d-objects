#!/usr/bin/env python3
"""
NEO Objects — Catálogo PDF PREMIUM v3
CADA producto con su propia FOTO GRANDE y descripción premium.
Formato: 1-2 productos por página con imágenes de gran tamaño.
"""
import os, urllib.request
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.flowables import Flowable, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
OUTPUT_PATH = OUTPUT_DIR / "catalogo_neo_objects_v3.pdf"

# ─── COLORS ───
BG = HexColor("#050508")
GOLD = HexColor("#d4af37")
GOLD_LIGHT = HexColor("#e8d5a3")
WHITE = HexColor("#ffffff")
LIGHT = HexColor("#f0e8d8")
MUTED = HexColor("#6a6558")
DARK_BG = HexColor("#0a0a12")
BORDER = HexColor("#1a1a24")

# Try fonts
try:
    pdfmetrics.registerFont(TTFont('Syne', '/usr/share/fonts/truetype/syne/Syne-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('SyneBold', '/usr/share/fonts/truetype/syne/Syne-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Sora', '/usr/share/fonts/truetype/sora/Sora-Regular.ttf'))
    FONT_D = 'Syne'
    FONT_B = 'Sora'
except:
    FONT_D = 'Helvetica-Bold'
    FONT_B = 'Helvetica'

# ─── SPECIFIC PRODUCT IMAGES (high quality reference photos) ───
# Each product gets its own image URL that visually represents the style
PRODUCT_IMAGES = {
    # Maceteros
    "Macetero Geométrico": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=800&q=80",
    "Macetero Ola": "https://images.unsplash.com/photo-1602872030219-0fe6e21a2856?w=800&q=80",
    "Mini Macetero Suculenta": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=800&q=80",
    "Macetero Colgante Nube": "https://images.unsplash.com/photo-1585338107529-29b3d6b9f8c7?w=800&q=80",
    
    # Jarrones
    "Jarrón Espiral": "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=800&q=80",
    "Jarrón Ola": "https://images.unsplash.com/photo-1590511795882-6f00d91a3b8f?w=800&q=80",
    "Jarrón Cilíndrico": "https://images.unsplash.com/photo-1564419436123-55b1c70601e3?w=800&q=80",
    "Set 3 Jarrones": "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?w=800&q=80",
    
    # Portavelas
    "Portavelas Hexagonal": "https://images.unsplash.com/photo-1595009553162-5f0d6a218424?w=800&q=80",
    "Set 3 Portavelas": "https://images.unsplash.com/photo-1603376629532-0afbe6b6e3e0?w=800&q=80",
    "Candelabro Triple": "https://images.unsplash.com/photo-1572893046851-5e8e7db0f9c8?w=800&q=80",
    "Farolillo de Mesa": "https://images.unsplash.com/photo-1591287083668-2ee2a55627bd?w=800&q=80",
    
    # Figuras
    "Busto Atenea": "https://images.unsplash.com/photo-1561736778-92e52a7769ef?w=800&q=80",
    "Figura Gato Egipcio": "https://images.unsplash.com/photo-1568572933382-74d440642117?w=800&q=80",
    "Dragón Articulado": "https://images.unsplash.com/photo-1618336753974-aae8e04506aa?w=800&q=80",
    "Árbol Zen": "https://images.unsplash.com/photo-1608111425280-3e41a6a79a32?w=800&q=80",
    
    # Joyeros
    "Bandeja para Anillos": "https://images.unsplash.com/photo-1581375328618-1e646ab3bfc7?w=800&q=80",
    "Soporte para Pulseras": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&q=80",
    "Expositor Collares": "https://images.unsplash.com/photo-1591703225809-1a79f4b0cae0?w=800&q=80",
    "Cofre Joyero Mini": "https://images.unsplash.com/photo-1592859595518-5b1e1c2d3f9f?w=800&q=80",
    
    # Bandejas
    "Bandeja Ola": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80",
    "Bandeja Geométrica": "https://images.unsplash.com/photo-1586105251261-72a756497a11?w=800&q=80",
    "Catch-all Nube": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
    "Set 3 Bandejas": "https://images.unsplash.com/photo-1530092285049-1c42085fd395?w=800&q=80",
    
    # Pared
    "Panel Hexagonal": "https://images.unsplash.com/photo-1517842645767-c639042777db?w=800&q=80",
    "Estante Nube": "https://images.unsplash.com/photo-1594026112284-02bb6f3352fe?w=800&q=80",
    "Cuadro 3D Abstracto": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=800&q=80",
    "Perchero Escultórico": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&q=80",
    
    # Regalos
    "Llavero Inicial": "https://images.unsplash.com/photo-1605870445919-838d190e8e18?w=800&q=80",
    "Set 4 Imanes": "https://images.unsplash.com/photo-1559827291-2650b44a3c0c?w=800&q=80",
    "Set 6 Posavasos": "https://images.unsplash.com/photo-1567104182658-31ef7e2dc128?w=800&q=80",
    "Marcapáginas": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&q=80",
}

# ─── PRODUCTS ───
PRODUCTS = [
    # ── Maceteros ──
    ("Maceteros", "Diseño minimalista para plantas de interior",
     "Macetero Geométrico", "Prisma de líneas puras con base hexágonal. 14×14×18cm.", "PLA premium mate",
     "Una pieza de geometría escultórica que convierte cualquier rincón en una galería botánica."),
    ("Maceteros", "Diseño minimalista para plantas de interior",
     "Macetero Ola", "Forma orgánica fluida sobre una base estable. 20×12×16cm.", "PLA premium brillo",
     "Como una ola congelada en el tiempo, este macetero captura el movimiento en forma sólida."),
    ("Maceteros", "Diseño minimalista para plantas de interior",
     "Mini Macetero Suculenta", "Minimalista, ideal para escritorio o mesilla. 6×6×7cm.", "Resina HD",
     "Pequeño pero con personalidad. El hogar perfecto para tu planta de escritorio."),
    ("Maceteros", "Diseño minimalista para plantas de interior",
     "Macetero Colgante Nube", "Parece flotar en el aire. Cuerda de cáñamo incluida. 12×12×20cm.", "PLA premium mate",
     "La ingravidez hecha macetero. Un diseño suspendido que desafía la gravedad."),
    
    # ── Jarrones ──
    ("Jarrones", "Esculturas que contienen flores",
     "Jarrón Espiral", "Línea ascendente en espiral en torno a un eje. 10×10×32cm.", "PETG satinado",
     "Una línea que asciende sin fin. La espiral como forma perfecta para albergar flores."),
    ("Jarrones", "Esculturas que contienen flores",
     "Jarrón Ola", "Silueta ondulante que captura el movimiento. 8×8×28cm.", "PETG satinado",
     "La fluidez del agua convertida en cerámica digital. Un jarrón que es puro movimiento."),
    ("Jarrones", "Esculturas que contienen flores",
     "Jarrón Cilíndrico", "Pureza absoluta en su forma más esencial. Diámetro 12cm, alto 30cm.", "PETG satinado",
     "La perfección está en la simplicidad. Un cilindro impecable que deja brillar a las flores."),
    ("Jarrones", "Esculturas que contienen flores",
     "Set 3 Jarrones", "Trío de volúmenes complementarios. Alturas: 18, 24 y 30cm.", "PETG satinado",
     "Tres voces, una armonía. Una composición escultórica que evoluciona con cada flor."),
    
    # ── Portavelas ──
    ("Portavelas", "La luz más bella merece un pedestal",
     "Portavelas Hexagonal", "Geometría sagrada que refracta la luz. 10×10×15cm.", "Resina translúcida",
     "La luz del fuego baila a través de sus caras hexagonales creando patrones hipnóticos."),
    ("Portavelas", "La luz más bella merece un pedestal",
     "Set 3 Portavelas", "Trío de alturas: 8, 12 y 16cm. Composición libre.", "PLA premium mate",
     "Crea tu propia constelación de luz. Tres alturas, infinitas composiciones."),
    ("Portavelas", "La luz más bella merece un pedestal",
     "Candelabro Triple", "Tres brazos que emergen de una base única. 25cm de envergadura.", "PETG satinado",
     "Una escultura de luz. Tres llamas que iluminan cualquier espacio con elegancia."),
    ("Portavelas", "La luz más bella merece un pedestal",
     "Farolillo de Mesa", "Parece un farol japonés. Efecto caleidoscópico. 12×12×20cm.", "Resina translúcida",
     "Un farolillo de papel hecho materia. La luz se filtra creando un ambiente íntimo y mágico."),
    
    # ── Figuras ──
    ("Figuras Decorativas", "Miniatura, máxima expresión",
     "Busto Atenea", "Diosa de la sabiduría. 8×8×18cm.", "Resina HD",
     "La diosa Atenea cobra vida en tu estantería. Sabiduría y belleza clásica en 3D."),
    ("Figuras Decorativas", "Miniatura, máxima expresión",
     "Figura Gato Egipcio", "Bastet, guardiana del hogar. 6×10×15cm.", "Resina HD acabado metálico",
     "La elegancia felina del antiguo Egipto. Bastet protege tu hogar con estilo."),
    ("Figuras Decorativas", "Miniatura, máxima expresión",
     "Dragón Articulado", "12 articulaciones móviles. 30cm de envergadura.", "PLA premium mate + PETG",
     "Un dragón que cobra vida en tus manos. Cada articulación cuenta una historia."),
    ("Figuras Decorativas", "Miniatura, máxima expresión",
     "Árbol Zen", "Paz y armonía para tu espacio. Base 8cm, altura 15cm.", "PLA premium textura madera",
     "El árbol de la vida, miniaturizado. Un recordatorio diario de equilibrio y crecimiento."),
    
    # ── Joyeros ──
    ("Joyeros", "Guarda tus tesoros con estilo",
     "Bandeja para Anillos", "Cama de arena para tus anillos más preciados. 12×8×4cm.", "PLA premium terciopelo",
     "Tus anillos merecen un trono. Una bandeja suave que los exhibe como joyas de museo."),
    ("Joyeros", "Guarda tus tesoros con estilo",
     "Soporte para Pulseras", "Columna inclinada con 3 niveles. 6×6×12cm.", "PLA premium brillo",
     "Tres niveles para tus pulseras favoritas. Cada una visible, cada una accesible."),
    ("Joyeros", "Guarda tus tesoros con estilo",
     "Expositor Collares", "Rama minimalista de la que cuelgan tus collares. 20cm de alto.", "PLA premium mate",
     "Un árbol para tus collares. Cada rama diseñada para mostrar sin enredar."),
    ("Joyeros", "Guarda tus tesoros con estilo",
     "Cofre Joyero Mini", "Con cajón secreto. 10×10×8cm.", "PLA premium + terciopelo interior",
     "Un secreto bien guardado. El cofre perfecto para tus piezas más íntimas."),
    
    # ── Bandejas ──
    ("Bandejas Decorativas", "El orden como forma de belleza",
     "Bandeja Ola", "Topografía ondulante que organiza con estilo. 30×15×3cm.", "PLA premium brillo",
     "Una ola en tu recibidor. Llaves, monedas, cartas: todo encuentra su lugar en su curva."),
    ("Bandejas Decorativas", "El orden como forma de belleza",
     "Bandeja Geométrica", "Compartimentos asimétricos para objetos diversos. 25×18×4cm.", "PLA premium mate",
     "Un paisaje en miniatura para tus objetos cotidianos. Cada compartimento es un valle."),
    ("Bandejas Decorativas", "El orden como forma de belleza",
     "Catch-all Nube", "Forma orgánica para atrapar lo cotidiano. 20×15×3cm.", "PLA premium brillo",
     "Una nube que atrapa tus pequeños tesoros. Ligera, etérea, funcional."),
    ("Bandejas Decorativas", "El orden como forma de belleza",
     "Set 3 Bandejas", "Anidables. De 15 a 30cm. Decoración en capas.", "PLA premium mate",
     "Tres bandejas, una composición. Capas de diseño que organizan tu espacio."),
    
    # ── Pared ──
    ("Adornos de Pared", "La pared como lienzo tridimensional",
     "Panel Hexagonal", "Módulos conectables. 20×20cm cada uno. Set de 3.", "PLA premium mate + PETG",
     "Crea tu propio panal de abeja geométrico. Un mural que evoluciona contigo."),
    ("Adornos de Pared", "La pared como lienzo tridimensional",
     "Estante Nube", "Flota en la pared como una nube. 40×15×20cm.", "PLA premium brillo",
     "Una nube para tus objetos. Un estante que parece suspendido en el aire."),
    ("Adornos de Pared", "La pared como lienzo tridimensional",
     "Cuadro 3D Abstracto", "Capas de profundidad. 30×30×5cm.", "PLA premium mate + resina",
     "Un cuadro que puedes tocar. La tercera dimensión llega a tu pared."),
    ("Adornos de Pared", "La pared como lienzo tridimensional",
     "Perchero Escultórico", "5 ganchos. Arte funcional. 40×8×15cm.", "PLA premium mate",
     "Cuelga tus abrigos de una escultura. Funcionalidad con vocación de arte."),
    
    # ── Regalos ──
    ("Regalos y Detalles", "El regalo perfecto existe y es analógico",
     "Llavero Inicial", "Tu inicial en 3D dorado o plata. 3×5cm.", "PLA premium metalizado",
     "Tu inicial, tu identidad, tu llave. Un llavero que es una declaración de estilo."),
    ("Regalos y Detalles", "El regalo perfecto existe y es analógico",
     "Set 4 Imanes", "Diseños abstractos para tu nevera. 4×4cm cada uno.", "PLA premium mate con imán",
     "Cuatro pequeñas obras de arte para tu nevera. El imán más bonito que tendrás."),
    ("Regalos y Detalles", "El regalo perfecto existe y es analógico",
     "Set 6 Posavasos", "Geometría pura para tus bebidas. 10cm diámetro.", "PLA premium mate",
     "Cada bebida merece un pedestal. Seis diseños geométricos en una caja premium."),
    ("Regalos y Detalles", "El regalo perfecto existe y es analógico",
     "Marcapáginas", "Escultura para lectores. 5×12cm.", "PLA premium metalizado",
     "Un marcador que es una escultura. Porque los lectores también merecen belleza."),
]

W = A4[0] - 36*mm  # usable width


def fetch_img(url, name, max_w=350):
    """Download image, return Image or None."""
    try:
        safe = name.replace(" ", "_").replace("í", "i").replace("ó", "o").replace("é", "e").replace("á", "a")
        img_path = OUTPUT_DIR / f"prod_{safe}.jpg"
        if not img_path.exists():
            urllib.request.urlretrieve(url, img_path)
        if os.path.getsize(img_path) < 1000:
            return None
        img = Image(str(img_path))
        asp = img.drawHeight / img.drawWidth
        img.drawWidth = max_w
        img.drawHeight = max_w * asp
        return img
    except:
        return None


class GoldLine(Flowable):
    def __init__(self, w):
        Flowable.__init__(self)
        self.w = w
        self.height = 1
    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(GOLD)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 0, self.w, 0)
        self.canv.restoreState()


def build():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(str(OUTPUT_PATH), pagesize=A4,
        topMargin=15*mm, bottomMargin=15*mm,
        leftMargin=18*mm, rightMargin=18*mm)
    
    def bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BG)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.3)
        canvas.line(10*mm, 5*mm, 10*mm, A4[1]-5*mm)
        canvas.restoreState()
    
    elements = []
    
    # ─── COVER ───
    elements.append(Spacer(1, 70*mm))
    s = ParagraphStyle("N", fontName=FONT_D, fontSize=72, leading=60, textColor=WHITE, alignment=TA_CENTER)
    elements.append(Paragraph("NE", s))
    s2 = ParagraphStyle("O", fontName=FONT_D, fontSize=72, leading=60, textColor=GOLD, alignment=TA_CENTER)
    elements.append(Paragraph("O", s2))
    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("OBJECTS", ParagraphStyle("sub", fontName=FONT_D, fontSize=16, leading=20, textColor=GOLD, alignment=TA_CENTER)))
    elements.append(Spacer(1, 8*mm))
    g = GoldLine(W*0.4)
    elements.append(g)
    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph("Catálogo Comercial 2026", ParagraphStyle("d", fontName=FONT_B, fontSize=13, leading=18, textColor=LIGHT, alignment=TA_CENTER)))
    elements.append(Paragraph("8 colecciones · 32 piezas · Fabricación bajo pedido", ParagraphStyle("d2", fontName=FONT_B, fontSize=9, leading=13, textColor=MUTED, alignment=TA_CENTER)))
    elements.append(Spacer(1, 40*mm))
    elements.append(Paragraph("Madrid, España", ParagraphStyle("loc", fontName=FONT_B, fontSize=8, leading=12, textColor=MUTED, alignment=TA_CENTER)))
    
    # ─── PRODUCT PAGES ───
    # Group products by category
    current_cat = None
    cat_products = []
    
    for p in PRODUCTS:
        cat_name = p[0]
        cat_tag = p[1]
        prod_name = p[2]
        prod_detail = p[3]
        prod_mat = p[4]
        prod_desc = p[5]
        
        if cat_name != current_cat:
            if cat_products:
                # Render category page(s)
                render_category(elements, current_cat, current_tag, cat_products, doc)
            current_cat = cat_name
            current_tag = cat_tag
            cat_products = [(prod_name, prod_detail, prod_mat, prod_desc)]
        else:
            cat_products.append((prod_name, prod_detail, prod_mat, prod_desc))
    
    # Last category
    if cat_products:
        render_category(elements, current_cat, current_tag, cat_products, doc)
    
    # ─── BACK COVER ───
    elements.append(PageBreak())
    elements.append(Spacer(1, 60*mm))
    elements.append(Paragraph("NE", ParagraphStyle("N2", fontName=FONT_D, fontSize=60, leading=50, textColor=WHITE, alignment=TA_CENTER)))
    elements.append(Paragraph("O", ParagraphStyle("O2", fontName=FONT_D, fontSize=60, leading=50, textColor=GOLD, alignment=TA_CENTER)))
    elements.append(Spacer(1, 25*mm))
    c = ParagraphStyle("c2", fontName=FONT_B, fontSize=9, leading=14, textColor=MUTED, alignment=TA_CENTER)
    elements.append(Paragraph("NEO Objects · Madrid", c))
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph("Fabricamos bajo pedido · Envío 24-72h · Gratis desde 100€", c))
    elements.append(Paragraph("Condiciones especiales para tiendas y mayoristas", 
        ParagraphStyle("cond", fontName=FONT_B, fontSize=8, leading=12, textColor=GOLD, alignment=TA_CENTER)))
    elements.append(Spacer(1, 15*mm))
    g3 = GoldLine(W*0.3)
    elements.append(g3)
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("https://magodago.github.io/neo3d-objects/", 
        ParagraphStyle("web", fontName=FONT_B, fontSize=8, leading=12, textColor=GOLD_LIGHT, alignment=TA_CENTER)))
    
    doc.build(elements, onFirstPage=bg, onLaterPages=bg)
    kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"✅ Catálogo v3: {OUTPUT_PATH} ({kb:.0f} KB)")


def render_category(elements, cat_name, cat_tag, products, doc):
    """Render a category with its products, each with individual large photo."""
    elements.append(PageBreak())
    
    # ── Category header ──
    elements.append(Paragraph(cat_name, ParagraphStyle("ct", fontName=FONT_D, fontSize=26, leading=30, textColor=WHITE, alignment=TA_LEFT)))
    elements.append(Paragraph(cat_tag, ParagraphStyle("ct2", fontName=FONT_B, fontSize=10, leading=13, textColor=GOLD, alignment=TA_LEFT)))
    g = GoldLine(50*mm)
    elements.append(g)
    elements.append(Spacer(1, 10*mm))
    
    # ── Product cards (2 per page, each with large photo) ──
    half = len(products) // 2 + len(products) % 2
    chunks = [products[i:i+2] for i in range(0, len(products), 2)]
    
    for chunk_idx, chunk in enumerate(chunks):
        if chunk_idx > 0:
            elements.append(PageBreak())
            # Repeat header on each page
            elements.append(Paragraph(cat_name, ParagraphStyle("ct", fontName=FONT_D, fontSize=22, leading=26, textColor=WHITE, alignment=TA_LEFT)))
            elements.append(Paragraph(cat_tag, ParagraphStyle("ct2", fontName=FONT_B, fontSize=9, leading=12, textColor=GOLD, alignment=TA_LEFT)))
            g2 = GoldLine(40*mm)
            elements.append(g2)
            elements.append(Spacer(1, 8*mm))
        
        for prod_name, prod_detail, prod_mat, prod_desc in chunk:
            # ── Product card ──
            # Image (big!)
            img_url = PRODUCT_IMAGES.get(prod_name)
            img = fetch_img(img_url, prod_name, max_w=300) if img_url else None
            
            if img:
                # Center the image
                img.hAlign = TA_CENTER
                elements.append(img)
                elements.append(Spacer(1, 6*mm))
            
            # Product name
            elements.append(Paragraph(
                f'<font size="16" color="{WHITE.hexval()}"><b>{prod_name}</b></font>',
                ParagraphStyle("pn", fontName=FONT_D, fontSize=16, leading=20, textColor=WHITE, alignment=TA_CENTER)))
            elements.append(Spacer(1, 3*mm))
            
            # Material badge
            elements.append(Paragraph(
                f'<font size="8" color="{GOLD.hexval()}">▸ {prod_mat}</font>',
                ParagraphStyle("mat", fontName=FONT_B, fontSize=8, leading=11, textColor=GOLD, alignment=TA_CENTER)))
            elements.append(Spacer(1, 3*mm))
            
            # Description
            elements.append(Paragraph(
                prod_desc,
                ParagraphStyle("pd", fontName=FONT_B, fontSize=9, leading=13, 
                              textColor=LIGHT, alignment=TA_CENTER, spaceAfter=4)))
            
            # Details
            elements.append(Paragraph(
                f'<font size="8" color="{MUTED.hexval()}">{prod_detail}</font>',
                ParagraphStyle("pdet", fontName=FONT_B, fontSize=8, leading=11, 
                              textColor=MUTED, alignment=TA_CENTER)))
            
            elements.append(Spacer(1, 18*mm))  # Space between products
    
    # After all products in category, add price info
    elements.append(Spacer(1, 10*mm))
    g3 = GoldLine(W*0.4)
    elements.append(g3)
    elements.append(Spacer(1, 6*mm))
    elements.append(Paragraph(
        "Precios mayoristas desde 5€ · Pedido mínimo 12 uds · Consultar condiciones",
        ParagraphStyle("price", fontName=FONT_B, fontSize=8, leading=11, textColor=GOLD, alignment=TA_CENTER)))


if __name__ == "__main__":
    build()
