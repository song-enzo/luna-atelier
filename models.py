from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='guest')  # admin / guest
    is_active = db.Column(db.Boolean, default=True)
    last_login_ip = db.Column(db.String(45), default='')
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Style(db.Model):
    __tablename__ = 'styles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50))
    description = db.Column(db.Text)
    fabric_info = db.Column(db.String(500))
    image_path = db.Column(db.String(300))
    gallery = db.Column(db.Text, default='[]')  # JSON array of extra image paths
    colors = db.Column(db.Text, default='[]')  # JSON array of color strings
    fabric_id = db.Column(db.Integer, db.ForeignKey('fabrics.id'), nullable=True)
    price = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    orders = db.relationship('Order', backref='style', lazy=True)
    fabric = db.relationship('Fabric', backref='styles', lazy=True)

class Fabric(db.Model):
    __tablename__ = 'fabrics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    composition = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.now)

# 状态流转: pending → confirmed → cutting → sewing → qc → shipped → completed
STATUS_MAP = {
    'pending': '待确认',
    'confirmed': '已确认',
    'cutting': '裁剪中',
    'sewing': '车缝中',
    'qc': '质检中',
    'shipped': '运输中',
    'completed': '已完成',
}

def generate_order_no():
    """生成订单号: 编号-YYMMDDHH-XXXX"""
    now = datetime.now()
    prefix = now.strftime('编号-%y%m%d%H-')
    last = Order.query.filter(
        Order.order_no.like(f'{prefix}%')
    ).order_by(Order.id.desc()).first()
    if last:
        seq = int(last.order_no.split('-')[-1]) + 1
    else:
        seq = 1
    return f'{prefix}{seq:04d}'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    style_id = db.Column(db.Integer, db.ForeignKey('styles.id'), nullable=False)
    status = db.Column(db.String(30), default='pending')
    size = db.Column(db.String(30), default='M')
    total_qty = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Float, default=0)
    paid_amount = db.Column(db.Float, default=0)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    color_name = db.Column(db.String(100))
    swatch_image = db.Column(db.String(300))
    quantity = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)

class FabricImage(db.Model):
    __tablename__ = 'fabric_images'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    style_id = db.Column(db.Integer, db.ForeignKey('styles.id'), nullable=True)
    image_path = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class OrderLog(db.Model):
    __tablename__ = 'order_logs'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status_from = db.Column(db.String(30))
    status_to = db.Column(db.String(30))
    note = db.Column(db.String(500))
    operator = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)

class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip = db.Column(db.String(45), default='')
    user_agent = db.Column(db.String(500), default='')
    login_at = db.Column(db.DateTime, default=datetime.now)
    success = db.Column(db.Boolean, default=True)

def init_db(app):
    with app.app_context():
        db.create_all()
        # Migrations for existing tables
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        
        # Gallery column migration
        columns = [c['name'] for c in inspector.get_columns('styles')]
        if 'gallery' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE styles ADD COLUMN gallery TEXT DEFAULT \'[]\''))
                conn.commit()
        if 'colors' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE styles ADD COLUMN colors TEXT DEFAULT \'[]\''))
                conn.commit()
        if 'fabric_id' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE styles ADD COLUMN fabric_id INTEGER DEFAULT NULL'))
                conn.commit()
        
        # User columns migration
        user_cols = [c['name'] for c in inspector.get_columns('users')]
        if 'last_login_ip' not in user_cols:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE users ADD COLUMN last_login_ip VARCHAR(45) DEFAULT \'\''))
                from sqlalchemy import text as sa_text
                if 'postgresql' in db.engine.url.drivername:
                    conn.execute(sa_text('ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP DEFAULT NULL'))
                else:
                    conn.execute(text('ALTER TABLE users ADD COLUMN last_login_at DATETIME DEFAULT NULL'))
                conn.commit()
        
        # FabricImage columns migration
        fi_cols = [c['name'] for c in inspector.get_columns('fabric_images')]
        if 'style_id' not in fi_cols:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE fabric_images ADD COLUMN style_id INTEGER DEFAULT NULL'))
                conn.commit()
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                nickname='管理员',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
