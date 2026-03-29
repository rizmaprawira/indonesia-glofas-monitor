"""
Indonesia boundary utilities for GloFAS data processing.
Uses a simplified polygon that covers Indonesia's main territory.
"""

from shapely.geometry import Polygon, Point, box
import json
from pathlib import Path

# Simplified Indonesia boundary polygon
# This is a rough outline that covers the main Indonesian archipelago
# For production use, you might want to use official boundaries from Natural Earth
INDONESIA_POLYGON_COORDS = [
    (95.0, 6.0),    # Aceh
    (98.0, 4.0),
    (100.0, 2.0),
    (104.0, 1.5),
    (105.0, -2.0),
    (106.0, -6.0),
    (105.5, -7.0),
    (106.0, -7.5),
    (108.0, -7.8),
    (110.0, -8.0),
    (114.0, -8.5),
    (116.0, -8.8),
    (117.0, -9.0),
    (119.0, -10.5),
    (121.0, -10.5),
    (123.0, -11.0),
    (127.0, -8.5),
    (131.0, -8.0),
    (134.0, -6.0),
    (137.0, -5.0),
    (140.0, -3.0),
    (141.0, -2.5),
    (141.0, -1.0),
    (140.5, 0.0),
    (131.0, 0.5),
    (128.0, 1.0),
    (127.0, 2.5),
    (125.0, 3.5),
    (123.0, 1.0),
    (121.0, 1.0),
    (120.0, 0.0),
    (119.5, -1.0),
    (119.0, -2.0),
    (117.5, -4.0),
    (116.0, -3.5),
    (115.0, -3.0),
    (114.5, -3.5),
    (113.0, -2.5),
    (111.0, -1.0),
    (109.0, 0.0),
    (108.0, 1.0),
    (106.0, 2.0),
    (104.0, 1.0),
    (103.0, 1.5),
    (100.0, 3.0),
    (97.0, 5.5),
    (95.0, 6.0),
]

def get_indonesia_polygon() -> Polygon:
    """Returns a Shapely Polygon representing Indonesia's boundary."""
    return Polygon(INDONESIA_POLYGON_COORDS)

def get_indonesia_bbox() -> dict:
    """Returns Indonesia's bounding box as a dictionary."""
    return {
        "north": 8,
        "south": -12,
        "west": 94,
        "east": 142
    }

def point_in_indonesia(lat: float, lon: float) -> bool:
    """Check if a point is within Indonesia's boundary."""
    polygon = get_indonesia_polygon()
    point = Point(lon, lat)
    return polygon.contains(point)

def filter_points_to_indonesia(points: list[dict]) -> list[dict]:
    """Filter a list of points to only those within Indonesia."""
    polygon = get_indonesia_polygon()
    return [
        p for p in points
        if polygon.contains(Point(p['lon'], p['lat']))
    ]

def get_indonesia_geojson() -> dict:
    """Returns Indonesia boundary as GeoJSON for frontend use."""
    polygon = get_indonesia_polygon()
    return {
        "type": "Feature",
        "properties": {
            "name": "Indonesia",
            "country_code": "IDN"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [INDONESIA_POLYGON_COORDS]
        }
    }

def save_indonesia_geojson(output_path: str | Path) -> None:
    """Save Indonesia boundary GeoJSON to a file."""
    geojson = {
        "type": "FeatureCollection",
        "features": [get_indonesia_geojson()]
    }
    with open(output_path, 'w') as f:
        json.dump(geojson, f)

if __name__ == "__main__":
    # Test the functions
    print("Indonesia bounding box:", get_indonesia_bbox())
    print("Jakarta in Indonesia:", point_in_indonesia(-6.2, 106.8))
    print("Singapore in Indonesia:", point_in_indonesia(1.3, 103.8))
