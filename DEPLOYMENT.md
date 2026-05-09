# Railway Deployment

This backend repo is ready to deploy on Railway.

## Required service variables

Set these in Railway before the first production deploy:

```env
FLASK_ENV=production
SECRET_KEY=your-long-random-secret
JWT_SECRET_KEY=your-long-random-jwt-secret
MYSQL_URL=mysql://user:password@host:3306/torida
PUBLIC_API_BASE_URL=https://your-backend.up.railway.app
CORS_ORIGINS=https://your-frontend.vercel.app
```

If you use a custom domain, replace the Railway/Vercel URLs with your real domains.

## Uploads

Product images are stored on disk. On Railway, attach a volume and set:

```env
UPLOAD_FOLDER=/data/uploads
```

Without a volume, uploaded files will be lost on redeploy/restart.

## Deploy steps

1. Push this repo to GitHub.
2. In Railway, create a new service from the GitHub repo.
3. Add a MySQL service, then set `MYSQL_URL` on the backend service to that connection string.
4. Add the variables listed above.
5. Deploy. Railway will use `railway.json`, start `gunicorn`, and healthcheck `GET /health`.

## After the first deploy

The app creates tables automatically on boot. If you also want the seed data (roles, permissions, governorates, user types), run this once in a Railway shell:

```bash
flask --app run.py seed-db
```
