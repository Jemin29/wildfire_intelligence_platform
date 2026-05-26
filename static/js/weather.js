const api = {
  weather: async (lat, lon) => {
    const response = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || "Weather fetch failed");
    }
    return response.json();
  },
  forecast: async (lat, lon) => {
    const response = await fetch(`/api/weather/forecast?lat=${lat}&lon=${lon}`);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || "Forecast fetch failed");
    }
    return response.json();
  },
};

const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: "#f7f5f2" },
    },
  },
  scales: {
    x: { ticks: { color: "#a1a8b3" }, grid: { color: "rgba(255,255,255,0.08)" } },
    y: { ticks: { color: "#a1a8b3" }, grid: { color: "rgba(255,255,255,0.08)" } },
  },
};

const elements = {
  refreshWeather: document.getElementById("refreshWeather"),
  weatherGrid: document.getElementById("weatherGrid"),
  weatherSource: document.getElementById("weatherSource"),
  forecastGrid: document.getElementById("forecastGrid"),
  weatherIndex: document.getElementById("weatherIndex"),
  weatherIndexMeta: document.getElementById("weatherIndexMeta"),
  humidityStress: document.getElementById("humidityStress"),
  humidityMeta: document.getElementById("humidityMeta"),
  windSurge: document.getElementById("windSurge"),
  windMeta: document.getElementById("windMeta"),
  droughtIndex: document.getElementById("droughtIndex"),
  droughtMeta: document.getElementById("droughtMeta"),
  locationLabel: document.getElementById("locationLabel"),
  lastUpdated: document.getElementById("lastUpdated"),
  updateStatus: document.getElementById("updateStatus"),
  locationPicker: document.getElementById("locationPicker"),
  liveWidgets: document.getElementById("liveWidgets"),
  wildfireIndicators: document.getElementById("wildfireIndicators"),
  weatherAlerts: document.getElementById("weatherAlerts"),
  updateWorkflow: document.getElementById("updateWorkflow"),
  humidityChart: document.getElementById("humidityChart"),
  windChart: document.getElementById("windChart"),
  rainChart: document.getElementById("rainChart"),
  droughtChart: document.getElementById("droughtChart"),
  riskFactorChart: document.getElementById("riskFactorChart"),
};

const charts = {};

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const formatTime = (date) =>
  date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const setStatus = (text, variant) => {
  if (!elements.updateStatus) {
    return;
  }
  elements.updateStatus.textContent = text;
  elements.updateStatus.classList.toggle("error", variant === "error");
};

const parseLocation = (rawValue) => {
  const parts = rawValue.split(",");
  return {
    lat: Number(parts[0]),
    lon: Number(parts[1]),
    label: parts.slice(2).join(",").trim(),
  };
};

const defaultLocation = { lat: 34.05, lon: -118.25, label: "Los Angeles, CA" };
let activeLocation = { ...defaultLocation };

const computeWeatherIndex = (temp, humidity, wind, rain) => {
  if (!Number.isFinite(temp) || !Number.isFinite(humidity) || !Number.isFinite(wind)) {
    return null;
  }
  const moisturePenalty = clamp(100 - humidity, 0, 100);
  const windBoost = clamp(wind * 8, 0, 40);
  const rainRelief = clamp((rain || 0) * 6, 0, 25);
  return Math.round(clamp(temp * 1.1 + moisturePenalty * 0.6 + windBoost - rainRelief, 0, 100));
};

const computeDroughtIndex = (humidity, rain, temp) => {
  if (!Number.isFinite(humidity)) {
    return null;
  }
  const dryness = clamp(100 - humidity, 0, 100);
  const rainfallOffset = clamp((rain || 0) * 8, 0, 30);
  const heatBoost = Number.isFinite(temp) ? clamp(temp - 18, 0, 25) : 0;
  return Math.round(clamp(dryness + heatBoost - rainfallOffset, 0, 100));
};

const renderWeatherGrid = (metrics) => {
  if (!elements.weatherGrid) {
    return;
  }
  const values = [
    `${metrics.temp ?? "--"} C`,
    `${metrics.humidity ?? "--"}%`,
    `${metrics.wind ?? "--"} m/s`,
    `${metrics.rain ?? 0} mm`,
  ];
  elements.weatherGrid.querySelectorAll("strong").forEach((node, index) => {
    node.textContent = values[index];
  });
};

const renderWidgets = (metrics) => {
  if (!elements.liveWidgets) {
    return;
  }
  const widgets = [
    { label: "Feels like", value: `${metrics.feelsLike ?? "--"} C` },
    { label: "Pressure", value: `${metrics.pressure ?? "--"} hPa` },
    { label: "Visibility", value: `${metrics.visibility ?? "--"} km` },
    { label: "Cloud cover", value: `${metrics.clouds ?? "--"}%` },
    { label: "Wind direction", value: `${metrics.windDirection ?? "--"}` },
    { label: "Dew point", value: metrics.dewPoint ?? "--" },
  ];
  elements.liveWidgets.innerHTML = widgets
    .map(
      (widget) => `
        <div class="widget-card">
          <span class="muted">${widget.label}</span>
          <strong>${widget.value}</strong>
        </div>
      `
    )
    .join("");
};

const renderIndicators = (indicators) => {
  if (!elements.wildfireIndicators) {
    return;
  }
  elements.wildfireIndicators.innerHTML = indicators
    .map(
      (indicator) => `
        <div class="indicator-item">
          <div class="indicator-row">
            <strong>${indicator.label}</strong>
            <span class="indicator-pill">${indicator.status}</span>
          </div>
          <div class="indicator-score">${indicator.value}</div>
          <span class="muted">${indicator.detail}</span>
        </div>
      `
    )
    .join("");
};

const renderAlerts = (alerts) => {
  if (!elements.weatherAlerts) {
    return;
  }
  if (!alerts.length) {
    elements.weatherAlerts.innerHTML = `
      <div class="alert-item">
        <strong>No active weather alerts</strong>
        <div class="alert-meta">
          <span>Monitoring thresholds</span>
          <span>All clear</span>
        </div>
      </div>
    `;
    return;
  }
  elements.weatherAlerts.innerHTML = alerts
    .map(
      (alert) => `
        <div class="alert-item">
          <strong>${alert.title}</strong>
          <div class="alert-meta">
            <span>${alert.region}</span>
            <span>${alert.severity}</span>
          </div>
        </div>
      `
    )
    .join("");
};

const renderWorkflow = () => {
  if (!elements.updateWorkflow) {
    return;
  }
  const steps = [
    {
      title: "Ingest live weather API",
      detail: "Pulls current observations every 5 minutes.",
    },
    {
      title: "Normalize and enrich",
      detail: "Derives wildfire indices and drought risk.",
    },
    {
      title: "Trigger alert thresholds",
      detail: "Evaluates humidity, wind, and rainfall risks.",
    },
    {
      title: "Publish to live widgets",
      detail: "Broadcasts updates to field dashboards.",
    },
  ];
  elements.updateWorkflow.innerHTML = steps
    .map(
      (step) => `
        <div class="workflow-step">
          <strong>${step.title}</strong>
          <span class="muted">${step.detail}</span>
        </div>
      `
    )
    .join("");
};

const buildDailyForecast = (list) => {
  const daily = {};
  list.forEach((entry) => {
    const dateKey = entry?.dt_txt?.split(" ")[0];
    if (!dateKey) {
      return;
    }
    if (!daily[dateKey]) {
      daily[dateKey] = {
        date: dateKey,
        temp: 0,
        humidity: 0,
        wind: 0,
        rain: 0,
        count: 0,
      };
    }
    const rain = entry?.rain?.["3h"] ?? 0;
    daily[dateKey].temp += entry?.main?.temp ?? 0;
    daily[dateKey].humidity += entry?.main?.humidity ?? 0;
    daily[dateKey].wind += entry?.wind?.speed ?? 0;
    daily[dateKey].rain += rain;
    daily[dateKey].count += 1;
  });
  return Object.values(daily)
    .map((day) => ({
      date: day.date,
      temp: day.count ? day.temp / day.count : 0,
      humidity: day.count ? day.humidity / day.count : 0,
      wind: day.count ? day.wind / day.count : 0,
      rain: day.rain,
    }))
    .slice(0, 7);
};

const updateForecast = (daily) => {
  if (!elements.forecastGrid) {
    return;
  }
  elements.forecastGrid.innerHTML = daily
    .map((day, index) => {
      const date = new Date(day.date);
      const label = date.toLocaleDateString([], { weekday: "short" });
      return `
        <div class="forecast-card">
          <strong>${label} · Day ${index + 1}</strong>
          <div class="forecast-row"><span>Temp</span><span>${Math.round(day.temp)} C</span></div>
          <div class="forecast-row"><span>Humidity</span><span>${Math.round(day.humidity)}%</span></div>
          <div class="forecast-row"><span>Wind</span><span>${Math.round(day.wind)} m/s</span></div>
        </div>
      `;
    })
    .join("");
};

const createOrUpdateChart = (key, canvas, config) => {
  if (typeof Chart === "undefined" || !config || !canvas) {
    return;
  }
  if (charts[key]) {
    charts[key].data = config.data;
    charts[key].options = config.options;
    charts[key].update();
    return;
  }
  charts[key] = new Chart(canvas, config);
};

const updateCharts = (daily, riskFactors) => {
  if (elements.humidityChart) {
    createOrUpdateChart("humidity", elements.humidityChart, {
      type: "line",
      data: {
        labels: daily.map((day) => new Date(day.date).toLocaleDateString([], { weekday: "short" })),
        datasets: [
          {
            label: "Humidity",
            data: daily.map((day) => Math.round(day.humidity)),
            borderColor: "#38bdf8",
            backgroundColor: "rgba(56, 189, 248, 0.2)",
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: chartDefaults,
    });
  }

  if (elements.windChart) {
    createOrUpdateChart("wind", elements.windChart, {
      type: "line",
      data: {
        labels: daily.map((day) => new Date(day.date).toLocaleDateString([], { weekday: "short" })),
        datasets: [
          {
            label: "Wind speed",
            data: daily.map((day) => Math.round(day.wind)),
            borderColor: "#f97316",
            backgroundColor: "rgba(249, 115, 22, 0.2)",
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: chartDefaults,
    });
  }

  if (elements.rainChart) {
    createOrUpdateChart("rain", elements.rainChart, {
      type: "bar",
      data: {
        labels: daily.map((day) => new Date(day.date).toLocaleDateString([], { weekday: "short" })),
        datasets: [
          {
            label: "Rainfall (mm)",
            data: daily.map((day) => Math.round(day.rain)),
            backgroundColor: "rgba(148, 163, 184, 0.6)",
          },
        ],
      },
      options: chartDefaults,
    });
  }

  if (elements.droughtChart) {
    createOrUpdateChart("drought", elements.droughtChart, {
      type: "line",
      data: {
        labels: daily.map((day) => new Date(day.date).toLocaleDateString([], { weekday: "short" })),
        datasets: [
          {
            label: "Drought index",
            data: daily.map((day) => Math.round(100 - Math.min(day.humidity, 100) + day.temp * 0.4)),
            borderColor: "#ef4444",
            backgroundColor: "rgba(239, 68, 68, 0.18)",
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: chartDefaults,
    });
  }

  if (elements.riskFactorChart) {
    createOrUpdateChart("riskFactors", elements.riskFactorChart, {
      type: "radar",
      data: {
        labels: ["Heat", "Dryness", "Wind", "Rain deficit", "Pressure"],
        datasets: [
          {
            label: "Risk drivers",
            data: riskFactors,
            backgroundColor: "rgba(56, 189, 248, 0.2)",
            borderColor: "#38bdf8",
          },
        ],
      },
      options: {
        ...chartDefaults,
        scales: {},
      },
    });
  }
};

const buildAlerts = (metrics, wildfireIndex) => {
  const alerts = [];
  if (Number.isFinite(metrics.humidity) && metrics.humidity < 20) {
    alerts.push({
      title: "Critical humidity drop",
      region: activeLocation.label,
      severity: "Critical",
    });
  }
  if (Number.isFinite(metrics.wind) && metrics.wind > 10) {
    alerts.push({
      title: "Wind surge advisory",
      region: activeLocation.label,
      severity: "High",
    });
  }
  if (Number.isFinite(metrics.temp) && metrics.temp > 32) {
    alerts.push({
      title: "Extreme heat potential",
      region: activeLocation.label,
      severity: "High",
    });
  }
  if (Number.isFinite(metrics.rain) && metrics.rain < 1) {
    alerts.push({
      title: "Minimal rainfall expected",
      region: activeLocation.label,
      severity: "Moderate",
    });
  }
  if (Number.isFinite(wildfireIndex) && wildfireIndex > 80) {
    alerts.push({
      title: "Wildfire weather index elevated",
      region: activeLocation.label,
      severity: "Critical",
    });
  }
  return alerts.slice(0, 4);
};

const updateFromWeather = (current, forecast) => {
  const temp = Number(current?.data?.main?.temp ?? NaN);
  const humidity = Number(current?.data?.main?.humidity ?? NaN);
  const wind = Number(current?.data?.wind?.speed ?? NaN);
  const rain = Number(current?.data?.rain?.["1h"] ?? 0);
  const feelsLike = Number(current?.data?.main?.feels_like ?? NaN);
  const pressure = Number(current?.data?.main?.pressure ?? NaN);
  const visibility = Number(current?.data?.visibility ?? NaN);
  const clouds = Number(current?.data?.clouds?.all ?? NaN);
  const windDeg = Number(current?.data?.wind?.deg ?? NaN);

  const metrics = {
    temp: Number.isFinite(temp) ? Math.round(temp) : "--",
    humidity: Number.isFinite(humidity) ? Math.round(humidity) : "--",
    wind: Number.isFinite(wind) ? wind.toFixed(1) : "--",
    rain: Number.isFinite(rain) ? rain.toFixed(1) : 0,
    feelsLike: Number.isFinite(feelsLike) ? Math.round(feelsLike) : "--",
    pressure: Number.isFinite(pressure) ? Math.round(pressure) : "--",
    visibility: Number.isFinite(visibility) ? (visibility / 1000).toFixed(1) : "--",
    clouds: Number.isFinite(clouds) ? Math.round(clouds) : "--",
    windDirection: Number.isFinite(windDeg) ? `${Math.round(windDeg)} deg` : "--",
    dewPoint: Number.isFinite(temp) && Number.isFinite(humidity)
      ? `${Math.round(temp - ((100 - humidity) / 5))} C`
      : "--",
  };

  renderWeatherGrid(metrics);
  renderWidgets(metrics);

  if (elements.weatherSource) {
    elements.weatherSource.textContent = current?.source || "Weather API";
  }

  const wildfireIndex = computeWeatherIndex(temp, humidity, wind, rain);
  const droughtIndex = computeDroughtIndex(humidity, rain, temp);

  if (elements.weatherIndex) {
    elements.weatherIndex.textContent = wildfireIndex ?? "--";
  }
  if (elements.weatherIndexMeta && wildfireIndex !== null) {
    elements.weatherIndexMeta.textContent = wildfireIndex > 75 ? "Elevated ignition risk" : "Stable conditions";
  }
  if (elements.humidityStress) {
    elements.humidityStress.textContent = metrics.humidity === "--" ? "--" : `${metrics.humidity}%`;
  }
  if (elements.humidityMeta) {
    elements.humidityMeta.textContent = metrics.humidity !== "--" && metrics.humidity < 25
      ? "Below safe range"
      : "Moisture within band";
  }
  if (elements.windSurge) {
    elements.windSurge.textContent = metrics.wind === "--" ? "--" : `${metrics.wind} m/s`;
  }
  if (elements.windMeta) {
    elements.windMeta.textContent = metrics.wind !== "--" && Number(metrics.wind) > 10
      ? "Gusts trending upward"
      : "Wind profile stable";
  }
  if (elements.droughtIndex) {
    elements.droughtIndex.textContent = droughtIndex ?? "--";
  }
  if (elements.droughtMeta) {
    elements.droughtMeta.textContent = droughtIndex !== null && droughtIndex > 70
      ? "High drought stress"
      : "Moderate dryness";
  }

  const indicators = [
    {
      label: "Ignition probability",
      status: wildfireIndex !== null && wildfireIndex > 75 ? "Critical" : "Moderate",
      value: wildfireIndex !== null ? `${wildfireIndex}%` : "--",
      detail: "Composite temperature, humidity, and wind index.",
    },
    {
      label: "Fuel moisture",
      status: Number.isFinite(humidity) && humidity < 25 ? "Low" : "Stable",
      value: Number.isFinite(humidity) ? `${humidity}%` : "--",
      detail: "Lower values indicate higher ignition risk.",
    },
    {
      label: "Suppression outlook",
      status: Number.isFinite(wind) && wind > 9 ? "Challenging" : "Manageable",
      value: Number.isFinite(wind) ? `${wind.toFixed(1)} m/s` : "--",
      detail: "Wind drives rapid spread potential.",
    },
  ];
  renderIndicators(indicators);

  const daily = buildDailyForecast(forecast?.data?.list ?? []);
  updateForecast(daily);

  const riskFactors = [
    clamp(Number.isFinite(temp) ? temp * 2.2 : 0, 0, 100),
    clamp(Number.isFinite(humidity) ? 100 - humidity : 0, 0, 100),
    clamp(Number.isFinite(wind) ? wind * 8 : 0, 0, 100),
    clamp(Number.isFinite(rain) ? 100 - rain * 8 : 70, 0, 100),
    clamp(Number.isFinite(pressure) ? Math.abs(pressure - 1013) * 3 : 20, 0, 100),
  ];

  updateCharts(daily, riskFactors);
  renderAlerts(buildAlerts({ temp, humidity, wind, rain }, wildfireIndex));
};

const refreshWeather = async () => {
  if (!elements.refreshWeather) {
    return;
  }
  elements.refreshWeather.disabled = true;
  elements.refreshWeather.textContent = "Loading...";
  setStatus("Syncing", "live");

  try {
    const current = await api.weather(activeLocation.lat, activeLocation.lon);
    const forecast = await api.forecast(activeLocation.lat, activeLocation.lon);
    updateFromWeather(current, forecast);

    if (elements.lastUpdated) {
      elements.lastUpdated.textContent = `Last updated ${formatTime(new Date())}`;
    }
    if (elements.locationLabel) {
      elements.locationLabel.textContent = activeLocation.label;
    }
    setStatus("Live", "live");
  } catch (error) {
    if (elements.weatherSource) {
      elements.weatherSource.textContent = error.message;
    }
    setStatus("Offline", "error");
  } finally {
    elements.refreshWeather.disabled = false;
    elements.refreshWeather.textContent = "Refresh";
  }
};

const initLocationPicker = () => {
  if (!elements.locationPicker) {
    return;
  }
  const chips = elements.locationPicker.querySelectorAll("[data-weather-location]");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      activeLocation = parseLocation(chip.dataset.weatherLocation);
      refreshWeather();
    });
  });
};

if (elements.refreshWeather) {
  elements.refreshWeather.addEventListener("click", refreshWeather);
}

initLocationPicker();
renderWorkflow();
refreshWeather();
setInterval(refreshWeather, 5 * 60 * 1000);
