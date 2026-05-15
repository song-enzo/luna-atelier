"""Seed database with 8 clean categories, 1 style each with 2-3 real photos"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from app import app, db
from models import User, Style

STYLES = [
    # 8 categories, 1 style each
    ("连衣裙", "连衣裙", "优雅女式连衣裙，V领收腰设计", "涤纶60% 粘纤40%", 69.00, "dress"),
    ("衬衫", "衬衫", "经典女式衬衫，简约百搭", "棉60% 涤纶40%", 55.00, "shirt"),
    ("外套", "外套", "时尚女式外套，气质通勤", "涤纶65% 棉35%", 89.00, "jacket"),
    ("裤类", "裤类", "高腰女式长裤，垂感面料", "涤纶60% 粘纤40%", 55.00, "pants"),
    ("裙类", "裙类", "女式半身裙，优雅飘逸", "涤纶70% 粘纤30%", 45.00, "skirt"),
    ("大衣", "大衣", "长款女式大衣，保暖有型", "羊毛80% 涤纶20%", 180.00, "coat"),
    ("背心", "背心", "女式背心，内搭外穿皆可", "棉50% 涤纶50%", 35.00, "vest"),
    ("套装", "套装", "女式西装套装，干练职业", "涤纶65% 棉35%", 128.00, "suit"),
]

def img_path(code, n):
    """Returns path relative to static/ like images/dress_1.jpg"""
    return f"images/{code}_{n}.jpg"

def gallery_list(code, total=3):
    """Return gallery images for a style (all except primary)"""
    paths = []
    for n in range(2, total + 1):
        p = img_path(code, n)
        full = os.path.join(os.path.dirname(__file__), 'static', p)
        if os.path.exists(full):
            paths.append(p)
    return json.dumps(paths)

def seed():
    with app.app_context():
        db.create_all()

        # Check admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', nickname='管理员', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)

        # Check if already seeded with new system
        existing = Style.query.count()
        first = Style.query.first()
        if existing == 8 and first and first.code == '连衣裙':
            print(f"✅ 已有 8 个新款式，跳过导入")
            return

        # Clear old styles (re-seed)
        Style.query.delete()

        for idx, (name, desc, fabric, price, img_code) in enumerate(
            [(s[1], s[2], s[3], s[4], s[5]) for s in STYLES]
        ):
            code = STYLES[idx][0]  # category name as code
            primary = img_path(img_code, 1)
            gallery = gallery_list(img_code)
            s = Style(
                name=name, code=code, description=fabric,
                fabric_info=fabric, image_path=primary,
                gallery=gallery, price=price
            )
            db.session.add(s)

        db.session.commit()
        print(f"✅ 已导入 {len(STYLES)} 个款式（8品类各1款）")

if __name__ == '__main__':
    seed()
    print("完成")
