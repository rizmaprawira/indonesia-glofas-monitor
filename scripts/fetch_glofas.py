"""
GloFAS data fetching script for Indonesia river discharge forecasts.
Uses the Copernicus EWDS (Early Warning Data Store) API.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_PATH = Path(__file__).parent.parent / "config" / "data.config.json"
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

# Output directory for downloaded files
TEMP_DIR = Path(__file__).parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)


def get_api_credentials() -> tuple[str, str]:
    """Get EWDS API credentials from environment variables."""
    url = os.environ.get("EWDS_API_URL", "https://ewds.climate.copernicus.eu/api")
    key = os.environ.get("EWDS_API_KEY")
    
    if not key:
        raise ValueError(
            "EWDS_API_KEY environment variable is not set. "
            "Please set it with your personal access token from "
            "https://ewds.climate.copernicus.eu/"
        )
    
    return url, key


def setup_cdsapi_config(url: str, key: str) -> Path:
    """Create a temporary .cdsapirc file for the API client."""
    config_content = f"url: {url}\nkey: {key}\n"
    config_path = Path.home() / ".cdsapirc"
    
    # Backup existing config if present
    backup_path = None
    if config_path.exists():
        backup_path = config_path.with_suffix(".cdsapirc.backup")
        config_path.rename(backup_path)
        logger.info(f"Backed up existing .cdsapirc to {backup_path}")
    
    config_path.write_text(config_content)
    logger.info(f"Created temporary .cdsapirc at {config_path}")
    
    return backup_path


def restore_cdsapi_config(backup_path: Optional[Path]) -> None:
    """Restore the original .cdsapirc file if it existed."""
    config_path = Path.home() / ".cdsapirc"
    
    if backup_path and backup_path.exists():
        config_path.unlink(missing_ok=True)
        backup_path.rename(config_path)
        logger.info("Restored original .cdsapirc")
    elif config_path.exists():
        config_path.unlink()
        logger.info("Removed temporary .cdsapirc")


def find_latest_forecast_date(max_lookback_days: int = 7) -> str:
    """
    Find the latest available forecast date by trying recent dates.
    GloFAS forecasts are typically available with a 1-2 day delay.
    """
    import cdsapi
    
    client = cdsapi.Client(quiet=True)
    
    for days_back in range(max_lookback_days):
        test_date = datetime.utcnow() - timedelta(days=days_back)
        date_str = test_date.strftime("%Y-%m-%d")
        
        logger.info(f"Checking availability for {date_str}...")
        
        # Try a minimal request to check availability
        try:
            # Create a test request with minimal data
            request = {
                "system_version": "operational",
                "hydrological_model": "lisflood",
                "product_type": "control_forecast",
                "variable": "river_discharge_in_the_last_24_hours",
                "year": str(test_date.year),
                "month": f"{test_date.month:02d}",
                "day": f"{test_date.day:02d}",
                "leadtime_hour": "24",
                "area": [
                    CONFIG["indonesia"]["boundingBox"]["north"],
                    CONFIG["indonesia"]["boundingBox"]["west"],
                    CONFIG["indonesia"]["boundingBox"]["south"],
                    CONFIG["indonesia"]["boundingBox"]["east"]
                ],
                "data_format": "netcdf"
            }
            
            # Use a dry run to check availability without downloading
            test_file = TEMP_DIR / f"test_{date_str}.nc"
            client.retrieve(
                CONFIG["dataset"],
                request,
                str(test_file)
            )
            
            # If we get here, the date is available
            if test_file.exists():
                test_file.unlink()
            
            logger.info(f"Found available forecast date: {date_str}")
            return date_str
            
        except Exception as e:
            logger.debug(f"Date {date_str} not available: {e}")
            continue
    
    raise RuntimeError(
        f"No forecast data found in the last {max_lookback_days} days. "
        "Check your API credentials and data availability."
    )


def download_glofas_data(
    forecast_date: str,
    product_types: list[str],
    lead_times: list[int],
    output_dir: Path
) -> dict[str, Path]:
    """
    Download GloFAS forecast data for Indonesia.
    
    Args:
        forecast_date: Date string in YYYY-MM-DD format
        product_types: List of product types (control_forecast, ensemble_perturbed_forecasts)
        lead_times: List of lead time hours
        output_dir: Directory to save downloaded files
    
    Returns:
        Dictionary mapping product type to downloaded file path
    """
    import cdsapi
    
    client = cdsapi.Client()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date = datetime.strptime(forecast_date, "%Y-%m-%d")
    bbox = CONFIG["indonesia"]["boundingBox"]
    
    downloaded_files = {}
    
    for product_type in product_types:
        logger.info(f"Downloading {product_type} for {forecast_date}...")
        
        output_file = output_dir / f"glofas_{product_type}_{forecast_date}.nc"
        
        if output_file.exists():
            logger.info(f"File already exists: {output_file}")
            downloaded_files[product_type] = output_file
            continue
        
        request = {
            "system_version": "operational",
            "hydrological_model": "lisflood",
            "product_type": product_type,
            "variable": "river_discharge_in_the_last_24_hours",
            "year": str(date.year),
            "month": f"{date.month:02d}",
            "day": f"{date.day:02d}",
            "leadtime_hour": [str(lt) for lt in lead_times],
            "area": [bbox["north"], bbox["west"], bbox["south"], bbox["east"]],
            "data_format": "netcdf"
        }
        
        try:
            client.retrieve(
                CONFIG["dataset"],
                request,
                str(output_file)
            )
            logger.info(f"Downloaded: {output_file}")
            downloaded_files[product_type] = output_file
            
        except Exception as e:
            logger.error(f"Failed to download {product_type}: {e}")
            raise
        
        # Small delay between requests to be polite to the API
        time.sleep(2)
    
    return downloaded_files


def main():
    """Main entry point for the fetch script."""
    logger.info("Starting GloFAS data fetch...")
    
    # Get API credentials
    url, key = get_api_credentials()
    backup_path = setup_cdsapi_config(url, key)
    
    try:
        # Find latest available date
        lookback = CONFIG["api"]["maxRetries"] + 4
        forecast_date = find_latest_forecast_date(lookback)
        
        # Download data
        product_types = CONFIG["productType"]
        lead_times = CONFIG["leadTimeHours"]
        
        downloaded_files = download_glofas_data(
            forecast_date,
            product_types,
            lead_times,
            TEMP_DIR
        )
        
        # Save download info for the processing step
        info = {
            "forecast_date": forecast_date,
            "download_timestamp": datetime.utcnow().isoformat(),
            "files": {k: str(v) for k, v in downloaded_files.items()}
        }
        
        info_path = TEMP_DIR / "download_info.json"
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"Download complete. Info saved to {info_path}")
        return downloaded_files
        
    finally:
        restore_cdsapi_config(backup_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        sys.exit(1)
