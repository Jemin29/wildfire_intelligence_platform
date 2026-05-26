# Optional React Version (High-Level Stub)

Use this if you want to upgrade to React later. Keep the same API endpoints.

## Structure

```
frontend/
  src/
    components/
      Sidebar.tsx
      RiskCards.tsx
      RiskMap.tsx
      Charts.tsx
      PredictionForm.tsx
      WeatherWidget.tsx
    pages/
      Dashboard.tsx
    styles/
      theme.css
    api/
      client.ts
```

## Notes

- Use `Leaflet` and `react-leaflet` for the map.
- Use `Chart.js` with `react-chartjs-2` for charts.
- Create a single API client with `fetch` or `axios`.
- Keep theme variables in a CSS file so the color palette matches the HTML version.
