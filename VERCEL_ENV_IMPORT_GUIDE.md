# Vercel Environment Variables Import Guide

## Quick Start

Copy these environment variables to Vercel:

### 🔴 REQUIRED (Must have)

```
FLASK_ENV=production
SECRET_KEY=<generate-a-strong-random-key-32-chars-minimum>
JWT_SECRET_KEY=<generate-another-random-key-32-chars-minimum>
MYSQLHOST=<your-mysql-host>
MYSQLPORT=3306
MYSQLUSER=<your-mysql-username>
MYSQLPASSWORD=<your-mysql-password>
MYSQLDATABASE=torida
```

### 🟡 RECOMMENDED (For production)

```
CORS_ORIGINS=*
PUBLIC_API_BASE_URL=https://your-vercel-app-name.vercel.app
```

### 🟢 OPTIONAL (Enhanced features)

```
JWT_ACCESS_TOKEN_EXPIRES=86400
JWT_REFRESH_TOKEN_EXPIRES=2592000
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=Torida <noreply@torida.com>
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=10
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

---

## Step-by-Step Import to Vercel

### Step 1: Go to Vercel Dashboard
1. Visit https://vercel.com/dashboard
2. Click on your project (Torida-V2 or your project name)

### Step 2: Open Environment Variables
1. Click **Settings** (top navigation)
2. Click **Environment Variables** (left sidebar)

### Step 3: Add Variables (One by One)

For each variable below:

1. Click **Add New**
2. In **Name** field: Enter the variable name (e.g., `FLASK_ENV`)
3. In **Value** field: Enter the value
4. Under **Environments**: Check all three:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
5. Click **Add**

### Step 4: Verify and Deploy

1. After adding all variables, scroll to top
2. Click **Deploy** or **Redeploy**
3. Wait for deployment to complete

---

## Environment Variables Explained

### Database Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `MYSQLHOST` | `db.example.com` | Your MySQL server hostname |
| `MYSQLPORT` | `3306` | MySQL port (default: 3306) |
| `MYSQLUSER` | `torida_user` | MySQL username |
| `MYSQLPASSWORD` | `secure_password_123` | MySQL password |
| `MYSQLDATABASE` | `torida` | Database name |

### Security Variables

| Variable | Description |
|----------|-------------|
| `FLASK_ENV` | Set to `production` on Vercel |
| `SECRET_KEY` | Flask secret key (generate random string) |
| `JWT_SECRET_KEY` | JWT secret key (generate random string) |

### How to Generate Random Keys

**Using Python:**
```python
import secrets
print(secrets.token_urlsafe(32))  # Run twice for SECRET_KEY and JWT_SECRET_KEY
```

**Using OpenSSL:**
```bash
openssl rand -base64 32
```

**Online Generator:**
Visit: https://generate-random.org/encryption-keys-generator

---

## Where to Get Database Credentials

### If using Railway:
1. Go to https://railway.app
2. Click your project
3. Click the MySQL database
4. Copy credentials from **Connect** tab:
   - Host
   - Port
   - Username
   - Password

### If using AWS RDS:
1. Go to AWS Console → RDS → Databases
2. Click your database
3. Find connection details in **Connectivity & security**

### If using Google Cloud SQL:
1. Go to Google Cloud Console → SQL
2. Click your instance
3. Find connection info in **Instance details**

---

## Testing After Deployment

After deploying with environment variables, test these endpoints:

```bash
# Root endpoint (should return success message)
curl https://your-app-name.vercel.app/

# Health check
curl https://your-app-name.vercel.app/health

# API info
curl https://your-app-name.vercel.app/api
```

---

## Common Issues & Solutions

### ❌ 502 Bad Gateway
**Solution**: Check Vercel logs for database connection errors
```bash
vercel logs
```

### ❌ Database Connection Failed
- Verify all MYSQL_* variables are correct
- Check database is accessible from Vercel IPs
- Ensure database firewall allows external connections

### ❌ CORS Errors
- Set `CORS_ORIGINS=*` or your frontend URL
- Verify request headers match CORS configuration

### ❌ JWT Secret Issues
- Ensure `JWT_SECRET_KEY` is set
- Must be different from `SECRET_KEY`
- Should be at least 32 characters

---

## Important Notes

1. **Never commit `.env` file** - only `.env.example`
2. **Use strong passwords** - especially for production databases
3. **Rotate secrets regularly** - update SECRET_KEY and JWT_SECRET_KEY periodically
4. **Use environment variables** - never hardcode sensitive data
5. **Test before deployment** - verify all variables work locally first

---

## Vercel CLI Alternative

If you have Vercel CLI installed:

```bash
# Login to Vercel
vercel login

# Set environment variables
vercel env add FLASK_ENV
vercel env add SECRET_KEY
# ... repeat for each variable

# Deploy with variables
vercel --prod
```

---

## Need Help?

- **Vercel Docs**: https://vercel.com/docs/environment-variables
- **Flask Docs**: https://flask.palletsprojects.com/
- **SQLAlchemy Docs**: https://sqlalchemy.org/
