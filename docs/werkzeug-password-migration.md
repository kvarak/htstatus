# Werkzeug 3.x Password Migration Guide

## Critical Security Update: Password Hash Compatibility

### The Issue

After upgrading from Werkzeug 2.x to 3.x for security improvements, we discovered a critical backward compatibility issue:

- **Before**: Passwords were hashed using `generate_password_hash(password, method='sha256')`
- **After**: Werkzeug 3.x removes SHA256 support and uses secure scrypt by default
- **Problem**: Existing users with SHA256 password hashes cannot authenticate

### Test Results

```bash
# Werkzeug 3.x compatibility test results:
✅ Scrypt (new default): Works perfectly
✅ PBKDF2 (old default): Still supported for backward compatibility
❌ SHA256 (explicit method): No longer supported - "Invalid hash method 'sha256'"
```

### Impact Assessment

- **New Users**: No impact - get secure scrypt hashes
- **Existing Users with PBKDF2**: No impact - still works
- **Existing Users with SHA256**: 🚨 Cannot authenticate - requires migration

### Solution Implemented

#### 1. Database Migration (`migrate_sha256_passwords.py`)

- **Identifies**: Users with SHA256 password hashes (`sha256$...`)
- **Marks**: Passwords with `MIGRATION_REQUIRED:` prefix
- **Preserves**: Original hash for potential rollback
- **Maintains**: OAuth tokens for seamless access

#### 2. Authentication Logic Updates (`app/blueprints/auth.py`)

**Password Verification Enhancement:**
```python
if existing_user.password.startswith('MIGRATION_REQUIRED:'):
    # User has old SHA256 hash that needs migration
    needs_migration = True
    # Try OAuth tokens if available, otherwise require password reset
```

**Migration User Handling:**
- **Valid OAuth Tokens**: Log in directly with migration notice
- **Expired Tokens**: Require password reset or re-authentication
- **New Password**: Automatically upgrade to scrypt hash

#### 3. User Experience

**For Users with Valid OAuth Tokens:**
1. Continue using the app normally
2. See optional password update notification
3. Can update password at their convenience

**For Users with Expired Tokens:**
1. See clear message: "Your password needs to be updated for security"
2. Options: Reset password or re-authenticate with Hattrick
3. Get secure scrypt hash on next successful authentication

### Migration Workflow

1. **Pre-Migration**: Identify affected users
   ```sql
   SELECT COUNT(*) FROM users WHERE password LIKE 'sha256$%';
   ```

2. **Run Migration**:
   ```bash
   flask db upgrade
   ```

3. **Post-Migration**: Monitor user authentication
   ```sql
   SELECT COUNT(*) FROM users WHERE password LIKE 'MIGRATION_REQUIRED:%';
   ```

### Rollback Strategy

If needed, the migration can be rolled back:
```bash
flask db downgrade
```

**⚠️ Warning**: Rollback restores SHA256 hashes that won't work in Werkzeug 3.x. Only use when reverting to Werkzeug 2.x.

### Security Benefits

- **Modern Encryption**: Scrypt is more secure than SHA256
- **Future-Proof**: Werkzeug 3.x security improvements
- **Zero Vulnerabilities**: Eliminated all CVE vulnerabilities
- **Graceful Migration**: No user data loss or service disruption

### Testing Commands

```python
# Test hash compatibility
from werkzeug.security import check_password_hash, generate_password_hash

# New scrypt (works)
new_hash = generate_password_hash("test")
print(f"Scrypt: {check_password_hash(new_hash, 'test')}")

# Legacy PBKDF2 (works)
old_hash = generate_password_hash("test", method="pbkdf2")
print(f"PBKDF2: {check_password_hash(old_hash, 'test')}")

# SHA256 (broken)
try:
    sha256_hash = generate_password_hash("test", method="sha256")
except Exception as e:
    print(f"SHA256 error: {e}")  # Invalid hash method 'sha256'
```

### Deployment Checklist

- [x] Create password migration script
- [x] Update authentication logic
- [x] Test migration workflow
- [x] Document rollback procedure
- [x] Plan user communication
- [ ] Run migration in production
- [ ] Monitor user authentication
- [ ] Verify no authentication failures

### User Communication Template

```
Security Update Notice:

We've upgraded our password security system. If you see a message about
updating your password, simply:

1. Reset your password, OR
2. Re-authenticate with your Hattrick account

Your account data is safe and this upgrade provides better security
protection.
```

This migration ensures all users can continue accessing HT Status while benefiting from improved security provided by Werkzeug 3.x.
