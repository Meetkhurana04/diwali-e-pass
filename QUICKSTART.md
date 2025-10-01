# 🚀 Quick Start Guide

## Get Started in 3 Steps

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

Or simply double-click `run.bat` on Windows.

### 2️⃣ Run the Application
```bash
python app.py
```

The server will start at: **http://localhost:5000**

### 3️⃣ Login
Open your browser and navigate to http://localhost:5000

**Login Credentials:**
- Username: `admin1` (or admin2, admin3, admin4, admin5)
- Password: `diwaliparty@123`

---

## 📱 Features Overview

### Dashboard
- View real-time statistics
- Total passes, revenue breakdown
- Scan status tracking

### Generate Pass
1. Click **"Generate New Pass"**
2. Fill in details:
   - Name & Phone (required)
   - Pass Type: SINGLE (₹549) or COUPLE (₹999)
   - Event timing
   - Payment mode: CASH or ONLINE
3. Submit to generate pass with QR code
4. Download, print, or share

### Scan Passes
1. Click **"Open QR Scanner"**
2. Allow camera access
3. Point at QR code
4. Automatic validation and one-time scan enforcement

### Database
- Search by name or phone
- Filter by status/type
- Export to CSV

---

## 🔐 Security Notes

**IMPORTANT:** Before deploying to production:

1. Change the secret keys in `app.py`:
   ```python
   app.secret_key = 'your-random-secret-key-here'
   QR_SECRET = 'your-qr-signing-secret-here'
   ```

2. Generate secure random keys:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

---

## 📊 Database

The SQLite database (`epass.db`) is automatically created on first run with:
- 5 pre-configured admin accounts
- Empty passes table ready for use

**Backup:** Simply copy the `epass.db` file to backup your data.

---

## 🛠️ Troubleshooting

### Camera not working in scanner?
- **HTTPS required** for mobile browsers (not localhost)
- Grant camera permissions when prompted
- Use rear camera for best results

### Module not found error?
- Run: `pip install -r requirements.txt`

### Port already in use?
- Change port in `app.py`: `app.run(port=5001)`

---

## 📞 Need Help?

Check the full `README.md` for detailed documentation.

---

## ✅ System Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Camera (for QR scanning)

---

**Happy Diwali! 🪔**
