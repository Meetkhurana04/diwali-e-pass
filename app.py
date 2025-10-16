from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import sqlite3
import bcrypt
import uuid
import hmac
import hashlib
import base64
import json
from datetime import datetime
import io
import csv
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
QR_SECRET = os.environ.get('QR_SECRET', 'qr-signing-secret-change-this-too')

# Database configuration - supports both SQLite (local) and PostgreSQL (production)
DATABASE_URL = os.environ.get('DATABASE_URL', 'epass.db')

# Fix for Render PostgreSQL URL
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Price constants
PRICE_SINGLE = 499
PRICE_COUPLE = 999

def is_postgres():
    """Check if using PostgreSQL"""
    return DATABASE_URL.startswith('postgresql')

def get_db():
    """Get database connection - works with SQLite and PostgreSQL"""
    if is_postgres():
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.cursor_factory = RealDictCursor
        return conn
    else:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        return conn

def sql_param():
    """Return correct SQL parameter placeholder"""
    return '%s' if is_postgres() else '?'

def init_db():
    """Initialize database with schema and seed admin accounts"""
    conn = get_db()
    cursor = conn.cursor()
    
    pg = is_postgres()
    
    # Create admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create passes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passes (
            pass_id TEXT PRIMARY KEY,
            name1 TEXT NOT NULL,
            phone1 TEXT NOT NULL,
            name2 TEXT,
            phone2 TEXT,
            pass_type TEXT NOT NULL CHECK(pass_type IN ('SINGLE','COUPLE')),
            amount INTEGER NOT NULL,
            payment_mode TEXT NOT NULL CHECK(payment_mode IN ('CASH','ONLINE')),
            txn_info TEXT,
            timing TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scanned_at TIMESTAMP,
            scanned_by TEXT,
            UNIQUE(name1, phone1)
        )
    ''')
    
    # Seed admin accounts if not exist
    password = 'diwaliparty@123'
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_users = [
        ('admin1', 'Admin One'),
        ('admin2', 'Admin Two'),
        ('admin3', 'Admin Three'),
        ('admin4', 'Admin Four'),
        ('admin5', 'Admin Five')
    ]
    
    param = sql_param()
    for username, display_name in admin_users:
        if pg:
            cursor.execute(
                f'INSERT INTO admins (username, password_hash, display_name) VALUES ({param}, {param}, {param}) ON CONFLICT (username) DO NOTHING',
                (username, password_hash, display_name)
            )
        else:
            cursor.execute(
                f'INSERT OR IGNORE INTO admins (username, password_hash, display_name) VALUES ({param}, {param}, {param})',
                (username, password_hash, display_name)
            )
    
    conn.commit()
    conn.close()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_qr_payload(pass_id):
    """Generate QR payload with HMAC signature"""
    # Create HMAC signature
    signature = hmac.new(
        QR_SECRET.encode('utf-8'),
        pass_id.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Create payload
    payload = {
        'id': pass_id,
        'sig': signature
    }
    
    # Encode as base64
    json_str = json.dumps(payload)
    b64_payload = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    return b64_payload

def verify_qr_payload(b64_payload):
    """Verify QR payload and return pass_id if valid"""
    try:
        # Decode base64
        json_str = base64.b64decode(b64_payload.encode('utf-8')).decode('utf-8')
        payload = json.loads(json_str)
        
        pass_id = payload.get('id')
        signature = payload.get('sig')
        
        if not pass_id or not signature:
            return None
        
        # Recompute signature
        expected_sig = hmac.new(
            QR_SECRET.encode('utf-8'),
            pass_id.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Timing-safe comparison
        if hmac.compare_digest(signature, expected_sig):
            return pass_id
        
        return None
    except Exception as e:
        print(f"QR verification error: {e}")
        return None

@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        conn = get_db()
        cursor = conn.cursor()
        param = sql_param()
        cursor.execute(f'SELECT password_hash FROM admins WHERE username = {param}', (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            session['username'] = username
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout admin"""
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total passes
    cursor.execute('SELECT COUNT(*) as count FROM passes')
    total_passes = cursor.fetchone()['count']
    
    # Single vs Couple
    param = sql_param()
    cursor.execute(f"SELECT COUNT(*) as count FROM passes WHERE pass_type = {param}", ('SINGLE',))
    single_count = cursor.fetchone()['count']
    
    cursor.execute(f"SELECT COUNT(*) as count FROM passes WHERE pass_type = {param}", ('COUPLE',))
    couple_count = cursor.fetchone()['count']
    
    # Payment breakdown
    cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total FROM passes WHERE payment_mode = {param}", ('CASH',))
    cash_total = cursor.fetchone()['total']
    
    cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total FROM passes WHERE payment_mode = {param}", ('ONLINE',))
    online_total = cursor.fetchone()['total']
    
    # Total revenue
    total_revenue = cash_total + online_total
    
    # Scanned stats
    cursor.execute('SELECT COUNT(*) as count FROM passes WHERE scanned_at IS NOT NULL')
    scanned_count = cursor.fetchone()['count']
    
    conn.close()
    
    stats = {
        'total_passes': total_passes,
        'single_count': single_count,
        'couple_count': couple_count,
        'cash_total': cash_total,
        'online_total': online_total,
        'total_revenue': total_revenue,
        'scanned_count': scanned_count,
        'unscanned_count': total_passes - scanned_count
    }
    
    return render_template('dashboard.html', stats=stats, username=session.get('username'))

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    """Generate new pass"""
    if request.method == 'POST':
        # Get form data
        name1 = request.form.get('name1', '').strip()
        phone1 = request.form.get('phone1', '').strip()
        name2 = request.form.get('name2', '').strip()
        phone2 = request.form.get('phone2', '').strip()
        pass_type = request.form.get('pass_type', '').upper()
        timing = request.form.get('timing', '').strip()
        payment_mode = request.form.get('payment_mode', '').upper()
        txn_info = request.form.get('txn_info', '').strip() or None
        
        # Validation
        errors = []
        
        if not name1:
            errors.append('Name 1 is required')
        if not phone1 or len(phone1) != 10 or not phone1.isdigit():
            errors.append('Phone 1 must be 10 digits')
        if pass_type not in ['SINGLE', 'COUPLE']:
            errors.append('Invalid pass type')
        if pass_type == 'COUPLE':
            if not name2:
                errors.append('Name 2 is required for couple pass')
            if not phone2 or len(phone2) != 10 or not phone2.isdigit():
                errors.append('Phone 2 must be 10 digits for couple pass')
        if not timing:
            errors.append('Timing is required')
        if payment_mode not in ['CASH', 'ONLINE']:
            errors.append('Invalid payment mode')
        
        if errors:
            return render_template('generate.html', errors=errors, form_data=request.form)
        
        # Set amount
        amount = PRICE_COUPLE if pass_type == 'COUPLE' else PRICE_SINGLE
        
        # Generate pass ID
        pass_id = str(uuid.uuid4())
        
        # Insert into database
        try:
            conn = get_db()
            cursor = conn.cursor()
            param = sql_param()
            cursor.execute(f'''
                INSERT INTO passes (pass_id, name1, phone1, name2, phone2, pass_type, amount, payment_mode, txn_info, timing)
                VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param})
            ''', (pass_id, name1, phone1, name2, phone2, pass_type, amount, payment_mode, txn_info, timing))
            conn.commit()
            conn.close()
            
            return redirect(url_for('preview', pass_id=pass_id))
            
        except Exception as e:
            errors.append(f'A pass already exists for {name1} with phone {phone1}')
            return render_template('generate.html', errors=errors, form_data=request.form)
    
    return render_template('generate.html')

@app.route('/preview/<pass_id>')
@login_required
def preview(pass_id):
    """Preview generated pass"""
    conn = get_db()
    cursor = conn.cursor()
    param = sql_param()
    cursor.execute(f'SELECT * FROM passes WHERE pass_id = {param}', (pass_id,))
    pass_data = cursor.fetchone()
    conn.close()
    
    if not pass_data:
        return "Pass not found", 404
    
    # Generate QR payload
    qr_payload = generate_qr_payload(pass_id)
    
    # Convert to dict for template
    pass_dict = dict(pass_data)
    pass_dict['qr_payload'] = qr_payload
    
    return render_template('preview.html', pass_data=pass_dict)

@app.route('/regenerate/<pass_id>')
@login_required
def regenerate(pass_id):
    """Regenerate existing pass (same QR code)"""
    # Just redirect to preview - this ensures same QR code is used
    return redirect(url_for('preview', pass_id=pass_id))

@app.route('/scanner')
@login_required
def scanner():
    """QR scanner page"""
    return render_template('scanner.html', username=session.get('username'))

@app.route('/api/scan', methods=['POST'])
@login_required
def api_scan():
    """API endpoint to scan QR code"""
    data = request.get_json()
    qr_payload = data.get('payload', '')
    
    # Verify QR payload
    pass_id = verify_qr_payload(qr_payload)
    
    if not pass_id:
        return jsonify({'status': 'error', 'message': 'Invalid or tampered QR code'}), 400
    
    # Atomic update
    conn = get_db()
    cursor = conn.cursor()
    
    # First check if pass exists
    param = sql_param()
    cursor.execute(f'SELECT * FROM passes WHERE pass_id = {param}', (pass_id,))
    pass_data = cursor.fetchone()
    
    if not pass_data:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Pass not found'}), 404
    
    # Check if already scanned
    if pass_data['scanned_at']:
        conn.close()
        return jsonify({
            'status': 'already_scanned',
            'message': 'This pass has already been used',
            'scanned_at': pass_data['scanned_at'],
            'scanned_by': pass_data['scanned_by'],
            'pass_info': {
                'name1': pass_data['name1'],
                'phone1': pass_data['phone1'],
                'name2': pass_data['name2'],
                'phone2': pass_data['phone2'],
                'pass_type': pass_data['pass_type'],
                'timing': pass_data['timing']
            }
        }), 400
    
    # Atomic update - only update if not scanned
    param = sql_param()
    cursor.execute(f'''
        UPDATE passes 
        SET scanned_at = CURRENT_TIMESTAMP, scanned_by = {param} 
        WHERE pass_id = {param} AND scanned_at IS NULL
    ''', (session.get('username'), pass_id))
    rows_affected = cursor.rowcount
    conn.commit()
    
    if rows_affected == 0:
        # Race condition - already scanned
        cursor.execute(f'SELECT * FROM passes WHERE pass_id = {param}', (pass_id,))
        pass_data = cursor.fetchone()
        conn.close()
        return jsonify({
            'status': 'already_scanned',
            'message': 'This pass has already been used',
            'scanned_by': pass_data['scanned_by']
        }), 400
    
    # Get updated pass data
    param = sql_param()
    cursor.execute(f'SELECT * FROM passes WHERE pass_id = {param}', (pass_id,))
    pass_data = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'status': 'success',
        'message': 'Pass scanned successfully',
        'pass_info': {
            'name1': pass_data['name1'],
            'phone1': pass_data['phone1'],
            'name2': pass_data['name2'],
            'phone2': pass_data['phone2'],
            'pass_type': pass_data['pass_type'],
            'timing': pass_data['timing']
        }
    })

@app.route('/database')
@login_required
def database():
    """Database/search page"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    filter_scanned = request.args.get('scanned', '')
    filter_type = request.args.get('type', '')
    
    per_page = 20
    offset = (page - 1) * per_page
    
    param = sql_param()
    
    # Build query
    query = 'SELECT * FROM passes WHERE 1=1'
    params = []
    
    if search:
        query += f' AND (name1 LIKE {param} OR phone1 LIKE {param} OR name2 LIKE {param} OR phone2 LIKE {param})'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param, search_param])
    
    if filter_scanned == 'scanned':
        query += ' AND scanned_at IS NOT NULL'
    elif filter_scanned == 'unscanned':
        query += ' AND scanned_at IS NULL'
    
    if filter_type in ['SINGLE', 'COUPLE']:
        query += f' AND pass_type = {param}'
        params.append(filter_type)
    
    # Get total count
    count_query = query.replace('SELECT *', 'SELECT COUNT(*) AS count')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()['count']  # Use dictionary-style access for both SQLite and PostgreSQL
    
    # Get paginated results
    query += f' ORDER BY created_at DESC LIMIT {param} OFFSET {param}'
    params.extend([per_page, offset])
    cursor.execute(query, params)
    passes = cursor.fetchall()
    conn.close()
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('database.html', 
                         passes=passes, 
                         page=page, 
                         total_pages=total_pages,
                         search=search,
                         filter_scanned=filter_scanned,
                         filter_type=filter_type,
                         total_count=total_count)

@app.route('/export-csv')
@login_required
def export_csv():
    """Export database to CSV"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM passes ORDER BY created_at DESC')
    passes = cursor.fetchall()
    conn.close()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Pass ID', 'Name 1', 'Phone 1', 'Name 2', 'Phone 2', 'Pass Type', 
                     'Amount', 'Payment Mode', 'Transaction Info', 'Timing', 
                     'Created At', 'Scanned At', 'Scanned By'])
    
    # Write data
    for pass_data in passes:
        writer.writerow([
            pass_data['pass_id'],
            pass_data['name1'],
            pass_data['phone1'],
            pass_data['name2'] or '',
            pass_data['phone2'] or '',
            pass_data['pass_type'],
            pass_data['amount'],
            pass_data['payment_mode'],
            pass_data['txn_info'] or '',
            pass_data['timing'],
            pass_data['created_at'],
            pass_data['scanned_at'] or '',
            pass_data['scanned_by'] or ''
        ])
    
    # Prepare download
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'epass_database_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/health')
def health():
    """Health check endpoint"""
    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "ok",
        "database": None
    }
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"error: {str(e)}"

    return jsonify(status)


with app.app_context():
    init_db()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
