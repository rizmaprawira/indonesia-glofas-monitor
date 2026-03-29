"""
GloFAS data processing script.
Converts raw NetCDF data into frontend-friendly JSON files.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import hashlib

import numpy as np
import xarray as xr

from indonesia_boundary import point_in_indonesia, get_indonesia_polygon

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

TEMP_DIR = Path(__file__).parent / "temp"
OUTPUT_DIR = Path(__file__).parent.parent / CONFIG["output"]["dataDir"]


def generate_point_id(lat: float, lon: float) -> str:
    """Generate a stable point ID based on coordinates."""
    # Round to 2 decimal places for stability
    lat_r = round(lat, 2)
    lon_r = round(lon, 2)
    # Create a short hash for the ID
    coord_str = f"{lat_r:.2f},{lon_r:.2f}"
    hash_str = hashlib.md5(coord_str.encode()).hexdigest()[:8]
    return f"P{hash_str}"


def load_netcdf_data(file_path: Path) -> xr.Dataset:
    """Load NetCDF file into xarray Dataset."""
    logger.info(f"Loading {file_path}...")
    ds = xr.open_dataset(file_path)
    return ds


def extract_monitoring_points(
    control_ds: xr.Dataset,
    ensemble_ds: Optional[xr.Dataset],
    max_points: int,
    min_discharge: float
) -> list[dict]:
    """
    Extract monitoring points from the dataset.
    Prioritizes points with higher discharge values and ensures
    good geographic coverage across Indonesia.
    """
    logger.info("Extracting monitoring points...")
    
    indonesia_poly = get_indonesia_polygon()
    
    # Get first lead time data for point selection
    var_name = "dis24"  # river discharge variable
    
    # Try to find the correct variable name
    possible_vars = ["dis24", "dis", "river_discharge_in_the_last_24_hours"]
    for v in possible_vars:
        if v in control_ds.data_vars:
            var_name = v
            break
    
    # Get coordinates
    lat_coord = "latitude" if "latitude" in control_ds.coords else "lat"
    lon_coord = "longitude" if "longitude" in control_ds.coords else "lon"
    
    lats = control_ds[lat_coord].values
    lons = control_ds[lon_coord].values
    
    # Get first timestep data
    data = control_ds[var_name].isel(forecast_period=0).values
    if len(data.shape) == 3:
        data = data[0]  # Remove forecast_reference_time dimension
    
    # Collect valid points
    valid_points = []
    
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            value = float(data[i, j]) if len(data.shape) == 2 else float(data[j])
            
            # Skip invalid values
            if np.isnan(value) or value < min_discharge:
                continue
            
            # Check if point is in Indonesia
            if not point_in_indonesia(lat, lon):
                continue
            
            valid_points.append({
                "lat": float(lat),
                "lon": float(lon),
                "lat_idx": i,
                "lon_idx": j,
                "value": value
            })
    
    logger.info(f"Found {len(valid_points)} valid points in Indonesia")
    
    if len(valid_points) <= max_points:
        selected_points = valid_points
    else:
        # Smart selection: prioritize high discharge + geographic spread
        selected_points = select_representative_points(
            valid_points,
            max_points,
            grid_size=0.5  # degrees
        )
    
    # Add stable IDs
    for p in selected_points:
        p["id"] = generate_point_id(p["lat"], p["lon"])
    
    logger.info(f"Selected {len(selected_points)} monitoring points")
    return selected_points


def select_representative_points(
    points: list[dict],
    max_points: int,
    grid_size: float
) -> list[dict]:
    """
    Select representative points ensuring geographic coverage
    while prioritizing high discharge values.
    """
    # Sort by discharge value (descending)
    sorted_points = sorted(points, key=lambda p: p["value"], reverse=True)
    
    selected = []
    used_cells = set()
    
    for p in sorted_points:
        if len(selected) >= max_points:
            break
        
        # Grid cell for geographic spacing
        cell = (
            int(p["lat"] / grid_size),
            int(p["lon"] / grid_size)
        )
        
        # Allow one point per grid cell initially
        if cell not in used_cells:
            selected.append(p)
            used_cells.add(cell)
    
    # If we still have room, add more high-value points
    for p in sorted_points:
        if len(selected) >= max_points:
            break
        if p not in selected:
            selected.append(p)
    
    return selected


def compute_statistics(
    control_ds: xr.Dataset,
    ensemble_ds: Optional[xr.Dataset],
    points: list[dict],
    lead_times: list[int]
) -> dict:
    """
    Compute statistical summaries for each point and lead time.
    """
    logger.info("Computing statistics...")
    
    var_name = "dis24"
    possible_vars = ["dis24", "dis", "river_discharge_in_the_last_24_hours"]
    for v in possible_vars:
        if v in control_ds.data_vars:
            var_name = v
            break
    
    lat_coord = "latitude" if "latitude" in control_ds.coords else "lat"
    lon_coord = "longitude" if "longitude" in control_ds.coords else "lon"
    
    result = {}
    
    for point in points:
        point_id = point["id"]
        lat_idx = point["lat_idx"]
        lon_idx = point["lon_idx"]
        
        timeseries = []
        
        for step_idx, lt in enumerate(lead_times):
            try:
                # Get control value
                control_data = control_ds[var_name].values
                if len(control_data.shape) == 4:
                    # (forecast_period, forecast_reference_time, latitude, longitude)
                    control_val = float(control_data[step_idx, 0, lat_idx, lon_idx])
                elif len(control_data.shape) == 3:
                    control_val = float(control_data[step_idx, lat_idx, lon_idx])
                else:
                    control_val = float(control_data[step_idx, lat_idx])
                
                if np.isnan(control_val):
                    control_val = None
                
                # Get ensemble statistics if available
                if ensemble_ds is not None and var_name in ensemble_ds.data_vars:
                    ens_data = ensemble_ds[var_name].values
                    # Ensemble dimension is usually 'number' or 'realization'
                    if len(ens_data.shape) == 4:
                        ens_values = ens_data[:, step_idx, lat_idx, lon_idx]
                    else:
                        ens_values = ens_data[step_idx, :, lat_idx]
                    
                    ens_values = ens_values[~np.isnan(ens_values)]
                    
                    if len(ens_values) > 0:
                        stats = {
                            "leadTime": lt,
                            "control": control_val,
                            "min": float(np.min(ens_values)),
                            "max": float(np.max(ens_values)),
                            "mean": float(np.mean(ens_values)),
                            "p10": float(np.percentile(ens_values, 10)),
                            "p25": float(np.percentile(ens_values, 25)),
                            "p50": float(np.percentile(ens_values, 50)),
                            "p75": float(np.percentile(ens_values, 75)),
                            "p90": float(np.percentile(ens_values, 90))
                        }
                    else:
                        # Fallback to control only
                        val = control_val if control_val is not None else 0
                        stats = {
                            "leadTime": lt,
                            "control": control_val,
                            "min": val, "max": val, "mean": val,
                            "p10": val, "p25": val, "p50": val,
                            "p75": val, "p90": val
                        }
                else:
                    # No ensemble data, use control only
                    val = control_val if control_val is not None else 0
                    stats = {
                        "leadTime": lt,
                        "control": control_val,
                        "min": val, "max": val, "mean": val,
                        "p10": val, "p25": val, "p50": val,
                        "p75": val, "p90": val
                    }
                
                timeseries.append(stats)
                
            except Exception as e:
                logger.warning(f"Error computing stats for {point_id} at {lt}h: {e}")
                continue
        
        result[point_id] = {
            "id": point_id,
            "lat": point["lat"],
            "lon": point["lon"],
            "timeseries": timeseries
        }
    
    return result


def generate_output_files(
    points: list[dict],
    statistics: dict,
    forecast_date: str,
    lead_times: list[int]
) -> None:
    """Generate all output JSON files for the frontend."""
    logger.info("Generating output files...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts_dir = OUTPUT_DIR / CONFIG["output"]["timeseriesDir"]
    ts_dir.mkdir(exist_ok=True)
    
    # 1. Metadata
    metadata = {
        "forecastRunDate": forecast_date,
        "pipelineTimestamp": datetime.utcnow().isoformat(),
        "dataVersion": "1.0",
        "leadTimes": lead_times,
        "metrics": ["control", "min", "max", "mean", "p10", "p25", "p50", "p75", "p90"],
        "pointCount": len(points),
        "boundingBox": CONFIG["indonesia"]["boundingBox"]
    }
    
    with open(OUTPUT_DIR / CONFIG["output"]["metadataFile"], 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Wrote {CONFIG['output']['metadataFile']}")
    
    # 2. Points index
    points_index = {
        "points": [
            {
                "id": p["id"],
                "lat": p["lat"],
                "lon": p["lon"]
            }
            for p in points
        ]
    }
    
    with open(OUTPUT_DIR / CONFIG["output"]["pointsIndexFile"], 'w') as f:
        json.dump(points_index, f)
    logger.info(f"Wrote {CONFIG['output']['pointsIndexFile']}")
    
    # 3. Individual timeseries files
    for point_id, data in statistics.items():
        ts_file = ts_dir / f"{point_id}.json"
        with open(ts_file, 'w') as f:
            json.dump(data, f)
    logger.info(f"Wrote {len(statistics)} timeseries files")
    
    # 4. Values by lead time (for map coloring)
    for lt in lead_times:
        values = {}
        for point_id, data in statistics.items():
            ts_entry = next(
                (t for t in data["timeseries"] if t["leadTime"] == lt),
                None
            )
            if ts_entry:
                values[point_id] = {
                    "control": ts_entry.get("control"),
                    "min": ts_entry["min"],
                    "max": ts_entry["max"],
                    "mean": ts_entry["mean"],
                    "p10": ts_entry["p10"],
                    "p25": ts_entry["p25"],
                    "p50": ts_entry["p50"],
                    "p75": ts_entry["p75"],
                    "p90": ts_entry["p90"]
                }
        
        with open(OUTPUT_DIR / f"values-{lt}.json", 'w') as f:
            json.dump(values, f)
    logger.info(f"Wrote {len(lead_times)} values files")
    
    # 5. Top points files
    metrics = ["control", "p50", "p90", "max"]
    for lt in lead_times:
        for metric in metrics:
            top_points = []
            for point_id, data in statistics.items():
                ts_entry = next(
                    (t for t in data["timeseries"] if t["leadTime"] == lt),
                    None
                )
                if ts_entry:
                    value = ts_entry.get(metric)
                    if value is not None:
                        top_points.append({
                            "id": point_id,
                            "lat": data["lat"],
                            "lon": data["lon"],
                            "value": value
                        })
            
            top_points.sort(key=lambda x: x["value"], reverse=True)
            top_points = top_points[:20]
            
            for i, p in enumerate(top_points):
                p["rank"] = i + 1
            
            output = {
                "leadTime": lt,
                "metric": metric,
                "points": top_points
            }
            
            with open(OUTPUT_DIR / f"top-points-{lt}-{metric}.json", 'w') as f:
                json.dump(output, f)
    
    # Also write a default top-points.json
    default_top = []
    for point_id, data in statistics.items():
        ts_entry = data["timeseries"][0] if data["timeseries"] else None
        if ts_entry:
            default_top.append({
                "id": point_id,
                "lat": data["lat"],
                "lon": data["lon"],
                "value": ts_entry["p50"]
            })
    
    default_top.sort(key=lambda x: x["value"], reverse=True)
    default_top = default_top[:20]
    for i, p in enumerate(default_top):
        p["rank"] = i + 1
    
    with open(OUTPUT_DIR / "top-points.json", 'w') as f:
        json.dump({
            "leadTime": lead_times[0],
            "metric": "p50",
            "points": default_top
        }, f)
    
    logger.info("Output generation complete")


def main():
    """Main entry point for the processing script."""
    logger.info("Starting GloFAS data processing...")
    
    # Load download info
    info_path = TEMP_DIR / "download_info.json"
    if not info_path.exists():
        raise FileNotFoundError(
            f"Download info not found at {info_path}. "
            "Run fetch_glofas.py first."
        )
    
    with open(info_path) as f:
        download_info = json.load(f)
    
    forecast_date = download_info["forecast_date"]
    files = download_info["files"]
    
    # Load datasets
    control_ds = None
    ensemble_ds = None
    
    if "control_forecast" in files:
        control_ds = load_netcdf_data(Path(files["control_forecast"]))
    
    if "ensemble_perturbed_forecasts" in files:
        ensemble_ds = load_netcdf_data(Path(files["ensemble_perturbed_forecasts"]))
    
    if control_ds is None and ensemble_ds is None:
        raise ValueError("No data files found to process")
    
    # Use control or first ensemble member as reference
    ref_ds = control_ds if control_ds else ensemble_ds
    
    # Extract monitoring points
    points = extract_monitoring_points(
        ref_ds,
        ensemble_ds,
        max_points=CONFIG["monitoringPoints"]["maxPoints"],
        min_discharge=CONFIG["monitoringPoints"]["minDischargeThreshold"]
    )
    
    if not points:
        raise ValueError("No valid monitoring points found in Indonesia")
    
    # Compute statistics
    statistics = compute_statistics(
        ref_ds,
        ensemble_ds,
        points,
        CONFIG["leadTimeHours"]
    )
    
    # Generate output files
    generate_output_files(
        points,
        statistics,
        forecast_date,
        CONFIG["leadTimeHours"]
    )
    
    # Cleanup
    if control_ds:
        control_ds.close()
    if ensemble_ds:
        ensemble_ds.close()
    
    logger.info("Processing complete!")


if __name__ == "__main__":
    import sys
    try:
        main()
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)
