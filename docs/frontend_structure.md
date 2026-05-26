# Frontend Structure (HTML/CSS/JS)

```
static/
  css/
    dashboard.css
  js/
    dashboard.js
templates/
  dashboard.html
```

## Dashboard Layout

1. Sidebar navigation with operational status
2. Hero panel with global risk outlook
3. Risk cards for regions
4. Map + trend chart block
5. Analytics row (feature importance, alert mix, operations)
6. Prediction form + live weather widget

## API Integration

- POST `/api/predict` expects:
  - temperature, humidity, rainfall, wind_speed, vegetation, soil_moisture
- GET `/api/weather?lat={lat}&lon={lon}`

## UI Recommendations

- Use high-contrast typography, large numeric signals
- Keep risk colors consistent (green -> amber -> red)
- Use controlled motion (subtle hover, hero attention)

## Color Palette

- Background: #0b0e11
- Panel: #12161c
- Accent 1: #f97316
- Accent 2: #fbbf24
- Accent 3: #ef4444
- Highlight: #22c55e
