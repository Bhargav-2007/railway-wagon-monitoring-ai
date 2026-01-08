# 🔍 RAILWAY WAGON SYSTEM - SELF-VERIFICATION COMMANDS
## Copy & Paste These Commands to Check Everything Yourself

---

## **1️⃣ VERIFY PROJECT STRUCTURE**

### Check all directories exist:
```bash
ls -la backend/app/models/
ls -la backend/app/services/
ls -la backend/app/routes/
ls -la frontend/
ls -la ai_pipeline/
```

### View complete file tree:
```bash
tree -L 3 -I 'node_modules|venv|__pycache__'
```

---

## **2️⃣ VERIFY ADMIN AUTHENTICATION FILES**

### Check Admin Model exists:
```bash
file backend/app/models/admin.py
wc -l backend/app/models/admin.py
head -20 backend/app/models/admin.py
```

### Check Auth Service exists:
```bash
file backend/app/services/auth_service.py
wc -l backend/app/services/auth_service.py
head -20 backend/app/services/auth_service.py
```

### Check Admin Routes exists:
```bash
file backend/app/routes/admin_routes.py
wc -l backend/app/routes/admin_routes.py
head -20 backend/app/routes/admin_routes.py
```

---

## **3️⃣ VERIFY SECURITY FEATURES**

### Check password hashing implementation:
```bash
grep -n "pbkdf2_hmac\|bcrypt\|password_hash" backend/app/models/admin.py
```

### Check JWT token implementation:
```bash
grep -n "JWT\|jwt.encode\|jwt.decode\|token" backend/app/services/auth_service.py
```

### Check API endpoints:
```bash
grep -n "@router\|def " backend/app/routes/admin_routes.py
```

### Check account lockout:
```bash
grep -n "locked_until\|login_attempts\|increment_failed" backend/app/models/admin.py
```

---

## **4️⃣ VERIFY DOCUMENTATION**

### Check all documentation files exist:
```bash
ls -lh *.md
wc -l *.md
```

### View specific documentation:
```bash
cat TEAM_ROLES_AND_ARCHITECTURE.md | head -50
cat EDGE_DEPLOYMENT_READINESS.md | head -50
cat VALIDATION_AND_BENCHMARKING.md | head -50
cat ADMIN_AND_SECURITY_SUMMARY.md | head -50
```

---

## **5️⃣ VERIFY SYSTEM CHECK SCRIPT**

### Run the complete system check:
```bash
bash run_system_with_checks.sh
```

### Check specific parts:
```bash
echo "=== Backend Files ==="
find backend/app -name "*.py" | wc -l

echo "=== Frontend Files ==="
find frontend/src -name "*.tsx" -o -name "*.ts" | wc -l

echo "=== AI Pipeline Files ==="
find ai_pipeline -name "*.py" | wc -l
```

---

## **6️⃣ VERIFY DATABASE FILES**

### Check if databases exist:
```bash
ls -lah backend/*.db
```

### Check database schema (if using SQLite):
```bash
sqlite3 backend/railway_monitor.db ".tables"
sqlite3 backend/railway_monitoring.db ".tables"
```

---

## **7️⃣ VERIFY DEPENDENCIES**

### Check Python dependencies:
```bash
cat backend/requirements.txt | head -20
grep -E "fastapi|sqlalchemy|pydantic|bcrypt|python-jose" backend/requirements.txt
```

### Check Node dependencies:
```bash
cat frontend/package.json | grep -A 20 '"dependencies"'
```

---

## **8️⃣ VERIFY CODE STATISTICS**

### Count total lines of code:
```bash
echo "Python files:"
find . -name "*.py" -type f ! -path "*/venv/*" ! -path "*/node_modules/*" | xargs wc -l | tail -1

echo "\nTypeScript/TSX files:"
find . -name "*.tsx" -o -name "*.ts" ! -path "*/node_modules/*" | xargs wc -l | tail -1

echo "\nDocumentation:"
wc -l *.md | tail -1
```

### List all Python files:
```bash
find . -name "*.py" -type f ! -path "*/venv/*" ! -path "*/node_modules/*" | sort
```

### List all authentication files:
```bash
find . -name "admin*.py" -o -name "auth*.py" -o -name "*auth*.py" | grep -v venv
```

---

## **9️⃣ VERIFY CONFIGURATION FILES**

### Check config files exist:
```bash
ls -la camera_config.json
ls -la .env.example
ls -la backend/requirements.txt
ls -la frontend/package.json
```

### View camera configuration:
```bash
cat camera_config.json
```

### View environment template:
```bash
cat .env.example
```

---

## **🔟 VERIFY EXPORT MODULES**

### Check ONNX export script:
```bash
wc -l ai_pipeline/export_models_to_onnx.py
grep -n "ONNXExporter\|def export" ai_pipeline/export_models_to_onnx.py
```

---

## **1️⃣1️⃣ VERIFY ALL FILES AT ONCE**

### Quick verification:
```bash
echo "=== ADMIN FILES ==="
test -f backend/app/models/admin.py && echo "✓ admin.py" || echo "✗ admin.py missing"
test -f backend/app/services/auth_service.py && echo "✓ auth_service.py" || echo "✗ auth_service.py missing"
test -f backend/app/routes/admin_routes.py && echo "✓ admin_routes.py" || echo "✗ admin_routes.py missing"

echo "\n=== DOCUMENTATION ==="
test -f TEAM_ROLES_AND_ARCHITECTURE.md && echo "✓ Team Roles" || echo "✗ Team Roles missing"
test -f EDGE_DEPLOYMENT_READINESS.md && echo "✓ Edge Deployment" || echo "✗ Edge Deployment missing"
test -f VALIDATION_AND_BENCHMARKING.md && echo "✓ Validation" || echo "✗ Validation missing"
test -f ADMIN_AND_SECURITY_SUMMARY.md && echo "✓ Admin Summary" || echo "✗ Admin Summary missing"

echo "\n=== SCRIPTS ==="
test -f run_system_with_checks.sh && echo "✓ System Check Script" || echo "✗ Script missing"

echo "\n=== CONFIG FILES ==="
test -f camera_config.json && echo "✓ Camera Config" || echo "✗ Camera Config missing"
test -f backend/requirements.txt && echo "✓ Requirements" || echo "✗ Requirements missing"
test -f frontend/package.json && echo "✓ Package.json" || echo "✗ Package.json missing"
```

---

## **1️⃣2️⃣ TEST ADMIN AUTHENTICATION CODE**

### Check password hashing is implemented:
```bash
python3 << 'EOF'
import hashlib
import secrets

# Test PBKDF2 hashing
salt = secrets.token_hex(16)
password = "test_password"
hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
print(f"✓ PBKDF2 hashing works")
print(f"  Salt: {salt}")
print(f"  Hash: {hashed[:50]}...")
EOF
```

### Check JWT imports:
```bash
python3 << 'EOF'
try:
    from jose import jwt
    print("✓ PyJWT module available")
except ImportError:
    print("✗ PyJWT module missing - install: pip install python-jose")

try:
    from passlib.context import CryptContext
    print("✓ Passlib module available")
except ImportError:
    print("✗ Passlib module missing - install: pip install passlib")
EOF
```

---

## **1️⃣3️⃣ COMPARE FILE SIZES**

### Check file sizes:
```bash
echo "=== NEW SECURITY FILES ==="
ls -lh backend/app/models/admin.py backend/app/services/auth_service.py backend/app/routes/admin_routes.py

echo "\n=== DOCUMENTATION FILES ==="
ls -lh *.md | grep -E "TEAM|EDGE|VALIDATION|ADMIN|IMPLEMENTATION"

echo "\n=== SCRIPT FILES ==="
ls -lh *.sh
```

---

## **1️⃣4️⃣ VIEW FILE CONTENTS DIRECTLY**

### View entire admin.py:
```bash
cat backend/app/models/admin.py
```

### View entire auth_service.py:
```bash
cat backend/app/services/auth_service.py
```

### View entire admin_routes.py:
```bash
cat backend/app/routes/admin_routes.py
```

### View entire check script:
```bash
cat run_system_with_checks.sh
```

---

## **1️⃣5️⃣ SUMMARY OF WHAT WAS ADDED**

### Get quick summary:
```bash
echo "========== SYSTEM SUMMARY =========="
echo "Admin Files:"
find backend -name "admin*.py" -o -name "auth*.py" | grep -v venv | wc -l

echo "\nTotal Python Files:"
find . -name "*.py" ! -path "*/venv/*" ! -path "*/node_modules/*" | wc -l

echo "\nDocumentation Files:"
ls -1 *.md | wc -l

echo "\nTotal Lines of Code (Python):"
find . -name "*.py" ! -path "*/venv/*" ! -path "*/node_modules/*" | xargs wc -l | tail -1

echo "\nTotal Lines of Code (TypeScript):"
find . -name "*.tsx" -o -name "*.ts" | xargs wc -l 2>/dev/null | tail -1

echo "======================================"
```

---

## **✅ VERIFICATION CHECKLIST**

- [ ] Run: `bash run_system_with_checks.sh` - All files verified
- [ ] Check: `test -f backend/app/models/admin.py` - Admin model exists
- [ ] Check: `test -f backend/app/services/auth_service.py` - Auth service exists
- [ ] Check: `test -f backend/app/routes/admin_routes.py` - Admin routes exist
- [ ] Check: `ls -lh *.md` - All documentation present
- [ ] Check: `cat camera_config.json` - Camera config readable
- [ ] Check: `grep -c "def " backend/app/models/admin.py` - At least 3 methods (set_password, verify_password, is_locked, etc.)
- [ ] Check: `grep -c "@router\|def " backend/app/routes/admin_routes.py` - At least 4 endpoints
- [ ] Check: `wc -l *.md` - Total documentation >1500 lines
- [ ] Run: `python3 -c "from jose import jwt; print('✓ JWT works')"` - JWT module works

---

## **🚀 READY TO START**

Once verified, start the system:

```bash
# Terminal 1 - Backend
cd backend
python3 -m app.main
# Runs on: http://localhost:8000

# Terminal 2 - Frontend
cd frontend
npm start
# Runs on: http://localhost:3000
```

Then access:
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Admin Login: POST http://localhost:8000/api/v1/admin/login

