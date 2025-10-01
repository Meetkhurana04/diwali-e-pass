# 🪔 Diwali E-Pass Management System

A simple, lightweight web application to generate and manage paid Diwali e-passes with QR code scanning capabilities.

## Features

- **Admin Authentication**: 5 pre-configured admin accounts with secure bcrypt password hashing
- **Dashboard**: Live statistics showing total passes, revenue breakdown, and scan status
- **Pass Generation**: Create SINGLE (₹549) or COUPLE (₹999) passes with validation
- **QR Code Security**: HMAC-signed QR codes to prevent tampering
- **Live Scanner**: Camera-based QR scanner with atomic one-time scan validation
- **Database Management**: Search, filter, and export pass data to CSV
- **Mobile Friendly**: Responsive design for mobile and desktop

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Security**: bcrypt password hashing, HMAC QR signatures

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Update configuration** (Optional):
   - Copy `config.sample.py` to `config.py`
   - Update `SECRET_KEY` and `QR_SECRET` with secure random strings
   - Or edit these values directly in `app.py`

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## Default Login Credentials

- **Usernames**: admin1, admin2, admin3, admin4, admin5
- **Password**: diwaliparty@123

## Usage Guide

### 1. Login
Use any of the admin accounts to log in.

### 2. Dashboard
View live statistics:
- Total passes generated
- Single vs Couple breakdown
- Payment mode breakdown (Cash/Online)
- Total revenue
- Scan statistics

### 3. Generate Pass
1. Click "Generate New Pass"
2. Fill in the form:
   - Primary person details (name, phone)
   - Pass type (SINGLE/COUPLE)
   - For COUPLE: add second person details
   - Event timing
   - Payment mode (CASH/ONLINE)
   - Optional transaction info for online payments
3. Submit to generate pass with QR code
4. Download, print, or share via WhatsApp

### 4. Scan Passes
1. Click "Open QR Scanner"
2. Allow camera access
3. Point camera at QR code on pass
4. System automatically:
   - Validates QR signature
   - Checks if pass already used
   - Marks pass as scanned (one-time only)
   - Shows pass holder information

### 5. View Database
1. Click "View Database"
2. Search by name or phone
3. Filter by scan status or pass type
4. Export all data to CSV

## Security Features

- **Password Security**: bcrypt hashing with salt
- **QR Code Signing**: HMAC-SHA256 signatures prevent QR tampering
- **Atomic Scans**: Database-level atomicity prevents double-scanning
- **Unique Constraint**: Prevents duplicate passes for same name+phone

## Database Schema

### Admins Table
- username (PRIMARY KEY)
- password_hash
- display_name
- created_at

### Passes Table
- pass_id (PRIMARY KEY, UUID)
- name1, phone1 (UNIQUE together)
- name2, phone2 (for COUPLE)
- pass_type (SINGLE/COUPLE)
- amount
- payment_mode (CASH/ONLINE)
- txn_info
- timing
- created_at
- scanned_at
- scanned_by

## API Endpoints

- `GET /` - Redirect to login/dashboard
- `GET/POST /login` - Admin login
- `GET /logout` - Admin logout
- `GET /dashboard` - Main dashboard with stats
- `GET/POST /generate` - Pass generation form
- `GET /preview/<pass_id>` - Pass preview with QR code
- `GET /scanner` - QR scanner page
- `POST /api/scan` - Scan API endpoint
- `GET /database` - Database view with search/filter
- `GET /export-csv` - Export database to CSV

## Mobile Scanner Setup

For best results when using the scanner on mobile:
1. Use HTTPS (required for camera access on mobile browsers)
2. Or use `localhost` for testing
3. Grant camera permissions when prompted
4. Use environment-facing (rear) camera

## Production Deployment

1. **Change secrets**: Update `SECRET_KEY` and `QR_SECRET` in `app.py`
2. **Set debug=False**: Change `app.run(debug=False)`
3. **Use production server**: Deploy with Gunicorn, uWSGI, or similar
4. **Enable HTTPS**: Required for camera access on mobile devices
5. **Backup database**: Regularly backup `epass.db` file

Example production command:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Limitations

- No external payment gateway integration
- No email/SMS notifications
- No offline QR scanning capability
- Single-server deployment only
- SQLite (suitable for ~500 passes; use PostgreSQL for more)

## License

This is a simple demonstration application. Feel free to modify as needed.

## Support

For issues or questions, refer to the code comments or Flask documentation.
