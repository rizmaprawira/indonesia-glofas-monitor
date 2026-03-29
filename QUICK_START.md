# Quick Start Guide

Your GloFAS monitoring website is now fully built and working with real data!

## 🎯 Currently Running

**Dev server:** http://localhost:5173/

The website is serving **real GloFAS forecast data** for 1,000 monitoring points across Indonesia.

## ✅ What's Working

- **Interactive Map**: 1,000 river discharge monitoring points
- **Real Forecast Data**: 30-day lead times from your EWDS API download
- **All Features**: Lead time selector, metrics, search, hydrographs, CSV export
- **Production Build**: Ready in `dist/` folder

## 📋 Files Generated from Your Data

```
public/data/latest/
├── metadata.json                    # Forecast date, point count
├── points-index.json                # Locations of 1000 points
├── timeseries/
│   ├── P001.json                    # 30-day hydrograph for point 1
│   ├── P002.json
│   └── ... (1000 total)
├── values-24.json                   # All values for 24h lead time
├── values-48.json                   # All values for 48h lead time
└── ... (30 total - one per lead time)
```

## 🚀 Next Steps

### Option A: Deploy to GitHub Pages (Recommended)

```bash
# 1. Commit your code
git add .
git commit -m "Add Indonesia GloFAS monitor with real data"
git push origin main

# 2. In GitHub Settings → Secrets, add:
#    EWDS_API_KEY = your-personal-access-token

# 3. Go to Actions and run "Update GloFAS Data" workflow
# 4. Site auto-deploys to GitHub Pages
```

Your site will be live at: `https://YOUR_USERNAME.github.io/indonesia-glofas-monitor/`

### Option B: Deploy to Vercel

```bash
npm run build
vercel --prod
```

### Option C: Run Locally

```bash
# Already running! Access at http://localhost:5173/
# Press Ctrl+C to stop
# npm run dev to restart
```

## 🔄 Update Data Daily

Set up automatic updates via GitHub Actions:

1. In repository **Settings → Secrets → Add secret:**
   - Name: `EWDS_API_KEY`
   - Value: your personal access token

2. The workflow runs automatically every day at 06:17 UTC
   - Or manually: Go to **Actions → Update GloFAS Data → Run workflow**
   - New data commits to repo, site auto-updates

## 📊 Browser Features

- **Map Controls**: Zoom, pan, see point details on hover
- **Lead Time Selector**: Choose forecast day (1-30)
- **Metric Selector**: View different statistics (p50, p90, control, etc.)
- **Search**: Find points by ID or location
- **Click Points**: Opens detail modal with hydrograph chart
- **Download**: Export CSV for any point

## 🛠️ If You Want to Customize

### Change Update Schedule
Edit `.github/workflows/update-data.yml`:
```yaml
schedule:
  - cron: '17 6 * * *'  # Daily at 06:17 UTC
```
[Cron format explained](https://crontab.guru/)

### Change Monitoring Point Density
Edit `config/data.config.json`:
```json
"monitoringPoints": {
  "maxPoints": 500,  // Change from 1000
  "minDischargeThreshold": 50  // Filter small streams
}
```

### Change Indonesia Bounding Box
Edit `config/data.config.json`:
```json
"boundingBox": {
  "north": 8,
  "south": -12,
  "west": 94,
  "east": 142
}
```

### Rebuild After Config Changes
```bash
# Run pipeline
cd scripts && python update_data.py

# Rebuild site
cd ..
npm run build
```

## 📚 Full Documentation

See [README.md](./README.md) for:
- Architecture details
- Troubleshooting
- Development setup
- Complete API reference

## 🎓 How It Works (Simple Explanation)

1. **Data Pipeline (Python)**
   - Downloads GloFAS forecast from EWDS API
   - Extracts 1000 points in Indonesia
   - Computes ensemble statistics

2. **Frontend (React + TypeScript)**
   - Reads pre-computed JSON files
   - Displays on interactive map
   - No server needed!

3. **Hosting (Static)**
   - Files hosted on GitHub Pages or Vercel
   - No backend required
   - Very fast and cheap to run

---

**Questions?** See README.md or check the code in `src/` and `scripts/`
