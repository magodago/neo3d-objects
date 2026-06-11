#!/usr/bin/env python3
"""
NEO Objects — Catálogo PDF Premium v2
Genera un catálogo profesional con:
- Logo NEO con NE/O en 2 líneas
- Descripciones premium de cada categoría
- Fotografías de calidad (Unsplash)
- Diseño oscuro + dorado
"""
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.doctemplate import BaseDocTemplate
from reportlab.platypus.frames import Frame as RLFrame
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import urllib.request
import textwrap

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
OUTPUT_PATH = OUTPUT_DIR / "catalogo_neo_objects.pdf"

# ─── COLORS ───
BG = HexColor("#050508")
GOLD = HexColor("#d4af37")
GOLD_LIGHT = HexColor("#e8d5a3")
GOLD_DARK = HexColor("#b8962f")
WHITE = HexColor("#ffffff")
LIGHT_TEXT = HexColor("#f0e8d8")
MUTED = HexColor("#6a6558")
DARK_BG = HexColor("#0a0a12")
BORDER = HexColor("#1a1a24")

# ─── CATEGORIES ───
CATEGORIES = [
    {
        "id": "maceteros",
        "name": "Maceteros",
        "tagline": "Diseño minimalista para plantas de interior",
        "desc": (
            "Cada macetero NEO Objects es una pieza de diseño escultórico que eleva tus plantas "
            "a otro nivel. Geometrías puras acabadas en PLA premium con capa de 0.08mm, "
            "disponibles en versión con hueco para suculentas o con sistema de drenaje oculto. "
            "Desde maceteros colgantes que desafían la gravedad hasta composiciones geométricas "
            "que convierten cualquier rincón en una galería botánica."
        ),
        "products": [
            ("Macetero Geométrico", "Prisma de líneas puras con base hexágonal. 14×14×18cm."),
            ("Macetero Ola", "Forma orgánica fluida, como una ola congelada. 20×12×16cm."),
            ("Mini Macetero Suculenta", "Minimalista, ideal para escritorio. 6×6×7cm."),
            ("Macetero Colgante Nube", "Parece flotar. Cuerda incluida. 12×12×20cm."),
        ],
        "img": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=800&q=80",
    },
    {
        "id": "jarrones",
        "name": "Jarrones",
        "tagline": "Esculturas que contienen flores",
        "desc": (
            "Nuestros jarrones son el punto focal de cualquier estancia. Cada pieza está diseñada "
            "para ser contemplada tanto con flores como vacía, convirtiéndose en una escultura "
            "autónoma. Altos, esbeltos, escultóricos. Fabricados en PETG de alta resistencia "
            "con acabado satinado que juega con la luz natural. La unión perfecta entre "
            "artesanía digital y diseño contemporáneo."
        ),
        "products": [
            ("Jarrón Espiral", "Línea ascendente en espiral infinita. 10×10×32cm."),
            ("Jarrón Ola", "Silueta ondulante, fluida. 8×8×28cm."),
            ("Jarrón Cilíndrico", "Pureza absoluta. 12cm diámetro, 30cm alto."),
            ("Set 3 Jarrones", "Trío de volúmenes complementarios. Alturas 18/24/30cm."),
        ],
        "img": "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?w=800&q=80",
    },
    {
        "id": "portavelas",
        "name": "Portavelas",
        "tagline": "La luz más bella merece un pedestal",
        "desc": (
            "El juego de luces y sombras a través de nuestras piezas crea ambientes que "
            "transforman cualquier espacio. Cada portavelas está calibrado para maximizar "
            "la refracción de la llama, generando patrones de luz hipnóticos en las paredes. "
            "Disponibles en sets que permiten composiciones personalizadas. La oscuridad "
            "es el lienzo; nuestras piezas, el pincel de luz."
        ),
        "products": [
            ("Portavelas Hexagonal", "Geometría sagrada. 10×10×15cm. Para vela de 7cm."),
            ("Set 3 Portavelas", "Trío de alturas: 8, 12, 16cm. Composición libre."),
            ("Candelabro Triple", "Tres brazos, una pieza. 25cm de envergadura."),
            ("Farolillo de Mesa", "Efecto caleidoscópico. 12×12×20cm."),
        ],
        "img": "https://images.unsplash.com/photo-1595009553162-5f0d6a218424?w=800&q=80",
    },
    {
        "id": "figuras",
        "name": "Figuras Decorativas",
        "tagline": "Miniatura, máxima expresión",
        "desc": (
            "Pequeñas esculturas que cuentan historias. Cada figura NEO Objects captura "
            "la esencia de su inspiración — desde la majestuosidad de la mitología clásica "
            "hasta la serenidad del arte zen — en un formato que encaja en cualquier "
            "estantería, mesa o escritorio. Impresas en resina de alta definición con "
            "detalles que solo se aprecian al tenerlas en mano."
        ),
        "products": [
            ("Busto Atenea", "Diosa de la sabiduría. 8×8×18cm. Resina HD."),
            ("Figura Gato Egipcio", "Bastet, guardiana del hogar. 6×10×15cm."),
            ("Dragón Articulado", "12 articulaciones móviles. 30cm de largo."),
            ("Árbol Zen", "Paz y armonía. Base 8cm, altura 15cm."),
        ],
        "img": "https://images.unsplash.com/photo-1561736778-92e52a7769ef?w=800&q=80",
    },
    {
        "id": "joyeros",
        "name": "Joyeros",
        "tagline": "Guarda tus tesoros con estilo",
        "desc": (
            "Cada joyero NEO Objects está diseñado como un pedestal para tus objetos "
            "más preciados. Bandejas para anillos que parecen flotar, soportes para "
            "pulseras que las convierten en piezas decorativas, expositores que transforman "
            "tu tocador en una galería. Porque guardar no está reñido con exhibir."
        ),
        "products": [
            ("Bandeja para Anillos", "Cama de arena para tus anillos. 12×8×4cm."),
            ("Soporte para Pulseras", "Columna inclinada. 6×6×12cm. 3 niveles."),
            ("Expositor Collares", "Rama minimalista. 20cm de alto."),
            ("Cofre Joyero Mini", "Con cajón secreto. 10×10×8cm."),
        ],
        "img": "https://images.unsplash.com/photo-1581375328618-1e646ab3bfc7?w=800&q=80",
    },
    {
        "id": "bandejas",
        "name": "Bandejas Decorativas",
        "tagline": "El orden como forma de belleza",
        "desc": (
            "Bandejas que son arte funcional. Desde el recibidor hasta la mesa de centro, "
            "nuestras bandejas organizan mientras decoran. Cada pieza presenta una "
            "topografía única — olas, ondas, pliegues — que convierte lo cotidiano en "
            "extraordinario. Llaves, monedas, cartas: todo encuentra su lugar en una "
            "bandeja NEO."
        ),
        "products": [
            ("Bandeja Ola", "Topografía ondulante. 30×15×3cm."),
            ("Bandeja Geométrica", "Compartimentos asimétricos. 25×18×4cm."),
            ("Catch-all Nube", "Forma orgánica. 20×15×3cm."),
            ("Set 3 Bandejas", "Anidables. De 15 a 30cm. Decoración en capas."),
        ],
        "img": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80",
    },
    {
        "id": "pared",
        "name": "Adornos de Pared",
        "tagline": "La pared como lienzo tridimensional",
        "desc": (
            "Rompe la bidimensionalidad de tus paredes con nuestras piezas escultóricas. "
            "Paneles geométricos que crean sombras cambiantes según la luz del día, "
            "estantes que parecen flotar, cuadros 3D que invitan al tacto. Cada pieza "
            "es una instalación artística que transforma paredes vacías en galerías "
            "domésticas."
        ),
        "products": [
            ("Panel Hexagonal", "Paneles modulares. 20×20cm cada uno. Set de 3."),
            ("Estante Nube", "Flota en la pared. 40×15×20cm."),
            ("Cuadro 3D Abstracto", "Capa sobre capa. 30×30×5cm."),
            ("Perchero Escultórico", "5 ganchos. Arte funcional. 40×8×15cm."),
        ],
        "img": "https://images.unsplash.com/photo-1517842645767-c639042777db?w=800&q=80",
    },
    {
        "id": "gifts",
        "name": "Regalos y Detalles",
        "tagline": "El regalo perfecto existe y es analógico",
        "desc": (
            "En un mundo digital, un objeto impreso en 3D con tus iniciales o un diseño "
            "único es el regalo más personal que puedes hacer. Llaveros que son "
            "mini-esculturas, posavasos que son geometría pura, imanes que son "
            "pequeñas obras de arte. Porque los mejores regalos no vienen en una app."
        ),
        "products": [
            ("Llavero Inicial", "Tu inicial en 3D. 3×5cm. Dorado o plata."),
            ("Set 4 Imanes", "Diseños abstractos. 4×4cm cada uno."),
            ("Set 6 Posavasos", "Geometría. 10cm diámetro. Caja incluida."),
            ("Marcapáginas", "Escultura para lectores. 5×12cm."),
        ],
        "img": "https://images.unsplash.com/photo-1512909006721-3d6018887383?w=800&q=80",
    },
]

# ─── Try to register fonts ───
try:
    pdfmetrics.registerFont(TTFont('Syne', '/usr/share/fonts/truetype/syne/Syne-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('SyneBold', '/usr/share/fonts/truetype/syne/Syne-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('SyneExtraBold', '/usr/share/fonts/truetype/syne/Syne-ExtraBold.ttf'))
    pdfmetrics.registerFont(TTFont('Sora', '/usr/share/fonts/truetype/sora/Sora-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('SoraLight', '/usr/share/fonts/truetype/sora/Sora-Light.ttf'))
    pdfmetrics.registerFont(TTFont('SoraSemiBold', '/usr/share/fonts/truetype/sora/Sora-SemiBold.ttf'))
    FONT_DISPLAY = 'Syne'
    FONT_BODY = 'Sora'
    print("✅ Fonts loaded")
except:
    FONT_DISPLAY = 'Helvetica'
    FONT_BODY = 'Helvetica'
    print("⚠ Using Helvetica fallback")


# ─── STYLES ───
styles = getSampleStyleSheet()

s_cover_title = ParagraphStyle("CoverTitle", fontName=FONT_DISPLAY, fontSize=48,
    leading=52, textColor=WHITE, alignment=TA_CENTER, spaceAfter=6)
s_cover_sub = ParagraphStyle("CoverSub", fontName=FONT_BODY, fontSize=14,
    leading=20, textColor=GOLD, alignment=TA_CENTER, spaceAfter=40)
s_cover_tag = ParagraphStyle("CoverTag", fontName=FONT_BODY, fontSize=9,
    leading=13, textColor=MUTED, alignment=TA_CENTER)

s_section_title = ParagraphStyle("SectionTitle", fontName=FONT_DISPLAY, fontSize=28,
    leading=32, textColor=WHITE, spaceAfter=4)
s_section_tag = ParagraphStyle("SectionTag", fontName=FONT_BODY, fontSize=11,
    leading=14, textColor=GOLD, spaceAfter=16)
s_desc = ParagraphStyle("Desc", fontName=FONT_BODY, fontSize=9.5,
    leading=14, textColor=LIGHT_TEXT, alignment=TA_JUSTIFY, spaceAfter=12)
s_prod_name = ParagraphStyle("ProdName", fontName=FONT_DISPLAY, fontSize=10,
    leading=12, textColor=WHITE, spaceAfter=2)
s_prod_detail = ParagraphStyle("ProdDetail", fontName=FONT_BODY, fontSize=8,
    leading=10, textColor=MUTED)
s_footer = ParagraphStyle("Footer", fontName=FONT_BODY, fontSize=7,
    leading=9, textColor=MUTED, alignment=TA_CENTER)


class GradientBg(Flowable):
    """Dark background gradient flowable."""
    def __init__(self, width, height, color1=BG, color2=HexColor("#0a0a16")):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color1 = color1
        self.color2 = color2
    def draw(self):
        self.canv.saveState()
        self.canv.setFillColor(self.color1)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        self.canv.restoreState()


class GoldLine(Flowable):
    """Thin gold horizontal line."""
    def __init__(self, width, y_offset=0):
        Flowable.__init__(self)
        self.width = width
        self.y_offset = y_offset
        self.height = 1
    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(GOLD)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 0, self.width, 0)
        self.canv.restoreState()


def fetch_image(url, max_width=400):
    """Download image from URL and return reportlab Image."""
    try:
        img_path = OUTPUT_DIR / f"_img_{abs(hash(url))}.jpg"
        if not img_path.exists():
            urllib.request.urlretrieve(url, img_path)
        img = Image(str(img_path))
        aspect = img.drawHeight / img.drawWidth
        img.drawWidth = max_width
        img.drawHeight = max_width * aspect
        return img
    except:
        return None


def build_pdf():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        topMargin=15*mm, bottomMargin=15*mm,
        leftMargin=18*mm, rightMargin=18*mm,
    )
    
    # ─── PAGE BACKGROUND ───
    frame = RLFrame(
        18*mm, 15*mm, A4[0]-36*mm, A4[1]-30*mm,
        id='normal'
    )
    
    elements = []
    W = A4[0] - 36*mm  # usable width
    
    # ═══════════════════════════════════
    # PAGE 1: COVER
    # ═══════════════════════════════════
    elements.append(Spacer(1, 80*mm))
    
    # NEO Logo - NE on first line, O on second
    elements.append(Paragraph(
        '<font size="72" color="%s">NE</font>' % WHITE.hexval(),
        ParagraphStyle("Logo1", fontName=FONT_DISPLAY, fontSize=72,
                       leading=60, textColor=WHITE, alignment=TA_CENTER)
    ))
    elements.append(Paragraph(
        '<font size="72" color="%s">O</font>' % GOLD.hexval(),
        ParagraphStyle("Logo2", fontName=FONT_DISPLAY, fontSize=72,
                       leading=60, textColor=GOLD, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 8*mm))
    
    elements.append(Paragraph("OBJECTS", s_cover_sub))
    elements.append(Spacer(1, 6*mm))
    
    g = GoldLine(W*0.4)
    g.width = W*0.4
    elements.append(g)
    elements.append(Spacer(1, 10*mm))
    
    elements.append(Paragraph(
        "Catálogo Comercial · Primavera 2026",
        ParagraphStyle("CoverDate", fontName=FONT_BODY, fontSize=13,
                       leading=18, textColor=LIGHT_TEXT, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 6*mm))
    
    elements.append(Paragraph(
        "Diseño e impresión 3D premium · Madrid",
        ParagraphStyle("CoverLoc", fontName=FONT_BODY, fontSize=9,
                       leading=13, textColor=MUTED, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 30*mm))
    
    # Tagline
    elements.append(Paragraph(
        "8 colecciones · Más de 80 piezas · Fabricación bajo pedido",
        ParagraphStyle("Tagline", fontName=FONT_BODY, fontSize=10,
                       leading=14, textColor=GOLD, alignment=TA_CENTER)
    ))
    
    # ═══════════════════════════════════
    # PAGE 2: INDEX
    # ═══════════════════════════════════
    elements.append(PageBreak())
    elements.append(Spacer(1, 15*mm))
    
    elements.append(Paragraph("ÍNDICE", ParagraphStyle(
        "IndexTitle", fontName=FONT_DISPLAY, fontSize=18,
        leading=22, textColor=WHITE, alignment=TA_CENTER)))
    elements.append(Spacer(1, 6*mm))
    g2 = GoldLine(W*0.3)
    g2.width = W*0.3
    elements.append(g2)
    elements.append(Spacer(1, 20*mm))
    
    for i, cat in enumerate(CATEGORIES, 1):
        elements.append(Paragraph(
            f'<font color="%s">%02d.</font>  %s &nbsp;—&nbsp; '
            f'<font size="10" color="%s">%s</font>' % (
                GOLD.hexval(), i, cat["name"],
                MUTED.hexval(), cat["tagline"]),
            ParagraphStyle(f"Index{i}", fontName=FONT_BODY, fontSize=12,
                          leading=20, textColor=WHITE, alignment=TA_CENTER)
        ))
        elements.append(Spacer(1, 6*mm))
    
    # ═══════════════════════════════════
    # PAGES 3+: CATEGORIES
    # ═══════════════════════════════════
    for cat in CATEGORIES:
        elements.append(PageBreak())
        elements.append(Spacer(1, 10*mm))
        
        # Category header
        elements.append(Paragraph(cat["name"], s_section_title))
        elements.append(Paragraph(cat["tagline"], s_section_tag))
        g3 = GoldLine(60*mm)
        g3.width = 60*mm
        elements.append(g3)
        elements.append(Spacer(1, 8*mm))
        
        # Try to add image (if fetchable)
        img = fetch_image(cat["img"], max_width=int(W))
        if img:
            elements.append(img)
            elements.append(Spacer(1, 8*mm))
        
        # Premium description
        elements.append(Paragraph(cat["desc"], s_desc))
        elements.append(Spacer(1, 10*mm))
        
        # Product table (2 columns)
        prod_data = []
        for name, detail in cat["products"]:
            prod_data.append([
                Paragraph(f'<b>{name}</b>', s_prod_name),
                Paragraph(detail, s_prod_detail),
            ])
        
        col_w = W * 0.48
        prod_table = Table(prod_data, colWidths=[col_w, col_w])
        prod_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), DARK_BG),
            ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [DARK_BG, HexColor("#0e0e18")]),
        ]))
        elements.append(prod_table)
        elements.append(Spacer(1, 15*mm))
        
        # Price note
        elements.append(Paragraph(
            "Precios mayoristas desde 5€ · Pedido mínimo 12 unidades · "
            "Consultar condiciones comerciales",
            ParagraphStyle("PriceNote", fontName=FONT_BODY, fontSize=8,
                          leading=11, textColor=GOLD, alignment=TA_CENTER)
        ))
    
    # ═══════════════════════════════════
    # FINAL PAGE: CONTACT
    # ═══════════════════════════════════
    elements.append(PageBreak())
    elements.append(Spacer(1, 60*mm))
    
    elements.append(Paragraph(
        '<font size="60" color="%s">NE</font>' % WHITE.hexval(),
        ParagraphStyle("LogoEnd1", fontName=FONT_DISPLAY, fontSize=60,
                       leading=50, textColor=WHITE, alignment=TA_CENTER)
    ))
    elements.append(Paragraph(
        '<font size="60" color="%s">O</font>' % GOLD.hexval(),
        ParagraphStyle("LogoEnd2", fontName=FONT_DISPLAY, fontSize=60,
                       leading=50, textColor=GOLD, alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 15*mm))
    
    elements.append(Paragraph("OBJECTS", ParagraphStyle(
        "EndTitle", fontName=FONT_DISPLAY, fontSize=16,
        leading=20, textColor=LIGHT_TEXT, alignment=TA_CENTER)))
    elements.append(Spacer(1, 20*mm))
    
    contact_lines = [
        "info@neoobjects.com",
        "Madrid, España",
        "https://magodago.github.io/neo3d-objects/",
        "",
        "Fabricación bajo pedido · Envío 24-72h · Envío gratis >100€",
        "Condiciones especiales para tiendas y mayoristas",
    ]
    for line in contact_lines:
        elements.append(Paragraph(line, s_footer))
        elements.append(Spacer(1, 4*mm))
    
    # ─── BUILD ───
    # We need to set page background manually
    def add_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BG)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        # Gold accent line on left edge
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.5)
        canvas.line(10*mm, 0, 10*mm, A4[1])
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=add_bg, onLaterPages=add_bg)
    
    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"\n✅ Catálogo generado: {OUTPUT_PATH}")
    print(f"   Tamaño: {size_kb:.0f} KB")
    print(f"   Páginas: ~{len(CATEGORIES) + 3}")
    return OUTPUT_PATH


if __name__ == "__main__":
    build_pdf()
