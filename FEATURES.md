# ✨ Feature Documentation

## Complete Feature List

### 🔐 Authentication & Security

#### Admin Login System
- **5 Pre-configured Accounts**: admin1, admin2, admin3, admin4, admin5
- **Single Password**: diwaliparty@123 (hashed with bcrypt)
- **Session Management**: Secure Flask sessions
- **Login Protection**: All routes require authentication except login page

#### QR Code Security
- **HMAC-SHA256 Signatures**: Every QR code is cryptographically signed
- **Tamper Detection**: Modified QR codes are automatically rejected
- **One-Time Use**: Atomic database operations prevent double-scanning
- **Server-Side Validation**: All verification happens on the server

---

### 📊 Dashboard Features

#### Real-Time Statistics
```
Total Passes Generated: Live count
├── Single Passes: Count of SINGLE type
└── Couple Passes: Count of COUPLE type

Revenue Breakdown:
├── Cash Payments: Total ₹ from cash
├── Online Payments: Total ₹ from online
└── Total Revenue: Combined total

Scan Statistics:
├── Scanned: Entries that have been validated
└── Unscanned: Pending entries
```

#### Quick Actions
- **Generate New Pass**: Direct link to pass generation
- **Open QR Scanner**: Launch mobile scanner
- **View Database**: Access full pass database

---

### ➕ Pass Generation

#### Form Fields

**Primary Person (Required)**
- Name: Text input, non-empty
- Phone: 10-digit number validation

**Pass Type (Required)**
- SINGLE: ₹549
- COUPLE: ₹999 (shows additional fields)

**Couple Fields (Conditional)**
- Name 2: Required if COUPLE selected
- Phone 2: Required, 10-digit validation

**Event Details (Required)**
- Timing: Free text (e.g., "7:00 PM - 11:00 PM, Oct 24")

**Payment Information (Required)**
- Mode: CASH or ONLINE
- Transaction Info: Optional, visible if ONLINE selected

#### Validation Rules
```
✓ Phone numbers must be exactly 10 digits
✓ All required fields must be filled
✓ Unique constraint on name1 + phone1 combination
✓ COUPLE passes require both person details
✓ Amount is auto-calculated based on pass type
```

#### Form Behavior
- **Dynamic Fields**: COUPLE fields appear/disappear based on selection
- **Price Display**: Live update showing current amount
- **Client-Side Validation**: Instant feedback on errors
- **Server-Side Validation**: Final validation before saving

---

### 🎫 Pass Preview & Distribution

#### Pass Display
```
╔════════════════════════════════════════╗
║      🪔 Diwali Party Pass              ║
║           SINGLE / COUPLE              ║
╠════════════════════════════════════════╣
║  Name: [Primary Name]                  ║
║  Phone: [Primary Phone]                ║
║  [Partner Details if COUPLE]           ║
║  Timing: [Event Time]                  ║
║  Amount: ₹549/999 (CASH/ONLINE)       ║
╠════════════════════════════════════════╣
║       [QR CODE - 200x200px]           ║
║         Scan at Entry                  ║
║    Pass ID: xxxxxxxx...                ║
╠════════════════════════════════════════╣
║  Generated: [Timestamp]                ║
║  Valid for one-time entry only         ║
╚════════════════════════════════════════╝
```

#### Distribution Options

**1. Download PNG**
- Uses html2canvas library
- High-resolution 2x scale
- Transparent background
- Filename: `diwali-pass-[name].png`

**2. Print Pass**
- Print-optimized layout
- Removes UI elements
- Full-width pass design
- Browser print dialog

**3. Share on WhatsApp**
- Pre-formatted message with pass details
- Opens WhatsApp with shareable text
- Works on mobile and desktop
- Format:
  ```
  🪔 Diwali Party Pass Generated!
  
  Name: [Name]
  Type: SINGLE/COUPLE
  Timing: [Time]
  
  Please present this QR code at the entry.
  ```

---

### 📷 QR Code Scanner

#### Scanner Interface
```
┌─────────────────────────────────────┐
│  📷 QR Code Scanner                 │
├─────────────────────────────────────┤
│  Status: Ready to scan              │
├─────────────────────────────────────┤
│                                     │
│    [Live Camera Feed]               │
│                                     │
├─────────────────────────────────────┤
│  📱 Point camera at QR code         │
│  Auto-detect enabled                │
├─────────────────────────────────────┤
│  📊 Statistics                      │
│  Successful: 0  Failed/Used: 0      │
└─────────────────────────────────────┘
```

#### Scan Flow

**1. Camera Initialization**
- Request camera permissions
- Use rear camera (environment-facing)
- Start continuous scanning loop

**2. QR Detection**
- Real-time frame analysis using jsQR
- Automatic QR code detection
- 2-second cooldown prevents duplicate scans

**3. Verification Process**
```
QR Code Scanned
    ↓
Decode Base64 Payload
    ↓
Extract pass_id & signature
    ↓
Recompute HMAC-SHA256
    ↓
Timing-Safe Comparison
    ↓
┌─ Valid? ─┐
│          │
YES        NO → Show "Invalid Pass" ❌
│
Check Database
│
┌─ Found? ─┐
│          │
YES        NO → Show "Pass Not Found" ❌
│
┌─ Already Scanned? ─┐
│                    │
YES                  NO
│                    │
Show "Already Used"  Atomic Update
⚠️                   scanned_at = NOW
                     scanned_by = admin
                     ↓
                     Show "Success" ✅
```

#### Scan Results

**✅ Success Modal**
```
╔═══════════════════════════════════╗
║            ✅                     ║
║       Entry Approved!             ║
╠═══════════════════════════════════╣
║  Pass scanned successfully        ║
╠═══════════════════════════════════╣
║  Name: [Name]                     ║
║  Phone: [Phone]                   ║
║  Type: SINGLE/COUPLE              ║
║  Timing: [Time]                   ║
╠═══════════════════════════════════╣
║     [Continue Scanning]           ║
╚═══════════════════════════════════╝
```

**⚠️ Already Used Modal**
```
╔═══════════════════════════════════╗
║            ⚠️                     ║
║       Already Used!               ║
╠═══════════════════════════════════╣
║  This pass has been used          ║
╠═══════════════════════════════════╣
║  Scanned At: [Timestamp]          ║
║  Scanned By: [Admin]              ║
╠═══════════════════════════════════╣
║     [Continue Scanning]           ║
╚═══════════════════════════════════╝
```

**❌ Invalid Pass Modal**
```
╔═══════════════════════════════════╗
║            ❌                     ║
║       Invalid Pass!               ║
╠═══════════════════════════════════╣
║  QR code is invalid or tampered   ║
╠═══════════════════════════════════╣
║     [Continue Scanning]           ║
╚═══════════════════════════════════╝
```

---

### 🗄️ Database Management

#### Search & Filter

**Search Bar**
- Search by: name1, name2, phone1, phone2
- Real-time search as you type
- Case-insensitive matching
- Partial matches supported

**Filters**
```
Status Filter:
├── All Status (default)
├── Scanned Only
└── Unscanned Only

Type Filter:
├── All Types (default)
├── Single
└── Couple
```

**Auto-Submit**: Filters apply automatically on change

#### Table Columns
| Column | Description |
|--------|-------------|
| Name(s) | Primary name + partner (if couple) |
| Phone(s) | Primary phone + partner phone |
| Type | SINGLE/COUPLE badge |
| Amount | ₹549 or ₹999 |
| Payment | CASH/ONLINE badge + txn info |
| Timing | Event time slot |
| Created | Timestamp of generation |
| Status | Scanned ✓ or Pending with timestamp |
| Scanned By | Admin username who scanned |

#### Pagination
- **20 passes per page**
- Previous/Next navigation
- Current page indicator
- Total page count
- Maintains filters across pages

#### CSV Export
- **Export Button**: Top right of database page
- **Filename**: `epass_database_YYYYMMDD_HHMMSS.csv`
- **All Fields Included**: Complete data export
- **Format**: Standard CSV, UTF-8 encoded

**CSV Structure:**
```csv
Pass ID,Name 1,Phone 1,Name 2,Phone 2,Pass Type,Amount,Payment Mode,Transaction Info,Timing,Created At,Scanned At,Scanned By
uuid-here,John Doe,9876543210,,,SINGLE,549,CASH,,7 PM - 11 PM,2024-10-01 10:30:00,2024-10-01 19:45:00,admin1
```

---

### 🎨 UI/UX Features

#### Responsive Design
- **Mobile-First**: Optimized for phones
- **Tablet Support**: Adaptive layout
- **Desktop**: Full-width experience
- **Print-Friendly**: Optimized print styles

#### Color Coding
```
Pass Type:
├── SINGLE → Blue (#e3f2fd / #1976d2)
└── COUPLE → Pink (#fce4ec / #c2185b)

Payment Mode:
├── CASH → Green (#e8f5e9 / #388e3c)
└── ONLINE → Blue (#e1f5fe / #0277bd)

Status:
├── SCANNED → Green (#c8e6c9 / #2e7d32)
└── UNSCANNED → Yellow (#ffecb3 / #f57f17)
```

#### Animations
- **Fade In**: Modals slide in smoothly
- **Hover Effects**: Buttons lift on hover
- **Transitions**: Smooth state changes
- **Loading States**: Visual feedback

---

### 📱 Mobile Optimization

#### Scanner Optimizations
- **Rear Camera Default**: Best for scanning
- **Full-Screen Video**: Maximum visibility
- **Touch-Friendly**: Large buttons
- **Modal Alerts**: Clear feedback

#### Form Optimizations
- **Number Keyboards**: Auto-enabled for phone inputs
- **Large Touch Targets**: Easy tapping
- **Clear Labels**: Readable on small screens
- **Validation Feedback**: Instant error messages

---

### 🔧 Technical Specifications

#### Performance
- **SQLite**: Handles 500+ passes efficiently
- **Atomic Operations**: Race-condition safe
- **Session Management**: Server-side sessions
- **QR Generation**: Client-side (fast)

#### Browser Compatibility
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

#### Required Permissions
- **Camera**: For QR scanning (user-granted)
- **Cookies**: For session management

---

### 📈 Scalability Notes

**Current Setup (SQLite)**
- Recommended: Up to 500 passes
- No concurrent write issues for this use case
- Simple backup (copy .db file)

**For Larger Events**
Replace SQLite with PostgreSQL:
1. Change database connection in `app.py`
2. Update SQL syntax (minor changes)
3. Same application code otherwise

---

## 🎯 Use Cases

### Typical Event Flow

**Before Event:**
1. Admin logs in
2. Generate passes as attendees register
3. Download/print passes or share via WhatsApp
4. Monitor dashboard for registration stats

**During Event:**
1. Security staff opens scanner on mobile
2. Scan passes at entry gate
3. System validates and marks as used
4. Real-time tracking of entries

**After Event:**
1. Export database to CSV
2. Analyze attendance data
3. Revenue reporting
4. Backup database

---

## 💡 Tips & Best Practices

### For Organizers
- Generate passes in batches during registration
- Test scanner before event day
- Use multiple devices with different admin accounts
- Keep backup of database file
- Export CSV regularly

### For Security Staff
- Ensure good lighting for QR scanning
- Hold camera steady for 1-2 seconds
- Watch for "Already Used" warnings
- Report invalid passes to organizers

### For Attendees
- Download pass immediately after generation
- Keep QR code visible and unobstructed
- Arrive early to avoid entry queues
- Contact organizer if pass issues occur

---

**Built with ❤️ for Diwali celebrations! 🪔**
