"""Luxury brand catalog style product cards for fashion order system"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

STYLES_DIR = "/opt/data/workspace/fashion-order-system/uploads/styles"
os.makedirs(STYLES_DIR, exist_ok=True)

W, H = 600, 800

try:
    FONT_CN = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 20)
    FONT_EN = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    FONT_IT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 10)
except:
    FONT_CN = FONT_EN = FONT_IT = ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def create_catalog_image(main_hex, accent_hex, name, gtype_label, gtype_cn):
    """Create luxury product catalog card"""
    main_rgb = hex_to_rgb(main_hex)
    accent_rgb = hex_to_rgb(accent_hex)
    
    img = Image.new('RGB', (W, H), (248, 245, 240))
    draw = ImageDraw.Draw(img)
    
    # Determine text color based on brightness
    b = (main_rgb[0]*299 + main_rgb[1]*587 + main_rgb[2]*114) / 1000
    text_c = (255, 255, 255) if b < 150 else (30, 30, 30)
    muted_c = (200, 200, 200) if b < 150 else (120, 120, 120)
    
    # Main color block - fabric showcase area
    # Create a rich gradient background for the color area
    block_margin = 15
    block_top = 25
    block_h = 560
    block_bottom = block_top + block_h
    
    # Draw gradient block
    for y in range(block_top, block_bottom):
        ratio = (y - block_top) / block_h
        # Smooth gradient from main color to slightly lighter
        r = int(main_rgb[0] + (accent_rgb[0] - main_rgb[0]) * ratio * 0.6)
        g = int(main_rgb[1] + (accent_rgb[1] - main_rgb[1]) * ratio * 0.6)
        b_val = int(main_rgb[2] + (accent_rgb[2] - main_rgb[2]) * ratio * 0.6)
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b_val = max(0, min(255, b_val))
        draw.line([(block_margin, y), (W-block_margin, y)], fill=(r, g, b_val))
    
    # Subtle inner shadow at top of block
    for i in range(8):
        alpha = int(30 * (1 - i/8))
        draw.line([(block_margin, block_top+i), (W-block_margin, block_top+i)], 
                  fill=(0, 0, 0, alpha))
    
    # Garment type label - centered at top of color block
    draw.text((W//2, block_top + 35), gtype_label.upper(), 
              fill=muted_c, font=FONT_EN, anchor="mt", stroke_width=0)
    
    # Decorative line under type
    draw.line([(W//2-20, block_top + 50), (W//2+20, block_top + 50)], 
              fill=muted_c, width=1)
    
    # Color name - large, central on the block
    name_parts = name.split('-')
    gcolor = name_parts[-1] if len(name_parts) > 1 else name
    cname = gtype_cn + " · " + gcolor
    
    # Draw the full garment name near center
    draw.text((W//2, block_top + block_h//2 - 20), 
              gtype_cn, fill=text_c, font=FONT_CN, anchor="mm")
    
    # Color name slightly below
    draw.text((W//2, block_top + block_h//2 + 20), 
              gcolor, fill=text_c, font=FONT_CN, anchor="mm")
    
    # Bottom section - clean white area with details
    info_top = block_bottom + 10
    
    # Draw subtle decorative elements
    draw.line([(W//2-25, info_top + 10), (W//2+25, info_top + 10)], 
              fill=(210, 208, 204), width=1)
    
    # Full name
    draw.text((W//2, info_top + 35), name, fill=(80, 80, 80), font=FONT_CN, anchor="mt")
    draw.text((W//2, info_top + 58), "LUNA ATELIER", fill=(190, 190, 190), font=FONT_EN, anchor="mt")
    
    # Add a subtle fabric texture pattern on the color block (diagonal lines)
    texture_color = (255, 255, 255)
    alpha_val = 8
    for i in range(0, block_h, 6):
        y = block_top + i
        for x in range(block_margin, W-block_margin, 8):
            draw.point((x + (i%12)//2, y), fill=(255, 255, 255, 6))
    
    return img

# Garment data
garments = [
    ("西装外套-米白", "#F5F0EB", "#E8E0D4", "blazer", "西装外套"),
    ("西装外套-黑色", "#2A2A2A", "#1A1A1A", "blazer", "西装外套"),
    ("西装外套-藏青", "#1B2A4A", "#0E1A30", "blazer", "西装外套"),
    ("西装外套-驼色", "#C9A96E", "#B89550", "blazer", "西装外套"),
    ("西装外套-灰色", "#8C8C8C", "#707070", "blazer", "西装外套"),
    ("西装外套-卡其", "#BFA58A", "#A88A70", "blazer", "西装外套"),
    ("西装外套-酒红", "#6B2D3E", "#4A1C28", "blazer", "西装外套"),
    ("连衣裙-黑色", "#2A2A2A", "#1A1A1A", "dress", "连衣裙"),
    ("连衣裙-红色", "#8B1A1A", "#601010", "dress", "连衣裙"),
    ("连衣裙-碎花", "#F0E6D3", "#E0D0B8", "dress", "连衣裙"),
    ("连衣裙-米白", "#F8F4EF", "#ECE4D8", "dress", "连衣裙"),
    ("连衣裙-藏青", "#1B2A4A", "#0E1A30", "dress", "连衣裙"),
    ("连衣裙-粉色", "#F0D4D4", "#E0B8B8", "dress", "连衣裙"),
    ("真丝衬衫-白色", "#F5F5F5", "#E8E8E8", "blouse", "真丝衬衫"),
    ("真丝衬衫-香槟", "#E8DDC8", "#D8CAB0", "blouse", "真丝衬衫"),
    ("真丝衬衫-黑色", "#2A2A2A", "#1A1A1A", "blouse", "真丝衬衫"),
    ("真丝衬衫-雾蓝", "#8FA8C8", "#7088A8", "blouse", "真丝衬衫"),
    ("真丝衬衫-豆沙", "#C4958A", "#A8786C", "blouse", "真丝衬衫"),
    ("真丝衬衫-墨绿", "#2D4A3B", "#1A3028", "blouse", "真丝衬衫"),
    ("大衣-驼色", "#C9A96E", "#B89550", "coat", "大衣"),
    ("大衣-黑色", "#2A2A2A", "#1A1A1A", "coat", "大衣"),
    ("大衣-灰色", "#7A7A7A", "#606060", "coat", "大衣"),
    ("大衣-藏青", "#1B2A4A", "#0E1A30", "coat", "大衣"),
    ("大衣-焦糖", "#8B5E3C", "#6E4428", "coat", "大衣"),
    ("风衣-卡其", "#C4A882", "#A88A68", "trench", "风衣"),
    ("风衣-米白", "#F0EBE0", "#E0D8C8", "trench", "风衣"),
    ("羊毛衫-燕麦", "#E8DDC8", "#D8CAB0", "sweater", "羊毛衫"),
    ("羊毛衫-灰色", "#9A9A9A", "#7A7A7A", "sweater", "羊毛衫"),
    ("羊毛衫-酒红", "#6B2D3E", "#4A1C28", "sweater", "羊毛衫"),
    ("羊毛衫-墨绿", "#2D4A3B", "#1A3028", "sweater", "羊毛衫"),
    ("半身裙-黑色", "#2A2A2A", "#1A1A1A", "skirt", "半身裙"),
    ("半身裙-米白", "#F5F0EB", "#E8E0D4", "skirt", "半身裙"),
    ("半身裙-花呢", "#D4C8B8", "#C0B0A0", "skirt", "半身裙"),
    ("半身裙-驼色", "#C9A96E", "#B89550", "skirt", "半身裙"),
    ("阔腿裤-黑色", "#2A2A2A", "#1A1A1A", "pants", "阔腿裤"),
    ("阔腿裤-藏青", "#1B2A4A", "#0E1A30", "pants", "阔腿裤"),
    ("阔腿裤-卡其", "#BFA58A", "#A88A70", "pants", "阔腿裤"),
    ("阔腿裤-灰色", "#8C8C8C", "#707070", "pants", "阔腿裤"),
    ("小香风套装", "#D4C8B0", "#C0B0A0", "suit", "套装"),
    ("西装套裙", "#1B2A4A", "#0E1A30", "suit", "套装"),
    ("西装套裤", "#3A3A3A", "#282828", "suit", "套装"),
    ("夹克-军绿", "#4A5E3A", "#304028", "jacket", "夹克"),
    ("夹克-黑色", "#2A2A2A", "#1A1A1A", "jacket", "夹克"),
    ("马甲-米白", "#F5F0EB", "#E8E0D4", "vest", "马甲"),
    ("马甲-灰色", "#8C8C8C", "#707070", "vest", "马甲"),
    ("针织开衫-粉色", "#F0D4D4", "#E0B8B8", "cardigan", "针织开衫"),
    ("针织开衫-驼色", "#C9A96E", "#B89550", "cardigan", "针织开衫"),
    ("卫衣-灰色", "#7A7A7A", "#606060", "hoodie", "卫衣"),
    ("卫衣-黑色", "#2A2A2A", "#1A1A1A", "hoodie", "卫衣"),
    ("衬衫-条纹蓝", "#D8E0EC", "#B8C8DC", "shirt", "衬衫"),
]

for i, (name, main_h, accent_h, gtype_label, gtype_cn) in enumerate(garments, 1):
    img = create_catalog_image(main_h, accent_h, name, gtype_label, gtype_cn)
    path = os.path.join(STYLES_DIR, f"style_{i}.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"[{i:02d}/50] {name}")

print(f"\n✅ 已生成 {len(garments)} 张产品目录卡片")
