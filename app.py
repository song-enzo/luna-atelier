import os, uuid, json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Style, Order, OrderItem, FabricImage, OrderLog, init_db, generate_order_no, STATUS_MAP

app = Flask(__name__)
app.config['SECRET_KEY'] = 'luna-atelier-secret-2026'
# Use PostgreSQL from Render if DATABASE_URL is set, otherwise SQLite for local dev
db_url = os.environ.get('DATABASE_URL', 'sqlite:///fashion.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value) if value else []
    except:
        return []
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file, subdir=''):
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(app.config['UPLOAD_FOLDER'], subdir, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file.save(path)
    return os.path.join(subdir, name)

# ========== 登录 ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('guest_orders'))
        flash('用户名或密码错误', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('guest_styles'))
    return redirect(url_for('login'))

# ========== 客人端 ==========

@app.route('/guest/styles')
@login_required
def guest_styles():
    query = Style.query.filter_by(is_active=True)
    cat = request.args.get('cat', '')
    q = request.args.get('q', '').strip()
    
    # Category filter
    cat_map = {
        'blazer': ['西装'],
        'dress': ['连衣裙'],
        'coat': ['大衣', '风衣'],
        'top': ['真丝衬衫', '羊毛衫', '衬衫', '针织开衫', '马甲'],
        'pants': ['阔腿裤', '卫衣', '夹克'],
        'skirt': ['半身裙'],
        'suit': ['套装'],
    }
    if cat and cat in cat_map:
        import functools
        filters = [Style.name.like(f'%{k}%') for k in cat_map[cat]]
        query = query.filter(functools.reduce(lambda a, b: a | b, filters))
    
    # Search by name or code
    if q:
        query = query.filter(
            db.or_(Style.name.like(f'%{q}%'), Style.code.like(f'%{q}%'))
        )
    
    # Sort by newest first
    styles = query.order_by(Style.created_at.desc()).all()
    return render_template('guest_styles.html', styles=styles, cat=cat, q=q)

@app.route('/guest/order/<int:style_id>', methods=['GET', 'POST'])
@login_required
def new_order(style_id):
    style = Style.query.get_or_404(style_id)
    if request.method == 'POST':
        items_data = json.loads(request.form.get('items', '[]'))
        if not items_data:
            flash('请至少添加一个花色', 'error')
            return redirect(url_for('new_order', style_id=style_id))
        
        size = request.form.get('size', 'M')
        remark = request.form.get('remark', '')
        
        order = Order(
            order_no=generate_order_no(),
            user_id=current_user.id,
            style_id=style.id,
            status='pending',
            size=size,
            total_qty=sum(item['qty'] for item in items_data),
            remark=remark,
        )
        db.session.add(order)
        db.session.flush()
        
        for i, item in enumerate(items_data):
            swatch_path = ''
            if item.get('swatch_data'):
                import base64
                img_data = base64.b64decode(item['swatch_data'].split(',')[1])
                swatch_name = f"{uuid.uuid4().hex}.png"
                swatch_path = os.path.join('swatches', swatch_name)
                with open(os.path.join(app.config['UPLOAD_FOLDER'], 'swatches', swatch_name), 'wb') as f:
                    f.write(img_data)
            
            oi = OrderItem(
                order_id=order.id,
                color_name=item.get('color_name', ''),
                swatch_image=swatch_path,
                quantity=item['qty'],
                sort_order=i
            )
            db.session.add(oi)
        
        log_entry = OrderLog(
            order_id=order.id, status_from='', status_to='pending',
            note='订单创建', operator=current_user.nickname or current_user.username
        )
        db.session.add(log_entry)
        db.session.commit()
        flash('订单提交成功！', 'success')
        return redirect(url_for('guest_order_detail', order_id=order.id))
    
    return render_template('new_order.html', style=style, STATUS_MAP=STATUS_MAP)

@app.route('/guest/orders')
@login_required
def guest_orders():
    status_filter = request.args.get('status', '')
    query = Order.query.filter_by(user_id=current_user.id)
    if status_filter in STATUS_MAP:
        query = query.filter_by(status=status_filter)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('guest_orders.html', orders=orders, STATUS_MAP=STATUS_MAP, status_filter=status_filter)

@app.route('/guest/order/detail/<int:order_id>')
@login_required
def guest_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('无权查看此订单', 'error')
        return redirect(url_for('guest_orders'))
    logs = OrderLog.query.filter_by(order_id=order.id).order_by(OrderLog.created_at.desc()).all()
    return render_template('guest_order_detail.html', order=order, STATUS_MAP=STATUS_MAP, logs=logs)

@app.route('/guest/order/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_receipt(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return jsonify({'error': '无权操作'}), 403
    if order.status != 'shipped':
        return jsonify({'error': '当前状态不可确认收货'}), 400
    
    old_status = order.status
    order.status = 'completed'
    log = OrderLog(
        order_id=order.id, status_from=old_status, status_to='completed',
        note='客人确认收货', operator=current_user.nickname or current_user.username
    )
    db.session.add(log)
    db.session.commit()
    flash('已确认收货，订单已完成', 'success')
    return redirect(url_for('guest_order_detail', order_id=order.id))

# ========== 上传接口 ==========

@app.route('/upload/fabric', methods=['POST'])
@login_required
def upload_fabric():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file and allowed_file(file.filename):
        path = save_upload(file, 'fabrics')
        fi = FabricImage(user_id=current_user.id, image_path=path)
        db.session.add(fi)
        db.session.commit()
        return jsonify({'path': path, 'url': url_for('uploaded_file', filename=path)})
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/upload/swatch', methods=['POST'])
@login_required
def upload_swatch():
    data = request.json
    if not data or not data.get('image'):
        return jsonify({'error': 'No image data'}), 400
    import base64
    img_data = base64.b64decode(data['image'].split(',')[1])
    name = f"{uuid.uuid4().hex}.png"
    swatch_path = os.path.join('swatches', name)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'swatches', name), 'wb') as f:
        f.write(img_data)
    return jsonify({'path': swatch_path, 'url': url_for('uploaded_file', filename=swatch_path)})

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ========== 管理后台 ==========

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    active_orders = Order.query.filter(Order.status.in_(['cutting', 'sewing', 'qc'])).count()
    shipped_orders = Order.query.filter_by(status='shipped').count()
    completed_orders = Order.query.filter_by(status='completed').count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin_dashboard.html',
        total_orders=total_orders, pending_orders=pending_orders,
        active_orders=active_orders, shipped_orders=shipped_orders,
        completed_orders=completed_orders,
        recent_orders=recent_orders, STATUS_MAP=STATUS_MAP)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    q = request.args.get('q', '')
    status_filter = request.args.get('status', '')
    user_filter = request.args.get('user', '')
    
    query = Order.query
    if q:
        query = query.filter(Order.order_no.like(f'%{q}%'))
    if status_filter:
        query = query.filter(Order.status == status_filter)
    if user_filter:
        query = query.filter(Order.user_id == int(user_filter))
    
    orders = query.order_by(Order.created_at.desc()).all()
    users = User.query.filter_by(role='guest').all()
    return render_template('admin_orders.html', orders=orders,
        STATUS_MAP=STATUS_MAP, users=users,
        q=q, status_filter=status_filter, user_filter=user_filter)

@app.route('/admin/order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def admin_order_detail(order_id):
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_status':
            new_status = request.form.get('status')
            note = request.form.get('note', '')
            old_status = order.status
            order.status = new_status
            log = OrderLog(
                order_id=order.id, status_from=old_status, status_to=new_status,
                note=note, operator=current_user.nickname or current_user.username
            )
            db.session.add(log)
        elif action == 'update_amount':
            order.total_amount = float(request.form.get('total_amount', 0))
            order.paid_amount = float(request.form.get('paid_amount', 0))
        elif action == 'update_items':
            items_data = json.loads(request.form.get('items', '[]'))
            OrderItem.query.filter_by(order_id=order.id).delete()
            for i, item in enumerate(items_data):
                oi = OrderItem(
                    order_id=order.id, color_name=item.get('color_name', ''),
                    swatch_image=item.get('swatch_image', ''),
                    quantity=item.get('qty', 0), sort_order=i
                )
                db.session.add(oi)
            order.total_qty = sum(item.get('qty', 0) for item in items_data)
        
        db.session.commit()
        flash('更新成功', 'success')
        return redirect(url_for('admin_order_detail', order_id=order.id))
    
    logs = OrderLog.query.filter_by(order_id=order.id).order_by(OrderLog.created_at.desc()).all()
    return render_template('admin_order_detail.html',
        order=order, STATUS_MAP=STATUS_MAP, logs=logs)

@app.route('/admin/styles', methods=['GET', 'POST'])
@login_required
def admin_styles():
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    if request.method == 'POST':
        style = Style(
            name=request.form.get('name'),
            code=request.form.get('code'),
            description=request.form.get('description'),
            fabric_info=request.form.get('fabric_info'),
            price=float(request.form.get('price', 0))
        )
        if request.files.get('image') and allowed_file(request.files['image'].filename):
            style.image_path = save_upload(request.files['image'], 'styles')
        db.session.add(style)
        db.session.commit()
        flash('款式添加成功', 'success')
        return redirect(url_for('admin_styles'))
    
    styles = Style.query.order_by(Style.created_at.desc()).all()
    return render_template('admin_styles.html', styles=styles)

@app.route('/admin/style/<int:id>/edit', methods=['POST'])
@login_required
def admin_style_edit(id):
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    style = Style.query.get_or_404(id)
    style.name = request.form.get('name')
    style.code = request.form.get('code')
    style.description = request.form.get('description')
    style.fabric_info = request.form.get('fabric_info')
    style.price = float(request.form.get('price', 0))
    if request.files.get('image') and allowed_file(request.files['image'].filename):
        style.image_path = save_upload(request.files['image'], 'styles')
    db.session.commit()
    flash('款式已更新', 'success')
    return redirect(url_for('admin_styles'))

@app.route('/admin/style/<int:id>/delete', methods=['POST'])
@login_required
def admin_style_delete(id):
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    style = Style.query.get_or_404(id)
    style.is_active = False
    db.session.commit()
    flash('款式已下架', 'success')
    return redirect(url_for('admin_styles'))

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    if request.method == 'POST':
        user = User(
            username=request.form.get('username'),
            nickname=request.form.get('nickname'),
            phone=request.form.get('phone'),
            role='guest'
        )
        user.set_password(request.form.get('password', '123456'))
        db.session.add(user)
        db.session.commit()
        flash(f'客人账号 {user.username} 创建成功', 'success')
        return redirect(url_for('admin_users'))
    
    users = User.query.filter_by(role='guest').all()
    return render_template('admin_users.html', users=users)

# ========== Mockup ==========

@app.route('/mockup')
def mockup():
    return render_template('mockup.html')

# ========== 启动 ==========

if __name__ == '__main__':
    init_db(app)
    # Auto-seed styles on Render (fresh DB)
    from seed import seed
    seed()
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port, debug=True)
