# ✅ Vercel Deployment Checklist

Use this checklist to ensure your deployment is successful.

## Pre-Deployment Verification ✓

These files should already exist in the repository. Verify they're present:

- [ ] `vercel.json` configuration file exists
- [ ] `.vercelignore` file configured to exclude unnecessary files
- [ ] `api/index.py` serverless function handler created
- [ ] `requirements.txt` includes all dependencies (including `mangum`)
- [ ] Frontend files exist in `frontend/` directory
- [ ] Documentation created (`DEPLOYMENT.md`, `QUICKSTART_DEPLOY.md`)

## Database Setup (Required)

Before deploying, choose ONE of these database options:

- [ ] **Option 1: Vercel Postgres** (Recommended for Vercel users)
  ```bash
  vercel integration add postgres
  ```

- [ ] **Option 2: External Provider** (Free options available)
  - [ ] [Supabase](https://supabase.com) - Free tier: 500 MB
  - [ ] [Neon](https://neon.tech) - Free tier: 3 GB  
  - [ ] [Railway](https://railway.app) - Free tier: $5 credit/month

- [ ] Copy DATABASE_URL connection string (format: `postgresql://user:pass@host:5432/db?sslmode=require`)

## Deployment Steps

### Method A: Dashboard Deployment (Easiest)

- [ ] Go to [vercel.com/new](https://vercel.com/new)
- [ ] Click "Import Git Repository"
- [ ] Select `neelsabhaya/AI-Resume` repository
- [ ] Framework Preset: Select "Other"
- [ ] Add environment variables:
  - [ ] `DATABASE_URL` = `<your-postgresql-url>`
  - [ ] `DEBUG` = `false`
- [ ] Click "Deploy"
- [ ] Wait 2-3 minutes for deployment
- [ ] Copy deployment URL (e.g., `https://your-app.vercel.app`)

### Method B: CLI Deployment

- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Login: `vercel login`
- [ ] Deploy preview: `vercel`
- [ ] Add environment variables:
  ```bash
  vercel env add DATABASE_URL
  vercel env add DEBUG
  ```
- [ ] Deploy to production: `vercel --prod`

## Post-Deployment Testing

Test these endpoints to verify your deployment:

- [ ] **Home Page**: `https://your-app.vercel.app/`
  - [ ] Dashboard loads correctly
  - [ ] No console errors in browser DevTools

- [ ] **API Endpoints**:
  - [ ] GET `/api/jobs` - Returns empty list or existing jobs
  - [ ] GET `/docs` - Interactive API documentation loads

- [ ] **Database Connection**:
  - [ ] Create a test job via `/api/upload-jd`
  - [ ] Verify it appears in `/api/jobs`

- [ ] **File Upload** (Optional):
  - [ ] Upload test resume
  - [ ] Verify processing completes

## Performance Optimization (Optional)

- [ ] Set up monitoring (Vercel Analytics, Sentry, etc.)
- [ ] Configure custom domain (if desired)
- [ ] Set up warm-up service to reduce cold starts
- [ ] Review Vercel usage dashboard

## Common Issues & Solutions

### Issue: "Database connection failed"
- [ ] Verify `DATABASE_URL` is set correctly
- [ ] Check database is accessible (not behind firewall)
- [ ] Ensure connection string includes `?sslmode=require`

### Issue: "Function timeout exceeded"
- [ ] Check function execution time in Vercel logs
- [ ] Optimize heavy operations (ML model loading)
- [ ] Consider upgrading to Pro plan (60s timeout vs 10s)

### Issue: "Module not found"
- [ ] Verify all dependencies are in `requirements.txt`
- [ ] Check build logs in Vercel dashboard
- [ ] Ensure Python version compatibility (3.10-3.13)

### Issue: "404 Not Found" for API routes
- [ ] Verify API URL format: `https://your-app.vercel.app/api/endpoint`
- [ ] Check `vercel.json` routes configuration
- [ ] Review deployment logs for errors

## Upgrade Considerations

### Vercel Hobby Plan (Free)
- ✅ Unlimited deployments
- ✅ Automatic SSL
- ⚠️ 10 second function timeout
- ⚠️ Cold starts (30+ seconds)

### Vercel Pro Plan ($20/month)
- ✅ 60 second function timeout
- ✅ Faster cold starts
- ✅ Analytics & monitoring
- ✅ Better for production use

## Resources

- 📖 [QUICKSTART_DEPLOY.md](./QUICKSTART_DEPLOY.md) - Quick 2-minute guide
- 📖 [DEPLOYMENT.md](./DEPLOYMENT.md) - Comprehensive deployment guide
- 🔗 [Vercel Documentation](https://vercel.com/docs)
- 🔗 [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- 🔗 [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

## Next Steps

After successful deployment:

- [ ] Share deployment URL with your team
- [ ] Set up custom domain (optional)
- [ ] Configure environment-specific settings
- [ ] Monitor usage and performance
- [ ] Plan for scaling if needed

---

## ✨ Deployment Complete!

Your AI Resume Screening System is now live on Vercel!

**Deployment URL**: `https://__________.vercel.app` (fill in your URL)

Share feedback or issues at: [GitHub Issues](https://github.com/neelsabhaya/AI-Resume/issues)
