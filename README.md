# Indonesia GloFAS Monitor

Interactive web dashboard for monitoring GloFAS river discharge forecasts across Indonesia. This lightweight static site displays forecast data for ~25-1000 monitoring points across Indonesia's major rivers.

![Dashboard Preview](docs/preview.png)

## What This Project Does

This project provides:

- **Interactive Map**: View river discharge monitoring points across Indonesia
- **Forecast Charts**: Hydrographs showing ensemble forecasts (P10-P90 range) with control forecast
- **Lead Time Selection**: View forecasts from 1 to 30 days ahead (24h to 720h)
- **Top Points**: Quick access to locations with highest predicted discharge
- **Data Export**: Download CSV data for any monitoring point

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions                            │
│  ┌─────────────────┐         ┌─────────────────────────┐    │
│  │ update-data.yml │────────▶│   deploy-pages.yml      │    │
│  │ (daily @ 06:17) │         │   (on data update)      │    │
│  └────────┬────────┘         └───────────┬─────────────┘    │
│           │                              │                   │
│           ▼                              ▼                   │
│  ┌─────────────────┐         ┌─────────────────────────┐    │
│  │ Python Pipeline │         │   Vite Build            │    │
│  │ - fetch_glofas  │         │   - React + TypeScript  │    │
│  │ - process_glofas│         │   - Leaflet maps        │    │
│  └────────┬────────┘         │   - Chart.js graphs     │    │
│           │                  └───────────┬─────────────┘    │
│           ▼                              │                   │
│  ┌─────────────────┐                     │                   │
│  │ public/data/    │─────────────────────┘                   │
│  │ latest/*.json   │                                         │
│  └─────────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  GitHub Pages   │
                    │  (Static Host)  │
                    └─────────────────┘
```

**Key Design Decisions:**

1. **Static Site**: No server required. The frontend reads pre-computed JSON files.
2. **Scheduled Pipeline**: GitHub Actions fetches and processes data daily.
3. **Pre-computed Statistics**: Ensemble statistics (P10, P25, P50, P75, P90) are computed during processing, not in the browser.
4. **Lightweight**: Small bundle size, fast loading, works on low-bandwidth connections.

## Prerequisites

- **Node.js** 18+ (for frontend development)
- **Python** 3.10+ (for data pipeline)
- **Git** (for version control)
- **EWDS Account** (for API access - see below)

## How to Get EWDS API Access

1. Go to [Copernicus EWDS](https://ewds.climate.copernicus.eu/)
2. Click "Register" and create an account
3. Log in and go to your profile settings
4. Find "Personal Access Token" and create a new token
5. Save this token - you'll need it as `EWDS_API_KEY`

### ⚠️ IMPORTANT: Accept Dataset Terms

**Before the data pipeline will work**, you must manually accept the dataset terms:

1. Go to the [GloFAS Forecast Dataset Page](https://ewds.climate.copernicus.eu/datasets/cems-glofas-forecast)
2. Scroll down and click "Download data"
3. Read and accept the terms and conditions
4. This is a one-time step per account

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/indonesia-glofas-monitor.git
cd indonesia-glofas-monitor
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Node.js Environment

```bash
npm install
```

### 4. Configure API Credentials

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your EWDS API key
# EWDS_API_KEY=your-personal-access-token-here
```

## How to Run the Data Update Locally

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Set your API key (or use .env file)
export EWDS_API_KEY=your-personal-access-token

# Run the full pipeline
cd scripts
python update_data.py
```

This will:
1. Find the latest available forecast date
2. Download GloFAS data for Indonesia
3. Process the data into JSON files
4. Save output to `public/data/latest/`

**Note**: The first run may take 10-30 minutes depending on data availability and network speed.

## How to Run the Website Locally

```bash
# Development mode (with hot reload)
npm run dev

# Open http://localhost:5173 in your browser
```

To preview the production build:

```bash
npm run build
npm run preview
```

## How to Deploy to GitHub Pages

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Build and deployment", select **GitHub Actions**

### Step 2: Add Repository Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add: `EWDS_API_KEY` with your personal access token

### Step 3: Push to Main Branch

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

The `deploy-pages.yml` workflow will automatically build and deploy.

### Step 4: Trigger Data Update (Optional)

To populate with real data:
1. Go to **Actions** → **Update GloFAS Data**
2. Click **Run workflow**

## How to Deploy to Vercel (Alternative)

### Option A: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Connect your GitHub repository
4. Vercel will auto-detect Vite settings
5. Click Deploy

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Build and deploy
npm run build
vercel --prod
```

**Note for Vercel**: The data pipeline runs via GitHub Actions, not on Vercel. Data is committed to the repository and deployed as static files.

## GitHub Secrets Required

| Secret Name | Description |
|-------------|-------------|
| `EWDS_API_KEY` | Your Copernicus EWDS personal access token |

## Troubleshooting

### "EWDS_API_KEY environment variable is not set"

Make sure you've either:
- Set the environment variable: `export EWDS_API_KEY=your-token`
- Or added the secret in GitHub repository settings

### "No forecast data found in the last 7 days"

This can happen if:
- Your API credentials are incorrect
- You haven't accepted the dataset terms (see above)
- There's a temporary issue with the EWDS API

### "Failed to fetch metadata" in browser

The data files are missing. Either:
- Run the data pipeline locally
- Trigger the GitHub Action manually
- The sample data should be present if you cloned fresh

### Map not showing / Leaflet errors

Make sure you have an internet connection - the map tiles load from CartoDB CDN.

### Build fails with TypeScript errors

```bash
# Check for type errors
npx tsc --noEmit

# Fix common issues
npm install
```

## How to Change the Indonesia Bounding Box

Edit `config/data.config.json`:

```json
{
  "indonesia": {
    "boundingBox": {
      "north": 8,
      "west": 94,
      "south": -12,
      "east": 142
    }
  }
}
```

Also update the polygon in `scripts/indonesia_boundary.py` if you need precise clipping.

## How to Change the Monitoring Point Density

Edit `config/data.config.json`:

```json
{
  "monitoringPoints": {
    "maxPoints": 1000,        // Increase/decrease this
    "minDischargeThreshold": 10,  // Filter out tiny streams
    "gridSpacingDegrees": 0.1     // Geographic spacing
  }
}
```

More points = larger data files = slower initial load.

## How to Change the Refresh Schedule

Edit `.github/workflows/update-data.yml`:

```yaml
schedule:
  - cron: '17 6 * * *'  # Currently: daily at 06:17 UTC
```

Cron format: `minute hour day month weekday`

Examples:
- `'17 6 * * *'` - Daily at 06:17 UTC
- `'17 */6 * * *'` - Every 6 hours at :17
- `'17 6 * * 1,4'` - Monday and Thursday at 06:17 UTC

## Project Structure

```
.
├── .github/workflows/        # GitHub Actions
│   ├── update-data.yml       # Data fetch/process pipeline
│   └── deploy-pages.yml      # Build and deploy to Pages
├── config/
│   ├── app.config.json       # Frontend configuration
│   └── data.config.json      # Data pipeline configuration
├── public/
│   └── data/latest/          # Generated data files
├── scripts/
│   ├── fetch_glofas.py       # Download GloFAS data
│   ├── process_glofas.py     # Process to JSON
│   ├── update_data.py        # Main pipeline script
│   └── indonesia_boundary.py # Indonesia polygon utilities
├── src/
│   ├── components/           # React components
│   ├── lib/                  # Utilities and types
│   ├── styles/               # CSS
│   ├── App.tsx               # Main app component
│   └── main.tsx              # Entry point
├── index.html                # HTML template
├── package.json              # Node dependencies
├── requirements.txt          # Python dependencies
├── vite.config.ts            # Vite configuration
└── README.md                 # This file
```

## Data File Format

The pipeline generates these files in `public/data/latest/`:

- `metadata.json` - Forecast run date, point count, config
- `points-index.json` - List of all monitoring points
- `values-{leadtime}.json` - Point values for each lead time
- `top-points-{leadtime}-{metric}.json` - Top N points
- `timeseries/{point-id}.json` - Full timeseries for each point

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Acknowledgments

- Data: [Copernicus Emergency Management Service - GloFAS](https://www.globalfloods.eu/)
- Maps: [OpenStreetMap](https://www.openstreetmap.org/) via [CARTO](https://carto.com/)
- Icons: Custom SVG
