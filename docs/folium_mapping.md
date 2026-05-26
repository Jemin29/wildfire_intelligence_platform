# Folium Wildfire Mapping System

## Sample Data Structure

```python
risk_points = [
    {"lat": 34.05, "lon": -118.25, "risk": 0.82},
    {"lat": 36.77, "lon": -119.41, "risk": 0.67},
]

weather_points = [
    {"lat": 34.05, "lon": -118.25, "temp": 31.2, "humidity": 18, "wind": 7.1},
]

risk_zones = [
    {
        "name": "Sierra Corridor",
        "color": "#ef4444",
        "coords": [
            [37.2, -120.6],
            [37.8, -120.6],
            [38.1, -119.7],
            [37.4, -119.5],
        ],
    }
]
```

## Visualization Techniques

- Use a heatmap for continuous risk intensity
- Overlay markers with popups for station-level metadata
- Use polygons for regional risk zones and perimeters
- Keep layers togglable via `LayerControl`
- Add a custom legend overlay for risk categories

## Integration

- Map route: `GET /map/wildfire`
- Embed in dashboard with an iframe
