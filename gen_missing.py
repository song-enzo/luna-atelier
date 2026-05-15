"""Copy existing images to fill missing slots - all 8 categories x 4 variants x 4 images"""
import os, shutil

STATIC = os.path.join(os.path.dirname(__file__), 'static', 'images')
categories = ['dress', 'jacket', 'coat', 'knitwear', 'shirt', 'trouser', 'skirt', 'suit']

filled = 0
for cat in categories:
    existing = {}
    # Map existing images
    for variant in range(1, 5):
        for img_num in range(1, 5):
            fname = f"{cat}_{variant}_{img_num}.jpg"
            fpath = os.path.join(STATIC, fname)
            if os.path.exists(fpath) and os.path.getsize(fpath) > 500:
                existing[(variant, img_num)] = fpath
    
    # Find missing slots and fill them
    for variant in range(1, 5):
        for img_num in range(1, 5):
            fname = f"{cat}_{variant}_{img_num}.jpg"
            fpath = os.path.join(STATIC, fname)
            if os.path.exists(fpath) and os.path.getsize(fpath) > 500:
                continue
            
            # Find a source: try same variant first, then same img_num, then any
            src = None
            # Same variant
            for v, p in existing.items():
                if v[0] == variant and v != (variant, img_num):
                    src = p
                    break
            if not src:
                for v, p in existing.items():
                    if v[1] == img_num:
                        src = p
                        break
            if not src:
                src = list(existing.values())[0] if existing else None
            
            if src:
                shutil.copy2(src, fpath)
                filled += 1
                print(f"Filled: {fname} <- {os.path.basename(src)}")
            else:
                print(f"WARNING: No source for {fname}")

# Verify all 128 images exist
total = 0
for cat in categories:
    for variant in range(1, 5):
        for img_num in range(1, 5):
            fname = f"{cat}_{variant}_{img_num}.jpg"
            fpath = os.path.join(STATIC, fname)
            if os.path.exists(fpath):
                total += 1
            else:
                print(f"MISSING: {fname}")

print(f"\nTotal images: {total}/128, Filled: {filled}")
