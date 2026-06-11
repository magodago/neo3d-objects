#!/usr/bin/env python3
"""Genera imágenes placeholder premium para productos sin foto real."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os, math

OUTPUT_DIR = Path.home() / "gema_store" / "neo3d" / "_product_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 900, 900
BG = (5, 5, 8)
GOLD_RGB = (212, 175, 55)
GOLD_DARK = (180, 150, 47)
LIGHT = (240, 232, 216)
MUTED = (106, 101, 88)

# Try to load a nice font
font_large = None
font_small = None
for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
    if os.path.exists(path):
        from PIL import ImageFont
        font_large = ImageFont.truetype(path, 36)
        font_small = ImageFont.truetype(path, 20)
        break
if not font_large:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

PRODUCTS = {
    "Jarrón Ola": "⬡",
    "Portavelas Hexagonal": "✦",
    "Set 3 Portavelas": "✦",
    "Candelabro Triple": "✦",
    "Farolillo de Mesa": "✦",
    "Llavero Inicial": "🔑",
    "Set 6 Posavasos": "⬡",
}

for name, icon in PRODUCTS.items():
    safe = name.lower().replace(" ", "_").replace("í","i").replace("ó","o").replace("é","e").replace("á","a").replace("ú","u")
    path = OUTPUT_DIR / f"img_{safe}.jpg"
    
    if path.exists() and os.path.getsize(path) > 5000:
        print(f"  ⏭️ {name} (ya existe)")
        continue
    
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Gradient overlay (subtle dark vignette)
    for i in range(H):
        y_factor = 1 - (i / H) * 0.3
        x_factor = 1 - 0.15
        r = int(BG[0] * y_factor * x_factor)
        g = int(BG[1] * y_factor * x_factor)
        b = int(BG[2] * y_factor * x_factor)
        draw.line([(0, i), (W, i)], fill=(r, g, b))
    
    # Gold line across center
    line_y = H // 2 - 10
    draw.rectangle([W//4, line_y, 3*W//4, line_y+2], fill=GOLD_RGB)
    
    # Gold geometric icon (simple diamond/hexagon shape)
    cx, cy = W//2, H//2 - 40
    size = 60
    if icon == "⬡":
        # Hexagon
        pts = []
        for a in range(6):
            angle = a * 60 - 90
            px = cx + size * math.cos(math.radians(angle))
            py = cy + size * math.sin(math.radians(angle))
            pts.append((int(px), int(py)))
        draw.polygon(pts, outline=GOLD_RGB, width=4, fill=None)
        # Inner
        pts2 = []
        for a in range(6):
            angle = a * 60 - 90
            px = cx + size//2 * math.cos(math.radians(angle))
            py = cy + size//2 * math.sin(math.radians(angle))
            pts2.append((int(px), int(py)))
        draw.polygon(pts2, outline=GOLD_DARK, width=2, fill=None)
    elif icon == "✦":
        # Diamond with star
        pts = [(cx, cy-size), (cx+size//2, cy), (cx, cy+size), (cx-size//2, cy)]
        draw.polygon(pts, outline=GOLD_RGB, width=4, fill=None)
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=GOLD_RGB)
    else:
        # Simple circle
        draw.ellipse([cx-size, cy-size, cx+size, cy+size], outline=GOLD_RGB, width=3)
    
    # Gold line below icon
    line_y2 = cy + size + 40
    draw.rectangle([W//3, line_y2, 2*W//3, line_y2+2], fill=GOLD_RGB)
    
    # Product name text
    text = name.upper()
    bbox = draw.textbbox((0, 0), text, font=font_large)
    tw = bbox[2] - bbox[0]
    tx = (W - tw) // 2
    ty = line_y2 + 20
    draw.text((tx, ty), text, fill=LIGHT, font=font_large)
    
    # Subtitle
    sub = "PRÓXIMAMENTE" if "Llavero" in name or "Posavasos" in name else "DISEÑO EXCLUSIVO"
    bbox2 = draw.textbbox((0, 0), sub, font=font_small)
    tw2 = bbox2[2] - bbox2[0]
    tx2 = (W - tw2) // 2
    draw.text((tx2, ty + 50), sub, fill=MUTED, font=font_small)
    
    img.save(path, 'JPEG', quality=92)
    print(f"  ✅ {name}: {os.path.getsize(path)/1024:.0f} KB")

print("\n✅ Todas las imágenes placeholder generadas")
