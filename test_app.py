"""
Simple test script to verify the application setup
"""
import sqlite3
import bcrypt
from app import init_db, generate_qr_payload, verify_qr_payload

def test_database():
    """Test database initialization"""
    print("Testing database initialization...")
    init_db()
    
    conn = sqlite3.connect('epass.db')
    cursor = conn.cursor()
    
    # Check admins table
    cursor.execute('SELECT COUNT(*) FROM admins')
    admin_count = cursor.fetchone()[0]
    assert admin_count == 5, f"Expected 5 admins, found {admin_count}"
    print(f"✓ Admin accounts created: {admin_count}")
    
    # Verify admin password
    cursor.execute('SELECT password_hash FROM admins WHERE username = "admin1"')
    password_hash = cursor.fetchone()[0]
    assert bcrypt.checkpw('diwaliparty@123'.encode('utf-8'), password_hash.encode('utf-8'))
    print("✓ Admin password verification successful")
    
    # Check passes table structure
    cursor.execute('PRAGMA table_info(passes)')
    columns = [col[1] for col in cursor.fetchall()]
    expected_columns = ['pass_id', 'name1', 'phone1', 'name2', 'phone2', 
                       'pass_type', 'amount', 'payment_mode', 'txn_info', 
                       'timing', 'created_at', 'scanned_at', 'scanned_by']
    for col in expected_columns:
        assert col in columns, f"Missing column: {col}"
    print(f"✓ Passes table structure correct: {len(columns)} columns")
    
    conn.close()
    print("\n✅ Database tests passed!\n")

def test_qr_signature():
    """Test QR code signature generation and verification"""
    print("Testing QR signature...")
    
    test_pass_id = "test-pass-123"
    
    # Generate payload
    payload = generate_qr_payload(test_pass_id)
    print(f"✓ QR payload generated: {payload[:50]}...")
    
    # Verify payload
    verified_id = verify_qr_payload(payload)
    assert verified_id == test_pass_id, f"Expected {test_pass_id}, got {verified_id}"
    print(f"✓ QR signature verified successfully")
    
    # Test tampered payload
    tampered_payload = payload[:-5] + "xxxxx"
    verified_id = verify_qr_payload(tampered_payload)
    assert verified_id is None, "Tampered payload should fail verification"
    print("✓ Tampered payload rejected correctly")
    
    print("\n✅ QR signature tests passed!\n")

def test_application_structure():
    """Test application file structure"""
    print("Testing application structure...")
    import os
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'config.sample.py',
        'templates/base.html',
        'templates/login.html',
        'templates/dashboard.html',
        'templates/generate.html',
        'templates/preview.html',
        'templates/scanner.html',
        'templates/database.html'
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Missing file: {file}"
    
    print(f"✓ All {len(required_files)} required files present")
    print("\n✅ Application structure tests passed!\n")

if __name__ == '__main__':
    print("=" * 60)
    print("Diwali E-Pass System - Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_application_structure()
        test_database()
        test_qr_signature()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print()
        print("You can now run the application:")
        print("  python app.py")
        print()
        print("Then open your browser to:")
        print("  http://localhost:5000")
        print()
        print("Login with:")
        print("  Username: admin1")
        print("  Password: diwaliparty@123")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
