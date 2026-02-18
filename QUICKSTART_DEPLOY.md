# 🚀 Quick Deploy to Vercel

Your repository is already configured for Vercel! Follow these steps to deploy in minutes.

## ⚡ Fastest Method: Deploy via Vercel Dashboard

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/neelsabhaya/AI-Resume)

### Step-by-Step:

1. **Click the "Deploy with Vercel" button above** (or go to [vercel.com/new](https://vercel.com/new))

2. **Import your repository:**
   - Select "Import Git Repository"
   - Choose `neelsabhaya/AI-Resume`
   - Click "Import"

3. **Configure project settings:**
   - Framework Preset: **Other** (Vercel will auto-detect configuration)
   - Root Directory: `./` (leave as default)
   - Build Command: _(leave empty, not needed)_
   - Output Directory: _(leave empty, not needed)_

4. **Set up required environment variables:**
   
   Click "Environment Variables" and add:
   
   | Variable | Value | Required |
   |----------|-------|----------|
   | `DATABASE_URL` | `postgresql://user:pass@host:5432/db?sslmode=require` | ✅ YES |
   | `DEBUG` | `false` | ✅ YES |
   
   > ⚠️ **Important:** You MUST use PostgreSQL (not SQLite) for Vercel deployment. See database setup below.

5. **Click "Deploy"** and wait 2-3 minutes

6. **Visit your app** at `https://your-project.vercel.app` ✨

---

## 🗄️ Database Setup (Required)

Vercel requires PostgreSQL because SQLite doesn't work in serverless environments.

### Quick Options:

#### Option 1: Vercel Postgres (Easiest)
```bash
# In your Vercel project dashboard
vercel integration add postgres
# This automatically sets DATABASE_URL
```

#### Option 2: Free External Providers
- **[Supabase](https://supabase.com)** - Free tier: 500 MB
- **[Neon](https://neon.tech)** - Free tier: 3 GB
- **[Railway](https://railway.app)** - Free tier: $5 credit/month

After creating a database, copy the connection URL and paste it as `DATABASE_URL` in Vercel environment variables.

---

## 💻 Alternative: Deploy via CLI

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy to preview
vercel

# 4. Set environment variables
vercel env add DATABASE_URL
# Paste your PostgreSQL URL when prompted

vercel env add DEBUG
# Enter: false

# 5. Deploy to production
vercel --prod

# 6. Open in browser
vercel open
```

---

## ✅ Post-Deployment Checklist

After deployment:

- [ ] Visit your app URL (e.g., `https://your-app.vercel.app`)
- [ ] Test the dashboard at `/`
- [ ] Test API at `/api/jobs`
- [ ] Check API docs at `/docs`
- [ ] Verify database connection is working
- [ ] (Optional) Set up custom domain in Vercel settings

---

## 🆘 Troubleshooting

### "Database connection failed"
→ Make sure `DATABASE_URL` environment variable is set with a valid PostgreSQL URL

### "Module not found" error
→ Check build logs in Vercel dashboard. All dependencies should be in `requirements.txt`

### "Function timeout exceeded"
→ Vercel Hobby plan has 10s timeout. Upgrade to Pro for 60s or optimize your code

### API returns 404
→ Make sure you're using the correct URL format: `https://your-app.vercel.app/api/endpoint`

---

## 📚 Need More Details?

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for:
- Comprehensive deployment guide
- Performance optimization tips
- Serverless limitations and workarounds
- Advanced configuration options
- Alternative deployment methods

---

## 🎉 That's It!

Your AI Resume Screening System is now live on Vercel!

**Next Steps:**
1. Share your app URL with your team
2. Set up a custom domain (optional)
3. Monitor usage in Vercel dashboard
4. Consider upgrading to Pro if you hit limits

Happy recruiting! 🚀
