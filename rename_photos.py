#!/usr/bin/env python3
"""
Rename downloaded Sandro photos to match LUNA ATELIER's naming convention.
Old naming (my files): category_product_viewX.jpg (e.g. dresses_1_view1.jpg)
Target naming: code_product_viewX.jpg (e.g. dress_1_1.jpg)

The seed.py expects:
  images/dress_1_1.jpg (primary), dress_1_2.jpg through dress_1_4.jpg (gallery)
  images/trouser_1_1.jpg through trouser_4_4.jpg
  etc.
"""
import os, shutil

SRC = "/opt/data/workspace/fashion-order-system/static/images/products"
DST = "/opt/data/workspace/fashion-order-system/static/images"

# Category name mapping: my_names → seed.py codes
MAP = {
    "dresses":  "dress",
    "shirts":   "shirt",
    "jackets":  "jacket",
    "coats":    "coat",
    "knitwear": "knitwear",
    "pants":    "trouser",
    "skirts":   "skirt",
    "suits":    "suit",
}

renamed = []
for fname in sorted(os.listdir(SRC)):
    if not fname.endswith('.jpg'):
        continue
    
    # Parse: dresses_1_view1.jpg → pieces = ['dresses', '1', 'view1.jpg']
    parts = fname.replace('.jpg', '').split('_')
    if len(parts) != 3:
        print(f"  ⚠ Skipping unexpected format: {fname}")
        continue
    
    cat_my, prod_num, view_str = parts
    view_num = view_str.replace('view', '')
    
    if cat_my not in MAP:
        print(f"  ⚠ Unknown category: {cat_my}")
        continue
    
    cat_target = MAP[cat_my]
    new_name = f"{cat_target}_{prod_num}_{view_num}.jpg"
    
    src_path = os.path.join(SRC, fname)
    dst_path = os.path.join(DST, new_name)
    
    # Check if destination already exists (from old downloads)
    if os.path.exists(dst_path):
        print(f"  ~ Overwriting: {new_name}")
    
    shutil.copy2(src_path, dst_path)
    renamed.append(new_name)
    print(f"  ✓ {fname} → {new_name}")

print(f"\nTotal renamed: {len(renamed)}")

# Verify all expected files exist
EXPECTED = []
for cat in ['dress', 'jacket', 'coat', 'knitwear', 'shirt', 'trouser', 'skirt', 'suit']:
    for prod in [1,2,3,4]:
        for view in [1,2,3,4]:
            EXPECTED.append(f"{cat}_{prod}_{view}.jpg")

missing = [f for f in EXPECTED if not os.path.exists(os.path.join(DST, f))]
if missing:
    print(f"\nMissing {len(missing)} files:")
    for m in missing:
        print(f"  ✗ {m}")
else:
    print(f"\n✅ All {len(EXPECTED)} expected files present!")
