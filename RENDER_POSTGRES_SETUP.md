# 🔧 Render PostgreSQL Database Connection Setup

## ✅ Your app.py is already PostgreSQL-ready!

Maine already code me PostgreSQL support add kar diya hai. Ab sirf Render dashboard pe configuration karna hai.

---

## 📋 Step-by-Step Setup

### Step 1: Get PostgreSQL Connection String

1. **Render Dashboard me jao:** https://dashboard.render.com
2. **Left sidebar me "PostgreSQL" dikhai dega** - Click karo
3. **Apna database select karo** (jo tumne banaya hai)
4. **"Info" tab me jao**
5. **"Internal Database URL" copy karo**
   - Ye aisa dikhega: `postgresql://user:password@host/database`
   - Ye **INTERNAL URL** use karo (not External)

---

### Step 2: Set Environment Variable in Render Web Service

1. **Render Dashboard me jao**
2. **Left sidebar me "Web Services" click karo**
3. **Apni web service (diwali-epass ya jo bhi naam diya) select karo**
4. **"Environment" tab click karo**
5. **"Add Environment Variable" button click karo**
6. **Add karo:**
   ```
   Key: DATABASE_URL
   Value: [Paste karo Internal Database URL jo copy kiya]
   ```
7. **"Save Changes" click karo**
8. **App automatically redeploy hoga** (2-3 minutes)

---

## 🗑️ Step 3: Remove epass.db from Git

**Local machine pe (apne computer pe) ye commands run karo:**

```bash
# Navigate to project folder
cd c:\Users\meet1\OneDrive\Desktop\e-pass

# Remove epass.db from git tracking
git rm --cached epass.db

# Commit the change
git add .
git commit -m "Remove SQLite database, use PostgreSQL"

# Push to GitHub
git push
```

---

## 📝 Step 4: Update .gitignore

Check karo ki `.gitignore` file me ye line hai ki nahi:

<function_calls>
<invoke name="Read">
<parameter name="file_path">c:\Users\meet1\OneDrive\Desktop\e-pass\.gitignore
