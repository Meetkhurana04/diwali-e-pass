# 🏗️ System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  Web Browser (Desktop/Mobile)                               │
│  ├─── HTML5 Templates                                       │
│  ├─── CSS3 Styling (Responsive)                            │
│  └─── JavaScript (QR Generation/Scanning)                   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  Flask Web Server (Python 3.7+)                            │
│  ├─── Routes (10 endpoints)                                │
│  ├─── Session Management                                    │
│  ├─── Authentication Middleware                             │
│  ├─── HMAC QR Signing                                      │
│  └─── Business Logic                                        │
└─────────────────────────────────────────────────────────────┘
                            ↕ SQL
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  SQLite Database (epass.db)                                │
│  ├─── admins (5 pre-seeded)                               │
│  └─── passes (dynamic)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         FLASK APP (app.py)                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ Authentication │  │  Pass Manager  │  │  QR Security   │   │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤   │
│  │ • login()      │  │ • generate()   │  │ • sign_qr()    │   │
│  │ • logout()     │  │ • preview()    │  │ • verify_qr()  │   │
│  │ • @required    │  │ • validate()   │  │ • hmac_sha256  │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │   Dashboard    │  │    Scanner     │  │   Database     │   │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤   │
│  │ • stats()      │  │ • scanner()    │  │ • search()     │   │
│  │ • revenue()    │  │ • api_scan()   │  │ • filter()     │   │
│  │ • counts()     │  │ • atomic_upd() │  │ • export_csv() │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Database Manager (get_db)                   │  │
│  │  • Connection pooling • Row factory • SQL execution      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. Pass Generation Flow

```
User Request
    ↓
┌─────────────────────┐
│  GET /generate      │ ─→ Render empty form
└─────────────────────┘
    ↓
User fills form
    ↓
┌─────────────────────┐
│  POST /generate     │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Server Validation  │
├─────────────────────┤
│ • Check required    │
│ • Validate phone    │
│ • Check duplicates  │
└─────────────────────┘
    ↓
[Valid?] ─── No ──→ Return errors
    │
    Yes
    ↓
┌─────────────────────┐
│  Generate UUID      │ ─→ pass_id
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Database INSERT    │
├─────────────────────┤
│ INSERT INTO passes  │
│ VALUES (...)        │
└─────────────────────┘
    ↓
[Success?] ─── No ──→ Return error
    │
    Yes
    ↓
┌─────────────────────┐
│  Generate QR Code   │
├─────────────────────┤
│ • HMAC signature    │
│ • Base64 encode     │
│ • JSON payload      │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Redirect Preview   │ ─→ /preview/<pass_id>
└─────────────────────┘
    ↓
Display pass with QR
```

### 2. QR Scan Flow

```
Scanner Page Load
    ↓
┌─────────────────────┐
│  Request Camera     │
└─────────────────────┘
    ↓
[Permission?] ─── No ──→ Show error
    │
    Yes
    ↓
┌─────────────────────┐
│  Start Video Feed   │
│  (jsQR continuous)  │
└─────────────────────┘
    ↓
QR Code Detected
    ↓
┌─────────────────────┐
│  Extract Data       │ ─→ base64_payload
└─────────────────────┘
    ↓
┌─────────────────────┐
│  POST /api/scan     │
│  {payload: "..."}   │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Server: Decode     │
├─────────────────────┤
│ • Base64 decode     │
│ • JSON parse        │
│ • Extract id & sig  │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Verify Signature   │
├─────────────────────┤
│ expected = HMAC(id) │
│ valid = compare(    │
│   sig, expected)    │
└─────────────────────┘
    ↓
[Valid?] ─── No ──→ Return "Invalid QR"
    │
    Yes
    ↓
┌─────────────────────┐
│  Database Lookup    │
├─────────────────────┤
│ SELECT * FROM       │
│ passes WHERE        │
│ pass_id = ?         │
└─────────────────────┘
    ↓
[Found?] ─── No ──→ Return "Not Found"
    │
    Yes
    ↓
[Scanned?] ─── Yes ──→ Return "Already Used"
    │
    No
    ↓
┌─────────────────────┐
│  Atomic Update      │
├─────────────────────┤
│ UPDATE passes SET   │
│ scanned_at = NOW,   │
│ scanned_by = admin  │
│ WHERE pass_id = ?   │
│ AND scanned_at NULL │
└─────────────────────┘
    ↓
[Updated?] ─── No ──→ Return "Race condition"
    │                   (already used)
    Yes
    ↓
Return "Success" + pass info
    ↓
Show success modal
```

### 3. Authentication Flow

```
┌─────────────────────┐
│  GET /login         │ ─→ Show login form
└─────────────────────┘
    ↓
User submits credentials
    ↓
┌─────────────────────┐
│  POST /login        │
│  {user, pass}       │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Query Database     │
├─────────────────────┤
│ SELECT password_hash│
│ FROM admins WHERE   │
│ username = ?        │
└─────────────────────┘
    ↓
[Found?] ─── No ──→ Return "Invalid credentials"
    │
    Yes
    ↓
┌─────────────────────┐
│  Bcrypt Verify      │
├─────────────────────┤
│ bcrypt.checkpw(     │
│   input_pass,       │
│   stored_hash)      │
└─────────────────────┘
    ↓
[Valid?] ─── No ──→ Return "Invalid credentials"
    │
    Yes
    ↓
┌─────────────────────┐
│  Create Session     │
├─────────────────────┤
│ session['username'] │
│      = username     │
└─────────────────────┘
    ↓
Redirect to Dashboard
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Transport Security                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ HTTPS/TLS (Required for mobile camera)               │ │
│  │ • Encrypted communication                             │ │
│  │ • Certificate validation                              │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Layer 2: Session Security                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Flask Sessions                                        │ │
│  │ • Server-side storage                                 │ │
│  │ • Signed cookies (SECRET_KEY)                         │ │
│  │ • Automatic expiration                                │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Layer 3: Authentication                                    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Bcrypt Password Hashing                               │ │
│  │ • Work factor: 12 (default)                           │ │
│  │ • Automatic salting                                   │ │
│  │ • Timing-safe comparison                              │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Layer 4: Authorization                                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ @login_required Decorator                             │ │
│  │ • Check session on every request                      │ │
│  │ • Redirect if not authenticated                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Layer 5: Data Integrity                                    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ HMAC-SHA256 QR Signatures                             │ │
│  │ • Secret key: QR_SECRET                               │ │
│  │ • Payload: pass_id                                    │ │
│  │ • Timing-safe verification                            │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Layer 6: Database Security                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Atomic Operations                                     │ │
│  │ • UNIQUE constraints                                  │ │
│  │ • Parameterized queries (SQL injection safe)         │ │
│  │ • Transaction isolation                               │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema Details

```sql
-- SQLite Schema

-- Admins Table
CREATE TABLE admins (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes (automatic on PRIMARY KEY)
-- Index on username for fast lookup

-- Passes Table
CREATE TABLE passes (
    pass_id TEXT PRIMARY KEY,           -- UUID string
    name1 TEXT NOT NULL,
    phone1 TEXT NOT NULL,
    name2 TEXT,
    phone2 TEXT,
    pass_type TEXT NOT NULL 
        CHECK(pass_type IN ('SINGLE','COUPLE')),
    amount INTEGER NOT NULL,            -- 549 or 999
    payment_mode TEXT NOT NULL 
        CHECK(payment_mode IN ('CASH','ONLINE')),
    txn_info TEXT,
    timing TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scanned_at TIMESTAMP,               -- NULL = not scanned
    scanned_by TEXT,                    -- FK to admins.username
    UNIQUE(name1, phone1)               -- Prevent duplicates
);

-- Indexes
-- 1. PRIMARY KEY index on pass_id (automatic)
-- 2. UNIQUE index on (name1, phone1) (automatic)

-- Useful query indexes (add if needed):
CREATE INDEX idx_scanned_at ON passes(scanned_at);
CREATE INDEX idx_pass_type ON passes(pass_type);
CREATE INDEX idx_created_at ON passes(created_at DESC);
```

---

## API Endpoints

```
GET  /                  → Redirect to /login or /dashboard
GET  /login             → Login page
POST /login             → Process login
GET  /logout            → Logout and redirect
GET  /dashboard         → Main dashboard (requires auth)
GET  /generate          → Pass generation form (requires auth)
POST /generate          → Create new pass (requires auth)
GET  /preview/<id>      → Pass preview with QR (requires auth)
GET  /scanner           → QR scanner page (requires auth)
POST /api/scan          → Scan API (requires auth, returns JSON)
GET  /database          → Database view (requires auth)
GET  /export-csv        → Export CSV (requires auth)
```

### API Response Formats

**Success Response (api/scan):**
```json
{
    "status": "success",
    "message": "Pass scanned successfully",
    "pass_info": {
        "name1": "John Doe",
        "phone1": "9876543210",
        "name2": null,
        "phone2": null,
        "pass_type": "SINGLE",
        "timing": "7:00 PM - 11:00 PM"
    }
}
```

**Error Response (already used):**
```json
{
    "status": "already_scanned",
    "message": "This pass has already been used",
    "scanned_at": "2024-10-01 19:45:00",
    "scanned_by": "admin1",
    "pass_info": { ... }
}
```

**Error Response (invalid):**
```json
{
    "status": "error",
    "message": "Invalid or tampered QR code"
}
```

---

## Deployment Architecture

### Development Setup
```
[Developer Machine]
    ↓
┌─────────────────────┐
│  Flask Dev Server   │
│  python app.py      │
│  Port: 5000         │
│  Debug: ON          │
└─────────────────────┘
    ↓
http://localhost:5000
```

### Production Setup (Small)
```
[Server]
    ↓
┌─────────────────────┐
│  Gunicorn           │
│  4 workers          │
│  Port: 5000         │
└─────────────────────┘
    ↓
http://server-ip:5000
```

### Production Setup (Large)
```
[Internet]
    ↓
┌─────────────────────┐
│  Nginx (Port 80/443)│
│  SSL Termination    │
│  Static files       │
│  Load balancing     │
└─────────────────────┘
    ↓ proxy_pass
┌─────────────────────┐
│  Gunicorn           │
│  8 workers          │
│  Port: 5000         │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  PostgreSQL         │
│  (if upgraded)      │
└─────────────────────┘
```

---

## Technology Justification

### Why Flask?
- ✅ Lightweight and minimal
- ✅ Built-in development server
- ✅ Simple routing
- ✅ Jinja2 templating
- ✅ Large community
- ✅ Easy to deploy

### Why SQLite?
- ✅ Zero configuration
- ✅ Single file database
- ✅ No separate server
- ✅ Perfect for ~500 rows
- ✅ ACID compliant
- ✅ Easy backup (copy file)

### Why Bcrypt?
- ✅ Industry standard
- ✅ Adaptive hashing
- ✅ Built-in salting
- ✅ Timing-safe comparison
- ✅ Future-proof (adjustable cost)

### Why Vanilla JS?
- ✅ No build step required
- ✅ No framework overhead
- ✅ Faster page loads
- ✅ Easier to understand
- ✅ No version conflicts

### Why HMAC-SHA256?
- ✅ Cryptographically secure
- ✅ Built into Python
- ✅ Fast computation
- ✅ Industry standard
- ✅ Tamper-evident

---

## Scalability Paths

### Current Capacity
```
Users: 10-20 concurrent
Passes: ~500 total
Scans: ~100 per minute
Database: SQLite (sufficient)
Server: Single instance
```

### Scale to 100+ concurrent
```
1. Add Gunicorn: 8-16 workers
2. Add Nginx: Reverse proxy + caching
3. Upgrade RAM: 2GB → 4GB
4. Consider PostgreSQL: Better concurrent writes
```

### Scale to 1000+ passes
```
1. PostgreSQL: Required for this scale
2. Connection pooling: 20-50 connections
3. Load balancer: Multiple app instances
4. CDN: Static asset delivery
5. Redis: Session storage
```

---

## Monitoring Points

### Application Health
```
✓ Response times per endpoint
✓ Error rate (500 errors)
✓ Request rate (requests/sec)
✓ Active sessions count
```

### Database Health
```
✓ Query execution time
✓ Database file size
✓ Locks/contention (SQLite)
✓ Connection pool usage (PostgreSQL)
```

### Business Metrics
```
✓ Pass generation rate
✓ Scan rate (entries/hour)
✓ Revenue tracking
✓ Success/failure ratio
```

---

## Backup Strategy Architecture

```
┌─────────────────────┐
│   Production DB     │
│    epass.db         │
└─────────────────────┘
         │
         │ Copy every hour
         ↓
┌─────────────────────┐
│   Hourly Backups    │
│  /backups/hourly/   │
│  (Last 24 hours)    │
└─────────────────────┘
         │
         │ Daily consolidation
         ↓
┌─────────────────────┐
│   Daily Backups     │
│  /backups/daily/    │
│  (Last 7 days)      │
└─────────────────────┘
         │
         │ CSV export
         ↓
┌─────────────────────┐
│   CSV Archives      │
│  /backups/csv/      │
│  (Permanent)        │
└─────────────────────┘
```

---

## Error Handling Flow

```
Exception Occurs
    ↓
┌─────────────────────┐
│  Exception Type?    │
└─────────────────────┘
    ↓
┌──────────┬──────────┬──────────┐
│          │          │          │
SQL Error  Network    Validation
   ↓          ↓          ↓
Log       Retry     User Feedback
   ↓          ↓          ↓
Return    Return    Return Form
Error     Error     with Errors
Page      Message
```

---

**This architecture supports 500+ passes efficiently while maintaining security and simplicity.** 🏗️
