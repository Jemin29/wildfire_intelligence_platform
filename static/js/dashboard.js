const api = {
  predict: async (payload) => {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || "Prediction failed");
    }
    return response.json();
  },
  weather: async (lat, lon) => {
    const response = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || "Weather fetch failed");
    }
    return response.json();
  },
  weatherForecast: async (lat, lon) => {
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

const riskTrendCanvas = document.getElementById("riskTrendChart");
if (riskTrendCanvas) {
  new Chart(riskTrendCanvas, {
    type: "line",
    data: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      datasets: [
        {
          label: "Forecast",
          data: [62, 64, 66, 70, 74, 78, 82],
          borderColor: "#f97316",
          backgroundColor: "rgba(249, 115, 22, 0.2)",
          tension: 0.4,
          fill: true,
        },
        {
          label: "Historical",
          data: [55, 57, 58, 60, 61, 63, 64],
          borderColor: "#fbbf24",
          tension: 0.4,
        },
      ],
    },
    options: chartDefaults,
  });
}

const featureCanvas = document.getElementById("featureChart");
if (featureCanvas) {
  new Chart(featureCanvas, {
    type: "bar",
    data: {
      labels: ["Humidity", "Temp", "Wind", "Vegetation", "Soil", "Rain"],
      datasets: [
        {
          label: "Importance",
          data: [0.32, 0.27, 0.18, 0.12, 0.07, 0.04],
          backgroundColor: [
            "#ef4444",
            "#f97316",
            "#fbbf24",
            "#22c55e",
            "#38bdf8",
            "#a855f7",
          ],
        },
      ],
    },
    options: chartDefaults,
  });
}

const alertCanvas = document.getElementById("alertChart");
if (alertCanvas) {
  new Chart(alertCanvas, {
    type: "doughnut",
    data: {
      labels: ["Critical", "High", "Moderate", "Low"],
      datasets: [
        {
          data: [18, 26, 34, 22],
          backgroundColor: ["#ef4444", "#f97316", "#fbbf24", "#22c55e"],
        },
      ],
    },
    options: {
      ...chartDefaults,
      scales: {},
    },
  });
}

const predictionForm = document.getElementById("predictionForm");
const predictionResult = document.getElementById("predictionResult");
const predictionMeta = document.getElementById("predictionMeta");
const predictionLabel = document.getElementById("predictionLabel");
const probabilityValue = document.getElementById("probabilityValue");
const probabilityGauge = document.getElementById("probabilityGauge");
const confidenceValue = document.getElementById("confidenceValue");
const confidenceGauge = document.getElementById("confidenceGauge");

if (predictionForm && predictionResult && predictionMeta) {
  predictionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(predictionForm);
    const payload = Object.fromEntries(formData.entries());
    Object.keys(payload).forEach((key) => {
      if (key !== "region" && key !== "scenario" && key !== "notes") {
        payload[key] = Number(payload[key]);
      }
    });

    predictionResult.classList.add("loading");
    predictionMeta.textContent = "Running model...";

    try {
      const response = await api.predict(payload);
      const score = response.probability ?? 0.0;
      const probability = `${Math.round(score * 100)}% risk`;
      const confidence = `${Math.round((score * 0.85 + 0.1) * 100)}%`; // placeholder
      const label = response.prediction === 1 ? "High Risk" : "Low Risk";

      predictionResult.querySelector(".result-value").textContent = label;
      predictionMeta.textContent = probability;
      if (predictionLabel) {
        predictionLabel.textContent = label;
      }
      if (probabilityValue && probabilityGauge) {
        probabilityValue.textContent = probability;
        probabilityGauge.style.width = `${Math.round(score * 100)}%`;
      }
      if (confidenceValue && confidenceGauge) {
        confidenceValue.textContent = confidence;
        confidenceGauge.style.width = `${Math.round((score * 0.85 + 0.1) * 100)}%`;
      }
    } catch (error) {
      predictionResult.querySelector(".result-value").textContent = "Error";
      predictionMeta.textContent = error.message;
    } finally {
      predictionResult.classList.remove("loading");
    }
  });
}

const riskCards = document.getElementById("riskCards");
if (riskCards) {
  const zones = [
    { name: "Sierra Corridor", score: 0.86, status: "Critical", trend: "+12%" },
    { name: "Central Basin", score: 0.72, status: "High", trend: "+6%" },
    { name: "Coastal Ridge", score: 0.58, status: "Moderate", trend: "-2%" },
    { name: "Desert Edge", score: 0.63, status: "High", trend: "+4%" },
  ];

  riskCards.innerHTML = zones
    .map(
      (zone) => `
        <div class="risk-tile">
          <div class="risk-tile-header">
            <strong>${zone.name}</strong>
            <span class="risk-indicator ${zone.status.toLowerCase()}">${zone.status}</span>
          </div>
          <div class="risk-tile-score">${Math.round(zone.score * 100)}</div>
          <div class="muted">AI risk score · ${zone.trend}</div>
          <div class="risk-bar"><span style="width: ${Math.round(zone.score * 100)}%"></span></div>
        </div>
      `
    )
    .join("");
}

const priorityZones = document.getElementById("priorityZones");
if (priorityZones) {
  const priorities = [
    { label: "Sierra Corridor", status: "Critical" },
    { label: "Central Basin", status: "High" },
    { label: "Coastal Ridge", status: "Moderate" },
  ];
  priorityZones.innerHTML = priorities
    .map(
      (item) => `
        <div class="status-item">
          <span>${item.label}</span>
          <strong>${item.status}</strong>
        </div>
      `
    )
    .join("");
}

const alertList = document.getElementById("alertList");
if (alertList) {
  const alerts = [
    { title: "Rapid wind escalation", region: "Sierra Corridor", time: "2m ago" },
    { title: "Dry fuel anomaly", region: "Central Basin", time: "15m ago" },
    { title: "Humidity drop", region: "Coastal Ridge", time: "38m ago" },
  ];
  alertList.innerHTML = alerts
    .map(
      (alert) => `
        <div class="alert-item">
          <strong>${alert.title}</strong>
          <div class="alert-meta">
            <span>${alert.region}</span>
            <span>${alert.time}</span>
          </div>
        </div>
      `
    )
    .join("");
}

const incidentList = document.getElementById("incidentList");
if (incidentList) {
  const incidents = [
    { name: "Pine Valley Fire", status: "Active", size: "1,420 ha" },
    { name: "Cedar Ridge Fire", status: "Contained", size: "320 ha" },
    { name: "Lagoon Flats", status: "Escalating", size: "640 ha" },
  ];
  incidentList.innerHTML = incidents
    .map(
      (incident) => `
        <div class="incident-item">
          <strong>${incident.name}</strong>
          <div class="incident-meta">
            <span>${incident.status}</span>
            <span>${incident.size}</span>
          </div>
        </div>
      `
    )
    .join("");
}

const opsMetrics = document.getElementById("opsMetrics");
if (opsMetrics) {
  const metrics = [
    { label: "Deployable units", value: "42" },
    { label: "Response ETA", value: "18 min" },
    { label: "Sensor uptime", value: "99%" },
    { label: "Drone coverage", value: "92%" },
  ];
  opsMetrics.innerHTML = metrics
    .map(
      (metric) => `
        <div class="metric-card">
          <span class="muted">${metric.label}</span>
          <div class="metric-value">${metric.value}</div>
        </div>
      `
    )
    .join("");
}

const statusTimeline = document.getElementById("statusTimeline");
if (statusTimeline) {
  const timeline = [
    { time: "02:10 UTC", event: "Wind shift detected - northbound spread" },
    { time: "01:42 UTC", event: "AI risk score crossed 0.8 threshold" },
    { time: "00:58 UTC", event: "Resources redeployed to Sierra Corridor" },
  ];
  statusTimeline.innerHTML = timeline
    .map(
      (item) => `
        <div class="timeline-item">
          <strong>${item.time}</strong>
          <span class="muted">${item.event}</span>
        </div>
      `
    )
    .join("");
}

const heatIndicators = document.getElementById("heatIndicators");
if (heatIndicators) {
  const heat = [
    { zone: "Sector A-1", level: "92" },
    { zone: "Sector B-4", level: "78" },
    { zone: "Sector C-2", level: "66" },
    { zone: "Sector D-5", level: "54" },
  ];
  heatIndicators.innerHTML = heat
    .map(
      (item) => `
        <div class="heat-item">
          <div>
            <strong>${item.zone}</strong>
            <div class="muted">Heat index</div>
          </div>
          <div class="heat-dot"></div>
          <strong>${item.level}</strong>
        </div>
      `
    )
    .join("");
}

const predictionTrend = document.getElementById("predictionTrendChart");
if (predictionTrend) {
  new Chart(predictionTrend, {
    type: "line",
    data: {
      labels: ["Now", "+6h", "+12h", "+18h", "+24h"],
      datasets: [
        {
          label: "Risk projection",
          data: [0.62, 0.68, 0.74, 0.79, 0.81],
          borderColor: "#f97316",
          backgroundColor: "rgba(249, 115, 22, 0.2)",
          tension: 0.35,
          fill: true,
        },
      ],
    },
    options: chartDefaults,
  });
}

const predictionImportance = document.getElementById("predictionImportanceChart");
if (predictionImportance) {
  new Chart(predictionImportance, {
    type: "bar",
    data: {
      labels: ["Humidity", "Wind", "Vegetation", "Temp", "Soil"],
      datasets: [
        {
          label: "Contribution",
          data: [0.31, 0.24, 0.18, 0.14, 0.13],
          backgroundColor: ["#ef4444", "#f97316", "#fbbf24", "#38bdf8", "#22c55e"],
        },
      ],
    },
    options: chartDefaults,
  });
}

const predictionHistory = document.getElementById("predictionHistory");
if (predictionHistory) {
  const history = [
    { region: "Sierra Corridor", score: "82%", time: "3m ago" },
    { region: "Central Basin", score: "71%", time: "15m ago" },
    { region: "Coastal Ridge", score: "58%", time: "1h ago" },
  ];
  predictionHistory.innerHTML = history
    .map(
      (entry) => `
        <div class="history-item">
          <strong>${entry.region}</strong>
          <div class="history-meta">
            <span>Risk score: ${entry.score}</span>
            <span>${entry.time}</span>
          </div>
        </div>
      `
    )
    .join("");
}

const wildfireTrend = document.getElementById("wildfireTrendChart");
if (wildfireTrend) {
  new Chart(wildfireTrend, {
    type: "line",
    data: {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      datasets: [
        {
          label: "Incidents",
          data: [48, 52, 61, 70, 82, 95],
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.2)",
          tension: 0.35,
          fill: true,
        },
        {
          label: "Containment rate",
          data: [62, 64, 66, 68, 70, 73],
          borderColor: "#22c55e",
          tension: 0.35,
        },
      ],
    },
    options: chartDefaults,
  });
}

const riskForecast = document.getElementById("riskForecastChart");
if (riskForecast) {
  new Chart(riskForecast, {
    type: "line",
    data: {
      labels: ["Day 1", "Day 4", "Day 7", "Day 10", "Day 14"],
      datasets: [
        {
          label: "Forecast",
          data: [0.62, 0.68, 0.74, 0.79, 0.82],
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

const weatherCorrelation = document.getElementById("weatherCorrelationChart");
if (weatherCorrelation) {
  new Chart(weatherCorrelation, {
    type: "radar",
    data: {
      labels: ["Humidity", "Wind", "Temp", "Rain", "Soil"],
      datasets: [
        {
          label: "Correlation",
          data: [0.78, 0.62, 0.7, 0.43, 0.55],
          backgroundColor: "rgba(56, 189, 248, 0.2)",
          borderColor: "#38bdf8",
        },
      ],
    },
    options: chartDefaults,
  });
}

const regionalComparison = document.getElementById("regionalComparisonChart");
if (regionalComparison) {
  new Chart(regionalComparison, {
    type: "bar",
    data: {
      labels: ["Sierra", "Central", "Coastal", "Desert"],
      datasets: [
        {
          label: "Risk index",
          data: [82, 71, 58, 63],
          backgroundColor: ["#ef4444", "#f97316", "#fbbf24", "#22c55e"],
        },
      ],
    },
    options: chartDefaults,
  });
}

const analyticsFeature = document.getElementById("analyticsFeatureChart");
if (analyticsFeature) {
  new Chart(analyticsFeature, {
    type: "bar",
    data: {
      labels: ["Humidity", "Wind", "Vegetation", "Temp", "Soil"],
      datasets: [
        {
          label: "Importance",
          data: [0.33, 0.25, 0.18, 0.14, 0.1],
          backgroundColor: ["#ef4444", "#f97316", "#fbbf24", "#38bdf8", "#22c55e"],
        },
      ],
    },
    options: chartDefaults,
  });
}

const anomalyChart = document.getElementById("anomalyChart");
if (anomalyChart) {
  new Chart(anomalyChart, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Anomalies",
          data: [
            { x: 1, y: 62 },
            { x: 2, y: 70 },
            { x: 3, y: 68 },
            { x: 4, y: 90 },
            { x: 5, y: 72 },
          ],
          backgroundColor: "#ef4444",
        },
      ],
    },
    options: chartDefaults,
  });
}

const performanceChart = document.getElementById("performanceChart");
if (performanceChart) {
  new Chart(performanceChart, {
    type: "line",
    data: {
      labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
      datasets: [
        {
          label: "Precision",
          data: [0.84, 0.86, 0.88, 0.9],
          borderColor: "#22c55e",
          tension: 0.35,
        },
        {
          label: "Recall",
          data: [0.8, 0.82, 0.85, 0.87],
          borderColor: "#f97316",
          tension: 0.35,
        },
      ],
    },
    options: chartDefaults,
  });
}

const timelineSlider = document.getElementById("timelineSlider");
const timelineValue = document.getElementById("timelineValue");
if (timelineSlider && timelineValue) {
  timelineSlider.addEventListener("input", (event) => {
    const value = Number(event.target.value);
    timelineValue.textContent = `${value}h`;
  });
}

const humidityChart = document.getElementById("humidityChart");
if (humidityChart) {
  new Chart(humidityChart, {
    type: "line",
    data: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      datasets: [
        {
          label: "Humidity",
          data: [28, 24, 22, 20, 18, 19, 21],
          borderColor: "#38bdf8",
          backgroundColor: "rgba(56, 189, 248, 0.2)",
          tension: 0.3,
          fill: true,
        },
      ],
    },
    options: chartDefaults,
  });
}

const windChart = document.getElementById("windChart");
if (windChart) {
  new Chart(windChart, {
    type: "line",
    data: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      datasets: [
        {
          label: "Wind speed",
          data: [4.2, 5.1, 6.3, 7.4, 8.0, 7.1, 6.5],
          borderColor: "#f97316",
          backgroundColor: "rgba(249, 115, 22, 0.2)",
          tension: 0.3,
          fill: true,
        },
      ],
    },
    options: chartDefaults,
  });
}

const rainChart = document.getElementById("rainChart");
if (rainChart) {
  new Chart(rainChart, {
    type: "bar",
    data: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      datasets: [
        {
          label: "Rainfall",
          data: [0, 0, 1, 0, 2, 1, 0],
          backgroundColor: "#22c55e",
        },
      ],
    },
    options: chartDefaults,
  });
}

const droughtChart = document.getElementById("droughtChart");
if (droughtChart) {
  new Chart(droughtChart, {
    type: "line",
    data: {
      labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
      datasets: [
        {
          label: "Drought index",
          data: [0.68, 0.71, 0.74, 0.78],
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.15)",
          tension: 0.35,
          fill: true,
        },
      ],
    },
    options: chartDefaults,
  });
}

const riskFactors = document.getElementById("riskFactors");
if (riskFactors) {
  const factors = [
    { label: "Dryness index", score: "0.82" },
    { label: "Wind alignment", score: "0.74" },
    { label: "Fuel stress", score: "0.69" },
    { label: "Lightning risk", score: "0.41" },
  ];
  riskFactors.innerHTML = factors
    .map(
      (item) => `
        <div class="factor-card">
          <span class="muted">${item.label}</span>
          <div class="factor-score">${item.score}</div>
        </div>
      `
    )
    .join("");
}

const weatherAlerts = document.getElementById("weatherAlerts");
if (weatherAlerts) {
  const alerts = [
    { title: "Low humidity warning", detail: "Humidity < 20%" },
    { title: "Wind surge advisory", detail: "Gusts > 7 m/s" },
    { title: "Drought watch", detail: "Dryness index > 0.75" },
  ];
  weatherAlerts.innerHTML = alerts
    .map(
      (alert) => `
        <div class="alert-item">
          <strong>${alert.title}</strong>
          <div class="alert-meta">
            <span>${alert.detail}</span>
            <span>Active</span>
          </div>
        </div>
      `
    )
    .join("");
}
