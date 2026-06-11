#!/usr/bin/env python3
"""
NEO Objects — Catálogo PDF ULTRA PREMIUM v4
Cada producto = UNA PÁGINA COMPLETA con foto grande de calidad.
Diseño: oscuro + dorado, minimalista, editorial.
"""
import os, urllib.request, time, random
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d"
OUTPUT_PATH = OUTPUT_DIR / "catalogo_neo_premium.pdf"

# ─── COLORS ───
BG = HexColor("#050508")
GOLD = HexColor("#d4af37")
GOLD_LIGHT = HexColor("#e8d5a3")
WHITE = HexColor("#ffffff")
LIGHT = HexColor("#f0e8d8")
MUTED = HexColor("#6a6558")
DARK2 = HexColor("#0a0a12")
BORDER = HexColor("#1a1a24")

# Fonts
try:
    pdfmetrics.registerFont(TTFont('Syne', '/usr/share/fonts/truetype/syne/Syne-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('SyneB', '/usr/share/fonts/truetype/syne/Syne-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('SyneEB', '/usr/share/fonts/truetype/syne/Syne-ExtraBold.ttf'))
    pdfmetrics.registerFont(TTFont('Sora', '/usr/share/fonts/truetype/sora/Sora-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('SoraL', '/usr/share/fonts/truetype/sora/Sora-Light.ttf'))
    pdfmetrics.registerFont(TTFont('SoraSB', '/usr/share/fonts/truetype/sora/Sora-SemiBold.ttf'))
    FONT_D = 'Syne'
    FONT_B = 'Sora'
except:
    FONT_D = 'Helvetica-Bold'
    FONT_B = 'Helvetica'

# ─── BACKUP IMAGES for each product (tries multiple URLs) ───
# Each entry has 3-4 backup URLs so at least one should work
PRODUCT_IMAGES = {
    # MACETEROS
    "Macetero Geométrico": [
        "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=900&q=85",
        "https://images.unsplash.com/photo-1617718295766-684d12df2479?w=900&q=85",
        "https://images.unsplash.com/photo-1585597047982-95e3c9e3678e?w=900&q=85",
    ],
    "Macetero Ola": [
        "https://images.unsplash.com/photo-1602872030219-0fe6e21a2856?w=900&q=85",
        "https://images.unsplash.com/photo-1596558450255-71e54f1a7579?w=900&q=85",
        "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?w=900&q=85",
    ],
    "Mini Macetero Suculenta": [
        "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=900&q=85",
        "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=900&q=85",
        "https://images.unsplash.com/photo-1487530811176-3780de880c2d?w=900&q=85",
    ],
    "Macetero Colgante Nube": [
        "https://images.unsplash.com/photo-1585338107529-29b3d6b9f8c7?w=900&q=85",
        "https://images.unsplash.com/photo-1463936575829-25148e1db1b8?w=900&q=85",
        "https://images.unsplash.com/photo-1545167626-e2b5f31059ac?w=900&q=85",
    ],
    # JARRONES
    "Jarrón Espiral": [
        "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=900&q=85",
        "https://images.unsplash.com/photo-1593757138779-214f13328fed?w=900&q=85",
        "https://images.unsplash.com/photo-1581783898377-1c85bf937427?w=900&q=85",
    ],
    "Jarrón Ola": [
        "https://images.unsplash.com/photo-1601634967762-b6d19dff6680?w=900&q=85",
        "https://images.unsplash.com/photo-1583485088034-697b5bc35c1d?w=900&q=85",
        "https://images.unsplash.com/photo-1590511795882-6f00d91a3b8f?w=900&q=85",
    ],
    "Jarrón Cilíndrico": [
        "https://images.unsplash.com/photo-1564419436123-55b1c70601e3?w=900&q=85",
        "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?w=900&q=85",
        "https://images.unsplash.com/photo-1600626371058-4b2612cb1adc?w=900&q=85",
    ],
    "Set 3 Jarrones": [
        "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?w=900&q=85",
        "https://images.unsplash.com/photo-1600626371058-4b2612cb1adc?w=900&q=85",
        "https://images.unsplash.com/photo-1590511795882-6f00d91a3b8f?w=900&q=85",
    ],
    # PORTAVELAS
    "Portavelas Hexagonal": [
        "https://images.unsplash.com/photo-1595009553162-5f0d6a218424?w=900&q=85",
        "https://images.unsplash.com/photo-1603376629532-0afbe6b6e3e0?w=900&q=85",
        "https://images.unsplash.com/photo-1591287083668-2ee2a55627bd?w=900&q=85",
    ],
    "Set 3 Portavelas": [
        "https://images.unsplash.com/photo-1603376629532-0afbe6b6e3e0?w=900&q=85",
        "https://images.unsplash.com/photo-1595009553162-5f0d6a218424?w=900&q=85",
        "https://images.unsplash.com/photo-1572893046851-5e8e7db0f9c8?w=900&q=85",
    ],
    "Candelabro Triple": [
        "https://images.unsplash.com/photo-1572893046851-5e8e7db0f9c8?w=900&q=85",
        "https://images.unsplash.com/photo-1595009553162-5f0d6a218424?w=900&q=85",
        "https://images.unsplash.com/photo-1603376629532-0afbe6b6e3e0?w=900&q=85",
    ],
    "Farolillo de Mesa": [
        "https://images.unsplash.com/photo-1591287083668-2ee2a55627bd?w=900&q=85",
        "https://images.unsplash.com/photo-1595009553162-5f0d6a218424?w=900&q=85",
        "https://images.unsplash.com/photo-1572893046851-5e8e7db0f9c8?w=900&q=85",
    ],
    # FIGURAS
    "Busto Atenea": [
        "https://images.unsplash.com/photo-1561736778-92e52a7769ef?w=900&q=85",
        "https://images.unsplash.com/photo-1546356061-92022e2ce3d3?w=900&q=85",
        "https://images.unsplash.com/photo-1603105037880-4cd82e398d39?w=900&q=85",
    ],
    "Figura Gato Egipcio": [
        "https://images.unsplash.com/photo-1568572933382-74d440642117?w=900&q=85",
        "https://images.unsplash.com/photo-1560807707-8cc77767d783?w=900&q=85",
        "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=900&q=85",
    ],
    "Dragón Articulado": [
        "https://images.unsplash.com/photo-1618336753974-aae8e04506aa?w=900&q=85",
        "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=900&q=85",
        "https://images.unsplash.com/photo-1534445867742-43195f401b6c?w=900&q=85",
    ],
    "Árbol Zen": [
        "https://images.unsplash.com/photo-1507501336603-6e6f661e2bfe?w=900&q=85",
        "https://images.unsplash.com/photo-1549797180-94df5ae472a3?w=900&q=85",
        "https://images.unsplash.com/photo-1518655048521-f130df041f66?w=900&q=85",
    ],
    # JOYEROS
    "Bandeja para Anillos": [
        "https://images.unsplash.com/photo-1581375328618-1e646ab3bfc7?w=900&q=85",
        "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900&q=85",
        "https://images.unsplash.com/photo-1591703225809-1a79f4b0cae0?w=900&q=85",
    ],
    "Soporte para Pulseras": [
        "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900&q=85",
        "https://images.unsplash.com/photo-1581375328618-1e646ab3bfc7?w=900&q=85",
        "https://images.unsplash.com/photo-1591703225809-1a79f4b0cae0?w=900&q=85",
    ],
    "Expositor Collares": [
        "https://images.unsplash.com/photo-1591703225809-1a79f4b0cae0?w=900&q=85",
        "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900&q=85",
        "https://images.unsplash.com/photo-1581375328618-1e646ab3bfc7?w=900&q=85",
    ],
    "Cofre Joyero Mini": [
        "https://images.unsplash.com/photo-1592859595518-5b1e1c2d3f9f?w=900&q=85",
        "https://images.unsplash.com/photo-1581375328618-1e646ab3bfc7?w=900&q=85",
        "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900&q=85",
    ],
    # BANDEJAS
    "Bandeja Ola": [
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=900&q=85",
        "https://images.unsplash.com/photo-1586105251261-72a756497a11?w=900&q=85",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900&q=85",
    ],
    "Bandeja Geométrica": [
        "https://images.unsplash.com/photo-1586105251261-72a756497a11?w=900&q=85",
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=900&q=85",
        "https://images.unsplash.com/photo-1530092285049-1c42085fd395?w=900&q=85",
    ],
    "Catch-all Nube": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900&q=85",
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=900&q=85",
        "https://images.unsplash.com/photo-1586105251261-72a756497a11?w=900&q=85",
    ],
    "Set 3 Bandejas": [
        "https://images.unsplash.com/photo-1530092285049-1c42085fd395?w=900&q=85",
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=900&q=85",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900&q=85",
    ],
    # PARED
    "Panel Hexagonal": [
        "https://images.unsplash.com/photo-1517842645767-c639042777db?w=900&q=85",
        "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=900&q=85",
        "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=900&q=85",
    ],
    "Estante Nube": [
        "https://images.unsplash.com/photo-1594026112284-02bb6f3352fe?w=900&q=85",
        "https://images.unsplash.com/photo-1517842645767-c639042777db?w=900&q=85",
        "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=900&q=85",
    ],
    "Cuadro 3D Abstracto": [
        "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=900&q=85",
        "https://images.unsplash.com/photo-1517842645767-c639042777db?w=900&q=85",
        "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=900&q=85",
    ],
    "Perchero Escultórico": [
        "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=900&q=85",
        "https://images.unsplash.com/photo-1517842645767-c639042777db?w=900&q=85",
        "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=900&q=85",
    ],
    # REGALOS
    "Llavero Inicial": [
        "https://images.unsplash.com/photo-1605870445919-838d190e8e18?w=900&q=85",
        "https://images.unsplash.com/photo-1559827291-2650b44a3c0c?w=900&q=85",
        "https://images.unsplash.com/photo-1567104182658-31ef7e2dc128?w=900&q=85",
    ],
    "Set 4 Imanes": [
        "https://images.unsplash.com/photo-1559827291-2650b44a3c0c?w=900&q=85",
        "https://images.unsplash.com/photo-1605870445919-838d190e8e18?w=900&q=85",
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=900&q=85",
    ],
    "Set 6 Posavasos": [
        "https://images.unsplash.com/photo-1567104182658-31ef7e2dc128?w=900&q=85",
        "https://images.unsplash.com/photo-1559827291-2650b44a3c0c?w=900&q=85",
        "https://images.unsplash.com/photo-1605870445919-838d190e8e18?w=900&q=85",
    ],
    "Marcapáginas": [
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=900&q=85",
        "https://images.unsplash.com/photo-1567104182658-31ef7e2dc128?w=900&q=85",
        "https://images.unsplash.com/photo-1559827291-2650b44a3c0c?w=900&q=85",
    ],
}

# ─── ALL 32 PRODUCTS ───
PRODUCTS = [
    # --- MACETEROS ---
    ("Maceteros", "Macetero Geométrico",
     "Prisma de líneas puras con base hexágonal.",
     "14×14×18cm | PLA premium mate",
     "Una pieza de geometría escultórica que convierte cualquier rincón en una galería botánica. "
     "Sus líneas puras y acabado mate capturan la luz de forma sutil."),
    ("Maceteros", "Macetero Ola",
     "Forma orgánica fluida sobre base estable.",
     "20×12×16cm | PLA premium brillo",
     "Como una ola congelada en el tiempo. Este macetero captura el movimiento en forma sólida, "
     "creando un diálogo entre la planta y su contenedor."),
    ("Maceteros", "Mini Macetero Suculenta",
     "Minimalista, ideal para escritorio o mesilla.",
     "6×6×7cm | Resina HD",
     "Pequeño pero con personalidad. El hogar perfecto para tu planta de escritorio. "
     "Un detalle que transforma cualquier espacio de trabajo."),
    ("Maceteros", "Macetero Colgante Nube",
     "Parece flotar en el aire. Cuerda de cáñamo incluida.",
     "12×12×20cm | PLA premium mate",
     "La ingravidez hecha macetero. Un diseño suspendido que desafía la gravedad "
     "y eleva tus plantas literal y metafóricamente."),
    
    # --- JARRONES ---
    ("Jarrones", "Jarrón Espiral",
     "Línea ascendente en espiral en torno a un eje.",
     "10×10×32cm | PETG satinado premium",
     "Una línea que asciende sin fin. La espiral como forma perfecta para albergar flores, "
     "creando un efecto visual hipnótico desde cualquier ángulo."),
    ("Jarrones", "Jarrón Ola",
     "Silueta ondulante que captura el movimiento.",
     "8×8×28cm | PETG satinado premium",
     "La fluidez del agua convertida en objeto. Un jarrón que es puro movimiento congelado, "
     "tan bello con flores como vacío."),
    ("Jarrones", "Jarrón Cilíndrico",
     "Pureza absoluta en su forma más esencial.",
     "Ø12×30cm | PETG satinado premium",
     "La perfección está en la simplicidad. Un cilindro impecable que deja brillar a las flores "
     "sin competir con ellas. El fondo de escena perfecto."),
    ("Jarrones", "Set 3 Jarrones",
     "Trío de volúmenes complementarios.",
     "Alturas: 18, 24 y 30cm | PETG satinado premium",
     "Tres voces, una armonía. Una composición escultórica que evoluciona con cada flor, "
     "permitiendo combinaciones infinitas."),
    
    # --- PORTAVELAS ---
    ("Portavelas", "Portavelas Hexagonal",
     "Geometría sagrada que refracta la luz.",
     "10×10×15cm | Resina translúcida",
     "La luz del fuego baila a través de sus caras hexagonales creando patrones hipnóticos "
     "en las paredes. Una experiencia visual envolvente."),
    ("Portavelas", "Set 3 Portavelas",
     "Trío de alturas. Composición libre.",
     "8, 12 y 16cm | PLA premium mate",
     "Crea tu propia constelación de luz. Tres alturas, infinitas composiciones. "
     "Cada vela encuentra su pedestal perfecto."),
    ("Portavelas", "Candelabro Triple",
     "Tres brazos que emergen de una base única.",
     "25cm envergadura | PETG satinado",
     "Una escultura de luz. Tres llamas que iluminan cualquier espacio con elegancia. "
     "El punto focal que toda mesa de comedor merece."),
    ("Portavelas", "Farolillo de Mesa",
     "Estética japonesa contemporánea. Efecto caleidoscópico.",
     "12×12×20cm | Resina translúcida",
     "Un farolillo de papel hecho materia. La luz se filtra creando un ambiente íntimo y mágico. "
     "Inspirado en la tradición japonesa del papel washi."),
    
    # --- FIGURAS ---
    ("Figuras Decorativas", "Busto Atenea",
     "Diosa de la sabiduría. Réplica escultórica.",
     "8×8×18cm | Resina HD premium",
     "La diosa Atenea cobra vida en tu estantería. Sabiduría y belleza clásica en 3D. "
     "Cada detalle del rostro capturado con precisión milimétrica."),
    ("Figuras Decorativas", "Figura Gato Egipcio",
     "Bastet, guardiana del hogar. Estilo art déco.",
     "6×10×15cm | Resina HD acabado oro",
     "La elegancia felina del antiguo Egipto. Bastet protege tu hogar con estilo. "
     "Acabado metalizado que evoca el oro de los templos egipcios."),
    ("Figuras Decorativas", "Dragón Articulado",
     "12 articulaciones móviles. Poseable.",
     "30cm envergadura | PLA+PETG",
     "Un dragón que cobra vida en tus manos. Cada articulación permite posarlo "
     "como una escultura viviente. La pieza estrella de la colección."),
    ("Figuras Decorativas", "Árbol Zen",
     "Paz y armonía para tu espacio.",
     "Base 8cm, altura 15cm | PLA textura madera",
     "El árbol de la vida, miniaturizado. Un recordatorio diario de equilibrio y "
     "crecimiento. La base funciona como bandeja para incienso."),
    
    # --- JOYEROS ---
    ("Joyeros", "Bandeja para Anillos",
     "Cama de terciopelo para tus anillos.",
     "12×8×4cm | PLA + terciopelo negro",
     "Tus anillos merecen un trono. Una bandeja suave que los exhibe como joyas de museo. "
     "El fondo de terciopelo protege tus piezas más preciadas."),
    ("Joyeros", "Soporte para Pulseras",
     "Columna inclinada. 3 niveles.",
     "6×6×12cm | PLA premium brillo",
     "Tres niveles para tus pulseras favoritas. Cada una visible, cada una accesible. "
     "Un joyero que es también un objeto decorativo."),
    ("Joyeros", "Expositor Collares",
     "Rama minimalista. 5 brazos.",
     "20cm de alto | PLA premium mate",
     "Un árbol para tus collares. Cada rama diseñada para mostrar sin enredar. "
     "Convierte tu tocador en una galería de joyas."),
    ("Joyeros", "Cofre Joyero Mini",
     "Con cajón secreto oculto.",
     "10×10×8cm | PLA + terciopelo interior",
     "Un secreto bien guardado. El cofre perfecto para tus piezas más íntimas. "
     "El cajón secreto se revela solo al iniciado."),
    
    # --- BANDEJAS ---
    ("Bandejas Decorativas", "Bandeja Ola",
     "Topografía ondulante. Recibidor.",
     "30×15×3cm | PLA premium brillo",
     "Una ola en tu recibidor. Llaves, monedas, cartas: todo encuentra su lugar "
     "en su curva. El primer objeto que ves al llegar a casa."),
    ("Bandejas Decorativas", "Bandeja Geométrica",
     "Compartimentos asimétricos.",
     "25×18×4cm | PLA premium mate",
     "Un paisaje en miniatura para tus objetos cotidianos. Cada compartimento es "
     "un valle donde descansan tus pequeños tesoros."),
    ("Bandejas Decorativas", "Catch-all Nube",
     "Forma orgánica. Atrapa lo cotidiano.",
     "20×15×3cm | PLA premium brillo",
     "Una nube que atrapa tus pequeños tesoros. Ligera, etérea, pero lo "
     "suficientemente sólida para organizar tu día a día."),
    ("Bandejas Decorativas", "Set 3 Bandejas",
     "Anidables. Decoración en capas.",
     "15, 22 y 30cm | PLA premium mate",
     "Tres bandejas, una composición. Capas de diseño que organizan tu espacio "
     "con elegancia. Usa juntas o por separado."),
    
    # --- PARED ---
    ("Adornos de Pared", "Panel Hexagonal",
     "Módulos conectables. Set de 3.",
     "20×20cm c/u | PLA+PETG",
     "Crea tu propio panal de abeja geométrico. Un mural que evoluciona contigo. "
     "Añade más paneles para expandir tu composición."),
    ("Adornos de Pared", "Estante Nube",
     "Flota en la pared. Almacenaje escultórico.",
     "40×15×20cm | PLA premium brillo",
     "Una nube para tus objetos. Un estante que parece suspendido en el aire. "
     "El soporte invisible crea el efecto de levitación."),
    ("Adornos de Pared", "Cuadro 3D Abstracto",
     "Capas de profundidad. Arte táctil.",
     "30×30×5cm | PLA+Resina",
     "Un cuadro que puedes tocar. La tercera dimensión llega a tu pared. "
     "Cada capa cuenta una historia de profundidad y textura."),
    ("Adornos de Pared", "Perchero Escultórico",
     "5 ganchos. Arte funcional.",
     "40×8×15cm | PLA premium mate",
     "Cuelga tus abrigos de una escultura. Funcionalidad con vocación de arte. "
     "Cada gancho es una pieza única del conjunto."),
    
    # --- REGALOS ---
    ("Regalos y Detalles", "Llavero Inicial",
     "Tu inicial en 3D. Dorado o plata.",
     "3×5cm | PLA metalizado premium",
     "Tu inicial, tu identidad, tu llave. Un llavero que es una declaración de estilo. "
     "Disponible en dorado NEO, plata y negro mate."),
    ("Regalos y Detalles", "Set 4 Imanes",
     "Diseños abstractos. Para nevera o pizarra.",
     "4×4cm c/u | PLA con imán neodimio",
     "Cuatro pequeñas obras de arte para tu nevera. El imán más bonito que tendrás. "
     "Diseños geométricos que cambian con la luz."),
    ("Regalos y Detalles", "Set 6 Posavasos",
     "Geometría pura. Caja regalo incluida.",
     "Ø10cm | PLA premium mate",
     "Cada bebida merece un pedestal. Seis diseños geométricos en una caja premium. "
     "El regalo perfecto que combina arte y utilidad."),
    ("Regalos y Detalles", "Marcapáginas",
     "Escultura para lectores.",
     "5×12cm | PLA metalizado premium",
     "Un marcador que es una escultura. Porque los lectores también merecen belleza. "
     "Se desliza entre las páginas como una obra de arte en miniatura."),
]

# ─── CATEGORY INTRO PAGES ───
CATEGORIES = [
    ("Maceteros", "Diseño minimalista para plantas de interior", "Cada macetero NEO Objects eleva tus plantas a otro nivel con geometrías puras y acabados premium.", 4),
    ("Jarrones", "Esculturas que contienen flores", "Piezas diseñadas para ser contempladas tanto con flores como vacías. El punto focal de cualquier estancia.", 4),
    ("Portavelas", "La luz más bella merece un pedestal", "El juego de luces y sombras a través de nuestras piezas transforma cualquier espacio en un ambiente mágico.", 4),
    ("Figuras Decorativas", "Miniatura, máxima expresión", "Pequeñas esculturas que cuentan historias. Cada figura captura la esencia de su inspiración.", 4),
    ("Joyeros", "Guarda tus tesoros con estilo", "Cada joyero NEO Objects está diseñado como un pedestal para tus objetos más preciados.", 4),
    ("Bandejas Decorativas", "El orden como forma de belleza", "Bandejas que organizan mientras decoran. Cada pieza convierte lo cotidiano en extraordinario.", 4),
    ("Adornos de Pared", "La pared como lienzo tridimensional", "Paneles, estantes y cuadros 3D que transforman paredes vacías en galerías domésticas.", 4),
    ("Regalos y Detalles", "El regalo perfecto existe", "Objetos únicos que son el regalo más personal que puedes hacer. Porque los mejores regalos no vienen en una app.", 4),
]


def download_image(urls, name, dest_dir, max_w=500):
    """Try multiple URLs for a product, return Image or None."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for url in urls:
        try:
            safe = name.lower().replace(" ", "_").replace("í","i").replace("ó","o").replace("é","e").replace("á","a").replace("ú","u").replace("/","_")
            ext = ".jpg"
            path = dest_dir / f"img_{safe}{ext}"
            
            if not path.exists():
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                with urllib.request.urlopen(req, timeout=15) as r:
                    with open(path, 'wb') as f:
                        f.write(r.read())
            
            if os.path.getsize(path) < 5000:
                os.remove(path)
                continue
            
            img = Image(str(path))
            asp = img.drawHeight / img.drawWidth
            
            # Limit height to fit nicely
            if asp > 1.5:  # portrait
                img.drawHeight = 440
                img.drawWidth = 440 / asp
            else:
                img.drawWidth = 440
                img.drawHeight = 440 * asp
            
            return img
        except:
            continue
    
    return None


class GoldLine(Flowable):
    def __init__(self, w):
        Flowable.__init__(self)
        self.w = w
        self.height = 0.5
    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(GOLD)
        self.canv.setLineWidth(0.3)
        self.canv.line(0, 0, self.w, 0)
        self.canv.restoreState()


class GoldBadge(Flowable):
    """Foil accent square in top-right corner."""
    def __init__(self, w=20, h=20, x=0, y=0):
        Flowable.__init__(self)
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.width = w
        self.height = h
    def draw(self):
        self.canv.saveState()
        self.canv.setFillColor(GOLD)
        self.canv.rect(self.x, self.y, self.w, self.h, fill=1, stroke=0)
        self.canv.restoreState()


W = A4[0] - 36*mm  # usable width (~170mm)


def build():
    print("=" * 50)
    print("  NEO Objects — Catálogo Premium v4")
    print("=" * 50)
    
    IMG_DIR = OUTPUT_DIR / "_product_images"
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    # ─── DOWNLOAD ALL IMAGES FIRST ───
    print("\n📥 Descargando imágenes de productos...")
    img_cache = {}
    for cat_name, prod_name, detail, specs, desc in PRODUCTS:
        urls = PRODUCT_IMAGES.get(prod_name, [])
        if not urls:
            print(f"  ❌ {prod_name}: sin URLs")
            continue
        img = download_image(urls, prod_name, IMG_DIR)
        if img:
            img_cache[prod_name] = img
            print(f"  ✅ {prod_name}")
        else:
            print(f"  ❌ {prod_name}: no se pudo descargar")
    
    print(f"\n📊 Imágenes descargadas: {len(img_cache)}/{len(PRODUCTS)}")
    
    # ─── BUILD PDF ───
    doc = SimpleDocTemplate(str(OUTPUT_PATH), pagesize=A4,
        topMargin=12*mm, bottomMargin=12*mm,
        leftMargin=15*mm, rightMargin=15*mm)
    
    def page_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BG)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        # Gold vertical accent on left
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.3)
        canvas.line(8*mm, 8*mm, 8*mm, A4[1]-8*mm)
        # Page number
        canvas.setFillColor(MUTED)
        canvas.setFont(FONT_B, 7)
        canvas.drawCentredString(A4[0]/2, 7*mm, f"—  {doc.page}  —")
        canvas.restoreState()
    
    elements = []
    
    # ═══════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════
    elements.append(Spacer(1, 50*mm))
    
    # Logo NE / O
    elements.append(Paragraph("NE", ParagraphStyle("cover_ne",
        fontName=FONT_D, fontSize=84, leading=70, textColor=WHITE, alignment=TA_CENTER)))
    elements.append(Paragraph("O", ParagraphStyle("cover_o",
        fontName=FONT_D, fontSize=84, leading=70, textColor=GOLD, alignment=TA_CENTER)))
    elements.append(Spacer(1, 12*mm))
    
    gl = GoldLine(W*0.35)
    elements.append(gl)
    elements.append(Spacer(1, 15*mm))
    
    elements.append(Paragraph("OBJECTS", ParagraphStyle("cover_sub",
        fontName=FONT_D, fontSize=20, leading=24, textColor=GOLD, alignment=TA_CENTER)))
    elements.append(Spacer(1, 25*mm))
    
    elements.append(Paragraph("Catálogo Comercial · 2026", ParagraphStyle("cover_date",
        fontName=FONT_B, fontSize=14, leading=18, textColor=LIGHT, alignment=TA_CENTER)))
    elements.append(Spacer(1, 6*mm))
    elements.append(Paragraph("Diseño e impresión 3D premium · Madrid, España", 
        ParagraphStyle("cover_loc", fontName=FONT_B, fontSize=9, leading=13, textColor=MUTED, alignment=TA_CENTER)))
    elements.append(Spacer(1, 40*mm))
    
    elements.append(Paragraph("8 colecciones  ·  32 piezas  ·  Fabricación bajo pedido", 
        ParagraphStyle("cover_stats", fontName=FONT_B, fontSize=9, leading=13, textColor=GOLD, alignment=TA_CENTER)))
    elements.append(Paragraph("Materiales premium  ·  Acabado 0.08mm  ·  Envío 24-72h", 
        ParagraphStyle("cover_stats2", fontName=FONT_B, fontSize=8, leading=12, textColor=MUTED, alignment=TA_CENTER)))
    
    # ═══════════════════════════════════════
    # ÍNDICE
    # ═══════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Spacer(1, 30*mm))
    
    elements.append(Paragraph("ÍNDICE", ParagraphStyle("index_title",
        fontName=FONT_D, fontSize=24, leading=28, textColor=WHITE, alignment=TA_CENTER)))
    gl2 = GoldLine(W*0.25)
    elements.append(gl2)
    elements.append(Spacer(1, 25*mm))
    
    for i, (name, tagline, desc, count) in enumerate(CATEGORIES, 1):
        elements.append(Paragraph(
            f'<font color="{GOLD.hexval()}">{i:02d}</font>&nbsp;&nbsp;{name}'
            f'&nbsp;&nbsp;<font size="9" color="{MUTED.hexval()}">{count} productos</font>',
            ParagraphStyle(f"idx{i}", fontName=FONT_D, fontSize=14, leading=22,
                          textColor=WHITE, alignment=TA_CENTER)))
        elements.append(Paragraph(
            f'<font size="8" color="{MUTED.hexval()}">— {tagline} —</font>',
            ParagraphStyle(f"idx{i}_t", fontName=FONT_B, fontSize=8, leading=12,
                          textColor=MUTED, alignment=TA_CENTER)))
        elements.append(Spacer(1, 10*mm))
    
    # ═══════════════════════════════════════
    # CATEGORY & PRODUCT PAGES
    # ═══════════════════════════════════════
    current_cat = None
    prod_count_in_cat = 0
    
    for cat_name, prod_name, detail, specs, desc in PRODUCTS:
        if cat_name != current_cat:
            current_cat = cat_name
            prod_count_in_cat = 0
            
            # Find category info
            cat_info = None
            for c in CATEGORIES:
                if c[0] == cat_name:
                    cat_info = c
                    break
            
            # ── Category intro page ──
            elements.append(PageBreak())
            elements.append(Spacer(1, 55*mm))
            
            elements.append(Paragraph(cat_name.upper(), ParagraphStyle("cat_title",
                fontName=FONT_D, fontSize=36, leading=40, textColor=WHITE, alignment=TA_CENTER)))
            elements.append(Spacer(1, 6*mm))
            elements.append(Paragraph(
                f'<font size="12" color="{GOLD.hexval()}">{cat_info[1] if cat_info else ""}</font>',
                ParagraphStyle("cat_tag", fontName=FONT_B, fontSize=12, leading=16,
                              textColor=GOLD, alignment=TA_CENTER)))
            gl3 = GoldLine(W*0.3)
            elements.append(gl3)
            elements.append(Spacer(1, 12*mm))
            elements.append(Paragraph(
                cat_info[2] if cat_info else "",
                ParagraphStyle("cat_desc", fontName=FONT_B, fontSize=10, leading=15,
                              textColor=LIGHT, alignment=TA_CENTER, spaceAfter=8)))
            elements.append(Spacer(1, 30*mm))
            elements.append(Paragraph(
                f'<font size="8" color="{MUTED.hexval()}">— {cat_info[3] if cat_info else 0} diseños —</font>',
                ParagraphStyle("cat_count", fontName=FONT_B, fontSize=8, leading=11,
                              textColor=MUTED, alignment=TA_CENTER)))
        
        # Count products in category
        prod_count_in_cat += 1
        
        # ── PRODUCT PAGE (FULL PAGE) ──
        elements.append(PageBreak())
        
        # Product image (large - fills most of the page)
        img = img_cache.get(prod_name)
        if img:
            elements.append(Spacer(1, 5*mm))
            elements.append(img)
            elements.append(Spacer(1, 8*mm))
        else:
            elements.append(Spacer(1, 40*mm))
            # Placeholder text when no image
            elements.append(Paragraph(
                f'<font size="48" color="{MUTED.hexval()}">◈</font>',
                ParagraphStyle("noimg", fontName=FONT_B, fontSize=48, leading=50,
                              textColor=MUTED, alignment=TA_CENTER)))
            elements.append(Spacer(1, 10*mm))
        
        # Product info (bottom section)
        elements.append(Paragraph(prod_name, ParagraphStyle("prod_name",
            fontName=FONT_D, fontSize=22, leading=26, textColor=WHITE, alignment=TA_CENTER)))
        elements.append(Spacer(1, 3*mm))
        
        # Gold accent
        gl4 = GoldLine(40*mm)
        elements.append(gl4)
        elements.append(Spacer(1, 5*mm))
        
        # Description
        elements.append(Paragraph(desc,
            ParagraphStyle("prod_desc", fontName=FONT_B, fontSize=9.5, leading=14,
                          textColor=LIGHT, alignment=TA_CENTER, spaceAfter=6)))
        elements.append(Spacer(1, 4*mm))
        
        # Specs badge
        elements.append(Paragraph(
            f'<font size="7" color="{GOLD.hexval()}">▸ {detail}</font>',
            ParagraphStyle("prod_detail", fontName=FONT_B, fontSize=7, leading=10,
                          textColor=GOLD, alignment=TA_CENTER)))
        elements.append(Paragraph(
            f'<font size="7" color="{MUTED.hexval()}">{specs}</font>',
            ParagraphStyle("prod_specs", fontName=FONT_B, fontSize=7, leading=10,
                          textColor=MUTED, alignment=TA_CENTER)))
    
    # ═══════════════════════════════════════
    # CONTRA PORTADA
    # ═══════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Spacer(1, 55*mm))
    
    elements.append(Paragraph("NE", ParagraphStyle("end_ne",
        fontName=FONT_D, fontSize=60, leading=50, textColor=WHITE, alignment=TA_CENTER)))
    elements.append(Paragraph("O", ParagraphStyle("end_o",
        fontName=FONT_D, fontSize=60, leading=50, textColor=GOLD, alignment=TA_CENTER)))
    elements.append(Spacer(1, 25*mm))
    
    end_info = [
        "NEO Objects",
        "Madrid, España",
        "",
        "Fabricación bajo pedido",
        "Materiales: PLA premium, PETG satinado, Resina HD",
        "Acabado: Capa de 0.08mm",
        "Envío: 24-72h a península",
        "Envío gratis desde 100€",
        "",
        "Condiciones especiales para tiendas y mayoristas",
        "Pedido mínimo: 12 unidades por diseño",
        "Descuentos por volumen disponibles",
    ]
    
    for line in end_info:
        c = ParagraphStyle("end_line", fontName=FONT_B, fontSize=9, leading=14,
                          textColor=MUTED, alignment=TA_CENTER)
        if line.startswith("Condiciones") or line.startswith("Descuentos"):
            c.textColor = GOLD
        if line == "":
            elements.append(Spacer(1, 4*mm))
        else:
            elements.append(Paragraph(line, c))
    
    elements.append(Spacer(1, 15*mm))
    gl5 = GoldLine(W*0.3)
    elements.append(gl5)
    elements.append(Spacer(1, 10*mm))
    
    elements.append(Paragraph("https://magodago.github.io/neo3d-objects/",
        ParagraphStyle("end_web", fontName=FONT_B, fontSize=8, leading=12,
                      textColor=GOLD_LIGHT, alignment=TA_CENTER)))
    
    # ─── BUILD ───
    doc.build(elements, onFirstPage=page_bg, onLaterPages=page_bg)
    
    kb = os.path.getsize(OUTPUT_PATH) / 1024
    pages_est = len(PRODUCTS) + 2 + len(CATEGORIES) + 1  # products + cover + categories + back
    print(f"\n✅ Catálogo PREMIUM generado:")
    print(f"   {OUTPUT_PATH}")
    print(f"   {kb:.0f} KB · ~{pages_est} páginas")
    print(f"   {len(img_cache)}/{len(PRODUCTS)} productos con imagen")
    
    if len(img_cache) < len(PRODUCTS):
        missing = [p[1] for p in PRODUCTS if p[1] not in img_cache]
        print(f"\n⚠ Productos sin imagen ({len(missing)}):")
        for p in missing:
            print(f"   • {p}")

if __name__ == "__main__":
    build()
