"""Generate remaining 42 premium catalog images (styles 9-50)"""
import os
from PIL import Image, ImageDraw, ImageFont

STYLES_DIR = "/opt/data/workspace/fashion-order-system/uploads/styles"
W, H = 600, 800

try:
    FONT_CN = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 22)
    FONT_EN = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except:
    FONT_CN = FONT_EN = ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

garments = [
    # (index, name, main_hex, accent_hex, gtype)
    (9, "连衣裙-红色", "#8B1A1A", "#C41E3A", "DRESS"),
    (10, "连衣裙-碎花", "#F0E6D3", "#E8D8C0", "DRESS"),
    (11, "连衣裙-米白", "#F8F4EF", "#ECE4D8", "DRESS"),
    (12, "连衣裙-藏青", "#1B2A4A", "#2C3E6B", "DRESS"),
    (13, "连衣裙-粉色", "#F0D4D4", "#E8C0C0", "DRESS"),
    (14, "真丝衬衫-白色", "#F5F5F5", "#E8E8E8", "BLOUSE"),
    (15, "真丝衬衫-香槟", "#E8DDC8", "#D8CAB0", "BLOUSE"),
    (16, "真丝衬衫-黑色", "#2A2A2A", "#1A1A1A", "BLOUSE"),
    (17, "真丝衬衫-雾蓝", "#8FA8C8", "#7090B0", "BLOUSE"),
    (18, "真丝衬衫-豆沙", "#C4958A", "#B08070", "BLOUSE"),
    (19, "真丝衬衫-墨绿", "#2D4A3B", "#1A3028", "BLOUSE"),
    (20, "大衣-驼色", "#C9A96E", "#D8BC87", "COAT"),
    (21, "大衣-黑色", "#2A2A2A", "#1A1A1A", "COAT"),
    (22, "大衣-灰色", "#7A7A7A", "#606060", "COAT"),
    (23, "大衣-藏青", "#1B2A4A", "#2C3E6B", "COAT"),
    (24, "大衣-焦糖", "#8B5E3C", "#A07040", "COAT"),
    (25, "风衣-卡其", "#C4A882", "#D4BCA0", "TRENCH"),
    (26, "风衣-米白", "#F0EBE0", "#E0D8C8", "TRENCH"),
    (27, "羊毛衫-燕麦", "#E8DDC8", "#D8CAB0", "SWEATER"),
    (28, "羊毛衫-灰色", "#9A9A9A", "#7A7A7A", "SWEATER"),
    (29, "羊毛衫-酒红", "#6B2D3E", "#8B3A4F", "SWEATER"),
    (30, "羊毛衫-墨绿", "#2D4A3B", "#3A5E4A", "SWEATER"),
    (31, "半身裙-黑色", "#2A2A2A", "#1A1A1A", "SKIRT"),
    (32, "半身裙-米白", "#F5F0EB", "#E8E0D4", "SKIRT"),
    (33, "半身裙-花呢", "#D4C8B8", "#C0B0A0", "SKIRT"),
    (34, "半身裙-驼色", "#C9A96E", "#D8BC87", "SKIRT"),
    (35, "阔腿裤-黑色", "#2A2A2A", "#1A1A1A", "PANTS"),
    (36, "阔腿裤-藏青", "#1B2A4A", "#2C3E6B", "PANTS"),
    (37, "阔腿裤-卡其", "#BFA58A", "#D4BCA0", "PANTS"),
    (38, "阔腿裤-灰色", "#8C8C8C", "#707070", "PANTS"),
    (39, "小香风套装", "#D4C8B0", "#C0B0A0", "SUIT"),
    (40, "西装套裙", "#1B2A4A", "#2C3E6B", "SUIT"),
    (41, "西装套裤", "#3A3A3A", "#282828", "SUIT"),
    (42, "夹克-军绿", "#4A5E3A", "#5E7548", "JACKET"),
    (43, "夹克-黑色", "#2A2A2A", "#1A1A1A", "JACKET"),
    (44, "马甲-米白", "#F5F0EB", "#E8E0D4", "VEST"),
    (45, "马甲-灰色", "#8C8C8C", "#707070", "VEST"),
    (46, "针织开衫-粉色", "#F0D4D4", "#E8C0C0", "CARDIGAN"),
    (47, "针织开衫-驼色", "#C9A96E", "#D8BC87", "CARDIGAN"),
    (48, "卫衣-灰色", "#7A7A7A", "#606060", "HOODIE"),
    (49, "卫衣-黑色", "#2A2A2A", "#1A1A1A", "HOODIE"),
    (50, "衬衫-条纹蓝", "#D8E0EC", "#B8C8DC", "SHIRT"),
]

for idx, name, main_h, accent_h, gtype in garments:
    main_rgb = hex_to_rgb(main_h)
    accent_rgb = hex_to_rgb(accent_h)
    
    img = Image.new('RGB', (W, H), (248, 245, 240))
    draw = ImageDraw.Draw(img)
    
    b = (main_rgb[0]*299 + main_rgb[1]*587 + main_rgb[2]*114) / 1000
    text_c = (255,255,255) if b < 150 else (30,30,30)
    muted_c = (200,200,200) if b < 150 else (120,120,120)
    
    # Color block with gradient
    m = 20; top = 30; bh = 550; bot = top + bh
    for y in range(top, bot):
        r = (y-top)/bh
        cr = int(main_rgb[0] + (accent_rgb[0]-main_rgb[0])*r*0.5)
        cg = int(main_rgb[1] + (accent_rgb[1]-main_rgb[1])*r*0.5)
        cb = int(main_rgb[2] + (accent_rgb[2]-main_rgb[2])*r*0.5)
        draw.line([(m, y), (W-m, y)], fill=(max(0,min(255,cr)), max(0,min(255,cg)), max(0,min(255,cb))))
    
    # Garment type at top of block
    draw.text((W//2, top+30), gtype, fill=muted_c, font=FONT_EN, anchor="mt")
    draw.line([(W//2-20, top+48), (W//2+20, top+48)], fill=muted_c, width=1)
    
    # Chinese name - product type and color
    parts = name.split('-')
    gtype_cn = parts[0] if len(parts)>0 else name
    gcolor = parts[-1] if len(parts)>1 else ''
    
    draw.text((W//2, bot-80), gtype_cn, fill=text_c, font=FONT_CN, anchor="mm")
    if gcolor:
        draw.text((W//2, bot-45), gcolor, fill=text_c, font=FONT_CN, anchor="mm")
    
    # Bottom info area
    info_y = bot + 10
    draw.line([(W//2-25, info_y+10), (W//2+25, info_y+10)], fill=(210,208,204), width=1)
    draw.text((W//2, info_y+35), name, fill=(80,80,80), font=FONT_CN, anchor="mt")
    draw.text((W//2, info_y+58), "LUNA ATELIER · " + gtype, fill=(190,190,190), font=FONT_EN, anchor="mt")
    
    path = os.path.join(STYLES_DIR, f"style_{idx}.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"[{idx:02d}/50] {name}")

print(f"\n✅ 已完成 42 张目录卡片")
