import os, uuid, json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Style, Order, OrderItem, FabricImage, OrderLog, Fabric, LoginLog, init_db, generate_order_no, STATUS_MAP

# Check if PIL is available for image compression
try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    PILImage = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'luna-atelier-secret-2026'
# Use PostgreSQL from Render if DATABASE_URL is set, otherwise SQLite for local dev
db_url = os.environ.get('DATABASE_URL', 'sqlite:///fashion.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static')
UPLOAD_DIR = app.config['UPLOAD_FOLDER']

# Initialize SQLAlchemy with the app
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
    # Auto-compress images: max width 1200px, quality 0.8
    try:
        img = PILImage.open(file)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), PILImage.LANCZOS)
        img.save(path, 'JPEG' if ext.lower() in ('jpg', 'jpeg') else 'PNG', quality=80, optimize=True)
    except Exception:
        file.seek(0)
        file.save(path)
    return os.path.join(subdir, name)

# ========== 登录 ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        ip = request.remote_addr or ''
        ua = request.headers.get('User-Agent', '')
        success = False
        if user and user.check_password(request.form.get('password')):
            if user.is_active:
                login_user(user)
                success = True
                user.last_login_ip = ip
                user.last_login_at = datetime.now()
                db.session.commit()
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('guest_styles'))
            else:
                flash('账号已被停用，请联系管理员', 'error')
        else:
            flash('用户名或密码错误', 'error')
        # Log login attempt
        if user:
            log = LoginLog(user_id=user.id, ip=ip, user_agent=ua, success=success)
            db.session.add(log)
            db.session.commit()
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
    
    # Get categories from DB — collect unique base names from styles
    all_styles = Style.query.filter_by(is_active=True).all()
    categories = set()
    for s in all_styles:
        parts = s.name.split('-')
        if parts[0]:
            categories.add(parts[0])
    categories = sorted(categories)
    
    # Category filter using stored categories
    cat_map = {
        'blazer': ['西装'],
        'dress': ['连衣裙'],
        'coat': ['大衣', '风衣'],
        'top': ['真丝衬衫', '羊毛衫', '衬衫', '针织开衫', '马甲', '背心', 'T恤'],
        'pants': ['阔腿裤', '卫衣', '夹克', '裤'],
        'skirt': ['半身裙', '半裙'],
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
    
    # Sort by newest first, limit to 30
    styles = query.order_by(Style.created_at.desc()).limit(30).all()
    return render_template('guest_styles.html', styles=styles, cat=cat, q=q, categories=categories)

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
        
        # Fix: validate items_data
        validated_items = []
        for item in items_data:
            if isinstance(item, dict) and 'qty' in item:
                validated_items.append(item)
        
        if not validated_items:
            flash('订单数据无效，请重试', 'error')
            return redirect(url_for('new_order', style_id=style_id))
        
        order = Order(
            order_no=generate_order_no(),
            user_id=current_user.id,
            style_id=style.id,
            status='pending',
            size=size,
            total_qty=sum(item.get('qty', 0) for item in validated_items),
            remark=remark,
        )
        db.session.add(order)
        db.session.flush()
        
        # Save swatch images and create order items
        for i, item in enumerate(validated_items):
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
                quantity=item.get('qty', 0),
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
    
    # Get fabric history (previous fabric images for this style + all)
    fabric_images = FabricImage.query.order_by(FabricImage.created_at.desc()).all()
    # Add order count for each fabric image
    for fi in fabric_images:
        fi.order_count = OrderItem.query.filter_by(swatch_image=fi.image_path).count()
    return render_template('new_order.html', style=style, STATUS_MAP=STATUS_MAP, fabric_images=fabric_images)

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
        style_id = request.form.get('style_id')
        if style_id:
            try:
                fi.style_id = int(style_id)
            except ValueError:
                pass
        db.session.add(fi)
        db.session.commit()
        return jsonify({'path': path, 'url': url_for('uploaded_file', filename=path), 'id': fi.id})
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

@app.route('/upload/multiple', methods=['POST'])
@login_required
def upload_multiple():
    """Upload multiple images for a style gallery"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files'}), 400
    files = request.files.getlist('files')
    style_id = request.form.get('style_id')
    paths = []
    for file in files:
        if file and allowed_file(file.filename):
            path = save_upload(file, 'styles')
            paths.append(path)
    if style_id and paths:
        style = Style.query.get(int(style_id))
        if style:
            gallery = json.loads(style.gallery or '[]')
            gallery.extend(paths)
            style.gallery = json.dumps(gallery)
            db.session.commit()
    return jsonify({'paths': paths, 'urls': [url_for('uploaded_file', filename=p) for p in paths]})

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

# ========== 款式管理 ==========

@app.route('/admin/styles', methods=['GET', 'POST'])
@login_required
def admin_styles():
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('款式名称不能为空', 'error')
            return redirect(url_for('admin_styles'))
        style = Style(
            name=name,
            code=request.form.get('code', '').strip(),
            description=request.form.get('description', ''),
            fabric_info=request.form.get('fabric_info', ''),
            price=float(request.form.get('price', 0))
        )
        # Colors
        colors = request.form.getlist('colors')
        if colors:
            style.colors = json.dumps(colors)
        # Fabric
        fabric_id = request.form.get('fabric_id', '').strip()
        if fabric_id:
            try:
                style.fabric_id = int(fabric_id)
            except ValueError:
                pass
        if request.files.get('image') and allowed_file(request.files['image'].filename):
            style.image_path = save_upload(request.files['image'], 'styles')
        # Multi-image gallery upload
        if request.files.getlist('gallery_files'):
            gallery_files = request.files.getlist('gallery_files')
            gallery = []
            for gf in gallery_files:
                if gf and gf.filename and allowed_file(gf.filename):
                    gallery.append(save_upload(gf, 'styles'))
            if gallery:
                style.gallery = json.dumps(gallery)
        db.session.add(style)
        db.session.commit()
        flash('款式添加成功', 'success')
        return redirect(url_for('admin_styles'))
    
    styles = Style.query.order_by(Style.created_at.desc()).all()
    fabrics = Fabric.query.order_by(Fabric.name).all()
    return render_template('admin_styles.html', styles=styles, fabrics=fabrics)

@app.route('/admin/style/<int:id>/edit', methods=['POST'])
@login_required
def admin_style_edit(id):
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    style = Style.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    if name:
        style.name = name
    style.code = request.form.get('code', '')
    style.description = request.form.get('description', '')
    style.fabric_info = request.form.get('fabric_info', '')
    style.price = float(request.form.get('price', 0))
    # Colors
    colors = request.form.getlist('colors')
    style.colors = json.dumps(colors) if colors else '[]'
    # Fabric
    fabric_id = request.form.get('fabric_id', '').strip()
    style.fabric_id = int(fabric_id) if fabric_id and fabric_id.isdigit() else None
    if request.files.get('image') and allowed_file(request.files['image'].filename):
        style.image_path = save_upload(request.files['image'], 'styles')
    # Multi-image gallery upload
    if request.files.getlist('gallery_files'):
        gallery_files = request.files.getlist('gallery_files')
        existing_gallery = json.loads(style.gallery or '[]')
        for gf in gallery_files:
            if gf and gf.filename and allowed_file(gf.filename):
                existing_gallery.append(save_upload(gf, 'styles'))
        style.gallery = json.dumps(existing_gallery)
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

@app.route('/admin/styles/edit', methods=['GET'])
@app.route('/admin/styles/edit/<int:id>', methods=['GET'])
@login_required
def admin_styles_edit(id=0):
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    style = None
    if id > 0:
        style = Style.query.get_or_404(id)
    fabrics = Fabric.query.order_by(Fabric.name).all()
    return render_template('admin_styles_edit.html', style=style, fabrics=fabrics)

@app.route('/admin/style/<int:id>/toggle', methods=['POST'])
@login_required
def admin_style_toggle(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    style = Style.query.get_or_404(id)
    style.is_active = not style.is_active
    db.session.commit()
    return jsonify({'is_active': style.is_active})

@app.route('/admin/style/<int:id>/rename', methods=['POST'])
@login_required
def admin_style_rename(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Name required'}), 400
    style = Style.query.get_or_404(id)
    style.name = data['name'].strip()
    db.session.commit()
    return jsonify({'name': style.name})

# ========== 面料管理 ==========

@app.route('/admin/fabrics', methods=['GET', 'POST'])
@login_required
def admin_fabrics():
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        if action == 'add':
            name = request.form.get('name', '').strip()
            composition = request.form.get('composition', '').strip()
            if name:
                fabric = Fabric(name=name, composition=composition)
                db.session.add(fabric)
                db.session.commit()
                flash(f'面料 "{name}" 添加成功', 'success')
        elif action == 'delete':
            fid = request.form.get('fabric_id', '').strip()
            if fid and fid.isdigit():
                fabric = Fabric.query.get(int(fid))
                if fabric:
                    db.session.delete(fabric)
                    db.session.commit()
                    flash('面料已删除', 'success')
        return redirect(url_for('admin_fabrics'))
    fabrics = Fabric.query.order_by(Fabric.name).all()
    return render_template('admin_fabrics.html', fabrics=fabrics)

@app.route('/api/fabrics', methods=['GET'])
@login_required
def api_fabrics():
    fabrics = Fabric.query.order_by(Fabric.name).all()
    return jsonify([{'id': f.id, 'name': f.name, 'composition': f.composition} for f in fabrics])

# ========== 颜色管理 API ==========

@app.route('/api/colors', methods=['GET'])
@login_required
def api_colors():
    """Return all colors used across styles"""
    styles = Style.query.all()
    all_colors = set()
    for s in styles:
        try:
            colors = json.loads(s.colors or '[]')
            for c in colors:
                all_colors.add(c)
        except:
            pass
    return jsonify(sorted(all_colors))

# ========== 花版历史 API ==========

@app.route('/api/fabric-history', methods=['GET'])
@login_required
def api_fabric_history():
    """Return fabric images with order count per image"""
    images = FabricImage.query.order_by(FabricImage.created_at.desc()).all()
    result = []
    for img in images:
        # Count how many order items used this fabric image by path
        count = OrderItem.query.filter_by(swatch_image=img.image_path).count()
        result.append({
            'id': img.id,
            'path': img.image_path,
            'url': url_for('uploaded_file', filename=img.image_path),
            'order_count': count,
            'created_at': img.created_at.strftime('%Y-%m-%d %H:%M') if img.created_at else ''
        })
    return jsonify(result)

# ========== 客人管理 ==========

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        if action == 'add':
            username = request.form.get('username', '').strip()
            if not username:
                flash('用户名不能为空', 'error')
                return redirect(url_for('admin_users'))
            if User.query.filter_by(username=username).first():
                flash(f'用户名 "{username}" 已存在', 'error')
                return redirect(url_for('admin_users'))
            user = User(
                username=username,
                nickname=request.form.get('nickname', '').strip(),
                phone=request.form.get('phone', '').strip(),
                role='guest'
            )
            user.set_password(request.form.get('password', '123456'))
            db.session.add(user)
            db.session.commit()
            flash(f'客人账号 {user.username} 创建成功', 'success')
        elif action == 'edit':
            user_id = request.form.get('user_id', '').strip()
            if user_id and user_id.isdigit():
                user = User.query.get(int(user_id))
                if user:
                    user.nickname = request.form.get('nickname', '').strip()
                    user.phone = request.form.get('phone', '').strip()
                    db.session.commit()
                    flash('客人信息已更新', 'success')
        elif action == 'reset_password':
            user_id = request.form.get('user_id', '').strip()
            new_pass = request.form.get('new_password', '123456')
            if user_id and user_id.isdigit():
                user = User.query.get(int(user_id))
                if user:
                    user.set_password(new_pass)
                    db.session.commit()
                    flash(f'密码已重置为 "{new_pass}"', 'success')
        elif action == 'toggle_active':
            user_id = request.form.get('user_id', '').strip()
            if user_id and user_id.isdigit():
                user = User.query.get(int(user_id))
                if user:
                    user.is_active = not user.is_active
                    db.session.commit()
                    flash(f'用户 {user.username} 已{"启用" if user.is_active else "停用"}', 'success')
        return redirect(url_for('admin_users'))
    
    users = User.query.filter_by(role='guest').all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/<int:user_id>', methods=['GET'])
@login_required
def admin_user_detail(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    user = User.query.get_or_404(user_id)
    if user.role != 'guest':
        abort(404)
    login_logs = LoginLog.query.filter_by(user_id=user.id).order_by(LoginLog.login_at.desc()).limit(20).all()
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('admin_user_detail.html', user=user, login_logs=login_logs, orders=orders, STATUS_MAP=STATUS_MAP)

# ========== 管理员修改密码 ==========

@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    if current_user.role != 'admin':
        return redirect(url_for('guest_styles'))
    if request.method == 'POST':
        old_pw = request.form.get('old_password', '')
        new_pw = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')
        if not current_user.check_password(old_pw):
            flash('原密码错误', 'error')
        elif len(new_pw) < 4:
            flash('新密码至少4位', 'error')
        elif new_pw != confirm_pw:
            flash('两次输入的新密码不一致', 'error')
        else:
            current_user.set_password(new_pw)
            db.session.commit()
            flash('密码修改成功', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_change_password.html')

# ========== Mockup ==========

@app.route('/mockup')
def mockup():
    return render_template('mockup.html')

# ========== 启动 ==========

# Lazy database initialization on first request (works with gunicorn)
_db_initialized = False

@app.before_request
def ensure_db_initialized():
    global _db_initialized
    if not _db_initialized:
        try:
            from models import init_db
            init_db(app)
            from seed import seed
            seed()
        except Exception as e:
            import traceback
            print(f"[DB INIT ERROR] {e}")
            traceback.print_exc()
        _db_initialized = True

if __name__ == '__main__':
    # Initialize before running
    with app.app_context():
        init_db(app)
        from seed import seed
        seed()
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    # Check if Pillow is available for image compression
    try:
        from PIL import Image
    except ImportError:
        print("⚠️  PIL/Pillow not installed, images will not be auto-compressed")
    app.run(host='0.0.0.0', port=port, debug=True)
