# Holly's Closet — Web App

A hosted web gallery for managing images on Cloudinary. Built with Flask + vanilla JS, deployable to Render for free.

---

## Deploy to Railway

### 1. Create a Railway account
Go to [railway.app](https://railway.app) and sign up (free tier works).

### 2. Push this folder to GitHub
Create a new **private** GitHub repo and push this folder to it:
```bash
git init
git add .
git commit -m "Holly's Closet web app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 3. Create a Railway project
- Click **New Project** → **Deploy from GitHub repo**
- Select your repo
- Railway will auto-detect Python and install dependencies

### 4. Set environment variables
In your Railway project → **Variables**, add these:

| Variable | Value |
|---|---|
| `CLOUDINARY_CLOUD_NAME` | `dk4a1il6a` |
| `CLOUDINARY_API_KEY` | `824821989928729` |
| `CLOUDINARY_API_SECRET` | `4jByQxPuSY5JxXEG8pcAIlh9HhI` |
| `APP_SECRET_KEY` | any long random string (e.g. `openssl rand -hex 32`) |
| `CHATRO_CODE` | `[img]SNIPPET[/img][color #a0a0a0]holly~.[/color]` |
| `UNDERGROUND_CODE` | `<img src="SNIPPET"> holly~.` |
| `AVAILABLE_TAGS` | `Favorites,Lair,LoL,Naked Nights,Tushday,Hickies,Parties` |

### 5. Done!
Railway will build and deploy. Click the generated `.up.railway.app` URL to access your closet.

---

## Features

- **Launcher screen** — door click enters the gallery, three settings pills below
- **Gallery** — 5-column image grid with lazy-loading, shimmer skeletons
- **Search** — real-time filename search
- **Tag filters** — filter pills for all your tags (All / tag / hidden)
- **Sort** — click the count badge to toggle newest-first
- **Bottom dock** — appears when an image is selected; shows thumbnail, filename, tags
  - **Link** — copies the Cloudinary URL
  - **Chatro** — copies the formatted code with the URL injected
  - **Underground** — copies the underground formatted code
  - **Tag** — opens a tag picker dialog
  - **Rename** — renames on Cloudinary
  - **Delete** — confirms then permanently deletes
- **Upload** — select multiple files; skips duplicates, shows progress
- **Codes dialog** — edit Chatro/Underground templates in the launcher
- **Tags dialog** — edit the available tag list in the launcher

---

## Local development

```bash
pip install -r requirements.txt

# Create a .env file:
export CLOUDINARY_CLOUD_NAME=dk4a1il6a
export CLOUDINARY_API_KEY=824821989928729
export CLOUDINARY_API_SECRET=4jByQxPuSY5JxXEG8pcAIlh9HhI
export APP_SECRET_KEY=dev-secret

python app.py
# → open http://localhost:5000
```

---

## Security note

Your `API_SECRET` is stored only in Railway's environment variables — it never touches the browser. All Cloudinary calls go through the Flask backend. Keep your Railway project **private** and rotate the secret if it's ever exposed.
