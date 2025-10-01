# Configuration file for Diwali E-Pass System
# Copy this to config.py and update with your settings

# Flask secret key - CHANGE THIS IN PRODUCTION!
SECRET_KEY = 'your-secret-key-change-this-in-production-use-random-string'

# QR code signing secret - CHANGE THIS IN PRODUCTION!
# This is used to sign QR codes to prevent tampering
QR_SECRET = 'qr-signing-secret-change-this-too-use-random-string'

# Database path
DATABASE = 'epass.db'

# Price configuration (in INR)
PRICE_SINGLE = 549
PRICE_COUPLE = 999

# Admin password (hashed with bcrypt)
# Default password: diwaliparty@123
# Accounts: admin1, admin2, admin3, admin4, admin5
