# 🚀 Deployment Guide

## Pre-Deployment Checklist

### ✅ Security Configuration

**CRITICAL: Change these before going live!**

1. **Flask Secret Key** (in `app.py` line 11)
   ```python
   # Current (INSECURE):
   app.secret_key = 'your-secret-key-change-this-in-production'
   
   # Change to:
   app.secret_key = 'YOUR-RANDOM-SECRET-HERE'
   ```
   
   Generate secure key:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. **QR Signing Secret** (in `app.py` line 12)
   ```python
   # Current (INSECURE):
   QR_SECRET = 'qr-signing-secret-change-this-too'
   
   # Change to:
   QR_SECRET = 'YOUR-QR-SECRET-HERE'
   ```

3. **Debug Mode** (in `app.py` line 504)
   ```python
   # Change from:
   app.run(debug=True, host='0.0.0.0', port=5000)
   
   # To:
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

### ✅ Environment Preparation

- [ ] Python 3.7+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database initialized: Run app once to create `epass.db`
- [ ] Test admin login works
- [ ] Test pass generation works
- [ ] Test QR scanner works (on mobile if applicable)

---

## Deployment Options

### Option 1: Local Development Server (Testing Only)

**Suitable for:** Testing, small private events (10-20 concurrent users)

```bash
python app.py
```

Access at: `http://localhost:5000`

⚠️ **Not recommended for production!**

---

### Option 2: Production Server with Gunicorn (Recommended)

**Suitable for:** Real events, up to 100+ concurrent users

#### Step 1: Install Gunicorn
```bash
pip install gunicorn
```

#### Step 2: Run with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Options explained:**
- `-w 4` = 4 worker processes (adjust based on CPU cores)
- `-b 0.0.0.0:5000` = Bind to all interfaces on port 5000
- `app:app` = Module name : Flask app variable

#### Step 3: Run in Background (Optional)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app --daemon
```

Or use `screen` or `tmux`:
```bash
screen -S epass
gunicorn -w 4 -b 0.0.0.0:5000 app:app
# Press Ctrl+A then D to detach
```

---

### Option 3: Production with Nginx + Gunicorn

**Suitable for:** Large events, multiple services, SSL/HTTPS

#### Setup Nginx Reverse Proxy

1. Install Nginx:
   ```bash
   sudo apt install nginx  # Ubuntu/Debian
   ```

2. Create Nginx config (`/etc/nginx/sites-available/epass`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
       
       client_max_body_size 10M;
   }
   ```

3. Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/epass /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. Run Gunicorn:
   ```bash
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```

---

### Option 4: HTTPS with Let's Encrypt (Required for Mobile Camera)

**IMPORTANT:** Mobile browsers require HTTPS for camera access!

#### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

#### Get SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

Follow prompts, certificate auto-renews.

#### Update Nginx Config
Certbot does this automatically, but verify:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        # ... rest of config
    }
}
```

---

## Platform-Specific Deployments

### Windows Server

**Using IIS + Python**

1. Install Python and dependencies
2. Use `waitress` instead of gunicorn:
   ```bash
   pip install waitress
   python -c "from waitress import serve; from app import app; serve(app, host='0.0.0.0', port=5000)"
   ```

**As Windows Service**

Use `NSSM` (Non-Sucking Service Manager):
```bash
nssm install EPassService "C:\Python\python.exe" "C:\path\to\app.py"
nssm start EPassService
```

---

### Linux Server (Systemd)

Create service file: `/etc/systemd/system/epass.service`

```ini
[Unit]
Description=Diwali E-Pass System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/epass
Environment="PATH=/var/www/epass/venv/bin"
ExecStart=/var/www/epass/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable epass
sudo systemctl start epass
sudo systemctl status epass
```

---

### Cloud Platforms

#### Heroku

1. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```

2. Add `gunicorn` to `requirements.txt`

3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

#### AWS EC2

1. Launch Ubuntu instance
2. SSH into instance
3. Install Python and dependencies
4. Follow Linux Server setup above
5. Configure security group (open port 80/443)

#### Google Cloud / Azure

Similar to AWS - use VM instances and follow Linux setup.

---

## Database Considerations

### Backup Strategy

**Before Event:**
```bash
cp epass.db epass_backup_$(date +%Y%m%d).db
```

**During Event (every hour):**
```bash
# Automated backup script
while true; do
    cp epass.db backups/epass_$(date +%Y%m%d_%H%M%S).db
    sleep 3600
done
```

**After Event:**
```bash
cp epass.db epass_final_$(date +%Y%m%d).db
```

### Migrate to PostgreSQL (for 500+ passes)

1. Install PostgreSQL:
   ```bash
   sudo apt install postgresql
   pip install psycopg2-binary
   ```

2. Update `app.py`:
   ```python
   import psycopg2
   
   DATABASE_URL = "postgresql://user:password@localhost/epass"
   
   def get_db():
       conn = psycopg2.connect(DATABASE_URL)
       return conn
   ```

3. Minor SQL syntax adjustments needed

---

## Performance Optimization

### For High Traffic

**1. Increase Workers**
```bash
gunicorn -w 8 -b 0.0.0.0:5000 app:app
```
Rule of thumb: `2 * CPU_cores + 1`

**2. Enable Keep-Alive**
```bash
gunicorn -w 4 --keep-alive 5 -b 0.0.0.0:5000 app:app
```

**3. Use Connection Pooling** (for PostgreSQL)
```python
from psycopg2 import pool
db_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)
```

**4. Cache Static Files** (in Nginx)
```nginx
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Monitoring & Logs

### Enable Logging

Add to `app.py`:
```python
import logging
logging.basicConfig(
    filename='epass.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

### Monitor with Gunicorn
```bash
gunicorn -w 4 --access-logfile access.log --error-logfile error.log app:app
```

### Real-Time Monitoring
```bash
tail -f epass.log
tail -f access.log
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Permission Denied
```bash
chmod +x app.py
chown www-data:www-data -R /var/www/epass
```

### Database Locked
- SQLite doesn't handle concurrent writes well
- Solution: Upgrade to PostgreSQL
- Or reduce worker count to 1

### Camera Not Working
- Ensure HTTPS is enabled
- Check browser permissions
- Test on localhost first

---

## Security Hardening

### 1. Firewall Rules
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Hide Flask Headers
```python
from flask import Flask
app = Flask(__name__)
app.config['SERVER_NAME'] = None  # Hide Flask version
```

### 3. Rate Limiting (Optional)
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/scan', methods=['POST'])
@limiter.limit("10 per minute")
def api_scan():
    # ...
```

### 4. CORS (if needed)
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

---

## Post-Deployment Checklist

- [ ] Changed all secret keys
- [ ] Debug mode disabled
- [ ] HTTPS configured (for mobile scanning)
- [ ] Database backup scheduled
- [ ] Tested login on production URL
- [ ] Tested pass generation
- [ ] Tested QR scanner on mobile device
- [ ] Tested from different networks
- [ ] Monitoring/logging enabled
- [ ] Emergency contact plan ready
- [ ] Backup server available (if possible)

---

## Emergency Procedures

### Server Down
1. Check service status: `systemctl status epass`
2. Check logs: `tail -f error.log`
3. Restart service: `systemctl restart epass`
4. If database corrupt: restore from backup

### High Load
1. Check CPU/memory: `top` or `htop`
2. Increase workers temporarily
3. Restart Gunicorn
4. Consider load balancer

### Database Issues
1. Stop application
2. Restore from latest backup
3. Restart application
4. Export CSV immediately

---

## Support & Maintenance

### Regular Maintenance
- **Daily**: Check logs for errors
- **Weekly**: Backup database
- **Monthly**: Update dependencies
- **After Event**: Archive data, clean up

### Updates
```bash
pip install --upgrade -r requirements.txt
```

---

## Cost Estimates

### Small Event (50-200 passes)
- **Local Server**: Free (use existing hardware)
- **Cloud VM**: $5-10/month (DigitalOcean, AWS EC2)

### Medium Event (200-500 passes)
- **Cloud VM**: $10-20/month
- **Domain + SSL**: $10-15/year

### Large Event (500+ passes)
- **Cloud VM**: $20-50/month
- **PostgreSQL**: $10-30/month
- **Load Balancer**: $10-20/month

---

**Ready to Deploy? 🚀**

Test thoroughly, backup often, and have a great event! 🪔
