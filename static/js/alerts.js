const alertCards = document.getElementById("alertCards");
const incidentFeed = document.getElementById("incidentFeed");
const notificationCenter = document.getElementById("notificationCenter");
const alertTimeline = document.getElementById("alertTimeline");
const aiRecommendations = document.getElementById("aiRecommendations");
const escalationWorkflow = document.getElementById("escalationWorkflow");
const responsePanel = document.getElementById("responsePanel");
const alertHistory = document.getElementById("alertHistory");
const responseStatus = document.getElementById("responseStatus");
const alertSearch = document.getElementById("alertSearch");
const severityFilters = document.getElementById("severityFilters");
const showActiveOnly = document.getElementById("showActiveOnly");
const showEscalated = document.getElementById("showEscalated");
const alertStatus = document.getElementById("alertStatus");
const alertSync = document.getElementById("alertSync");
const alertRegion = document.getElementById("alertRegion");
const criticalCount = document.getElementById("criticalCount");
const activeIncidents = document.getElementById("activeIncidents");
const escalationCount = document.getElementById("escalationCount");
const responseSla = document.getElementById("responseSla");

const formatTime = (date) =>
  date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const alertData = [
  {
    id: "ALT-201",
    title: "Extreme wind surge detected",
    region: "Sierra Corridor",
    severity: "critical",
    status: "Active",
    escalated: true,
    owner: "Ops Alpha",
    eta: "6 min",
    detail: "Gusts exceeding 12 m/s with rapid spread potential.",
    time: "2m ago",
  },
  {
    id: "ALT-187",
    title: "Fuel moisture collapse",
    region: "Central Basin",
    severity: "high",
    status: "Active",
    escalated: true,
    owner: "Ops Bravo",
    eta: "12 min",
    detail: "Moisture index below 18% across 3 sectors.",
    time: "6m ago",
  },
  {
    id: "ALT-175",
    title: "Containment breach",
    region: "Coastal Ridge",
    severity: "critical",
    status: "Active",
    escalated: true,
    owner: "Ops Delta",
    eta: "9 min",
    detail: "Fireline disruption along northern perimeter.",
    time: "12m ago",
  },
  {
    id: "ALT-162",
    title: "Dry lightning watch",
    region: "Desert Edge",
    severity: "moderate",
    status: "Monitoring",
    escalated: false,
    owner: "Ops Echo",
    eta: "18 min",
    detail: "Atmospheric instability with potential ignition.",
    time: "24m ago",
  },
  {
    id: "ALT-149",
    title: "Smoke column escalation",
    region: "Sierra Corridor",
    severity: "high",
    status: "Active",
    escalated: false,
    owner: "Ops Alpha",
    eta: "14 min",
    detail: "Vertical plume growth detected by drone imagery.",
    time: "34m ago",
  },
  {
    id: "ALT-132",
    title: "Humidity recovery",
    region: "Central Basin",
    severity: "low",
    status: "Resolved",
    escalated: false,
    owner: "Ops Bravo",
    eta: "Resolved",
    detail: "Moisture levels stabilized after rain band.",
    time: "1h ago",
  },
];

const incidentData = [
  { name: "Pine Valley Fire", status: "Active", size: "1,420 ha", crews: "12 crews" },
  { name: "Cedar Ridge Fire", status: "Contained", size: "320 ha", crews: "5 crews" },
  { name: "Lagoon Flats", status: "Escalating", size: "640 ha", crews: "8 crews" },
  { name: "North Basin", status: "Active", size: "410 ha", crews: "6 crews" },
];

const notificationData = [
  { title: "Dispatch issued", meta: "Ops Alpha • 3 units", time: "1m ago" },
  { title: "Evacuation warning", meta: "Central Basin • Level 2", time: "9m ago" },
  { title: "Drone surveillance", meta: "Coastal Ridge • Live feed", time: "14m ago" },
  { title: "Containment update", meta: "Lagoon Flats • 45%", time: "26m ago" },
];

const timelineData = [
  { time: "02:06 UTC", event: "Alert ALT-201 escalated to critical" },
  { time: "01:58 UTC", event: "Ops Alpha acknowledged wind surge" },
  { time: "01:42 UTC", event: "Containment breach detected on Coastal Ridge" },
  { time: "01:22 UTC", event: "Dry lightning watch issued for Desert Edge" },
  { time: "00:57 UTC", event: "Fuel moisture collapse triggered" },
];

const recommendationData = [
  {
    title: "Deploy aerial suppression to Sierra Corridor",
    detail: "Projected spread +18% in next 3 hours based on wind shift.",
  },
  {
    title: "Pre-stage evacuation units near Central Basin",
    detail: "Population exposure risk elevated by 0.22 in model.",
  },
  {
    title: "Activate mobile weather station",
    detail: "Humidity volatility could trigger new ignition.",
  },
];

const workflowSteps = [
  {
    title: "Detection",
    detail: "AI sensor fusion detects escalation signatures.",
  },
  {
    title: "Verification",
    detail: "Ops analyst validates signals and assigns severity.",
  },
  {
    title: "Dispatch",
    detail: "Response units mobilized and routed.",
  },
  {
    title: "Containment",
    detail: "Field commanders relay status updates.",
  },
];

const responseData = [
  { label: "Active strike teams", value: "18" },
  { label: "Air assets", value: "6" },
  { label: "Engines deployed", value: "42" },
  { label: "Medical standby", value: "4" },
];

const historyData = [
  { title: "ALT-122 resolved", meta: "Central Basin • 2h ago" },
  { title: "ALT-118 acknowledged", meta: "Sierra Corridor • 4h ago" },
  { title: "ALT-110 escalated", meta: "Coastal Ridge • 7h ago" },
];

const responseStatusData = [
  { label: "Operations", status: "Fully staffed" },
  { label: "Air command", status: "On call" },
  { label: "Logistics", status: "Stable" },
  { label: "Communications", status: "SLA green" },
];

const renderAlerts = (alerts) => {
  if (!alertCards) {
    return;
  }
  if (!alerts.length) {
    alertCards.innerHTML = `
      <div class="alert-card empty">
        <strong>No alerts match current filters</strong>
        <span class="muted">Adjust severity or search terms.</span>
      </div>
    `;
    return;
  }
  alertCards.innerHTML = alerts
    .map(
      (alert) => `
        <div class="alert-card ${alert.severity}">
          <div class="alert-card-header">
            <div>
              <strong>${alert.title}</strong>
              <div class="muted">${alert.region} · ${alert.id}</div>
            </div>
            <span class="severity-pill ${alert.severity}">${alert.severity}</span>
          </div>
          <p class="alert-detail">${alert.detail}</p>
          <div class="alert-card-footer">
            <span>${alert.status}</span>
            <span>${alert.owner}</span>
            <span>ETA ${alert.eta}</span>
            <span>${alert.time}</span>
          </div>
        </div>
      `
    )
    .join("");
};

const renderIncidents = () => {
  if (!incidentFeed) {
    return;
  }
  incidentFeed.innerHTML = incidentData
    .map(
      (incident) => `
        <div class="incident-item">
          <strong>${incident.name}</strong>
          <div class="incident-meta">
            <span>${incident.status}</span>
            <span>${incident.size}</span>
            <span>${incident.crews}</span>
          </div>
        </div>
      `
    )
    .join("");
};

const renderNotifications = () => {
  if (!notificationCenter) {
    return;
  }
  notificationCenter.innerHTML = notificationData
    .map(
      (note) => `
        <div class="notification-item">
          <strong>${note.title}</strong>
          <div class="alert-meta">
            <span>${note.meta}</span>
            <span>${note.time}</span>
          </div>
        </div>
      `
    )
    .join("");
};

const renderTimeline = () => {
  if (!alertTimeline) {
    return;
  }
  alertTimeline.innerHTML = timelineData
    .map(
      (item) => `
        <div class="timeline-item">
          <strong>${item.time}</strong>
          <span class="muted">${item.event}</span>
        </div>
      `
    )
    .join("");
};

const renderRecommendations = () => {
  if (!aiRecommendations) {
    return;
  }
  aiRecommendations.innerHTML = recommendationData
    .map(
      (item) => `
        <div class="recommendation-item">
          <strong>${item.title}</strong>
          <span class="muted">${item.detail}</span>
        </div>
      `
    )
    .join("");
};

const renderWorkflow = () => {
  if (!escalationWorkflow) {
    return;
  }
  escalationWorkflow.innerHTML = workflowSteps
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

const renderResponsePanel = () => {
  if (!responsePanel) {
    return;
  }
  responsePanel.innerHTML = responseData
    .map(
      (item) => `
        <div class="response-item">
          <span class="muted">${item.label}</span>
          <strong>${item.value}</strong>
        </div>
      `
    )
    .join("");
};

const renderHistory = () => {
  if (!alertHistory) {
    return;
  }
  alertHistory.innerHTML = historyData
    .map(
      (entry) => `
        <div class="history-item">
          <strong>${entry.title}</strong>
          <div class="history-meta">
            <span>${entry.meta}</span>
          </div>
        </div>
      `
    )
    .join("");
};

const renderResponseStatus = () => {
  if (!responseStatus) {
    return;
  }
  responseStatus.innerHTML = responseStatusData
    .map(
      (status) => `
        <div class="status-item">
          <span>${status.label}</span>
          <strong>${status.status}</strong>
        </div>
      `
    )
    .join("");
};

const updateKpis = () => {
  if (criticalCount) {
    criticalCount.textContent = alertData.filter((alert) => alert.severity === "critical").length;
  }
  if (activeIncidents) {
    activeIncidents.textContent = incidentData.length;
  }
  if (escalationCount) {
    escalationCount.textContent = alertData.filter((alert) => alert.escalated).length;
  }
  if (responseSla) {
    responseSla.textContent = "12 min";
  }
};

const applyFilters = () => {
  const search = alertSearch?.value?.toLowerCase() ?? "";
  const activeOnly = showActiveOnly?.checked ?? false;
  const escalatedOnly = showEscalated?.checked ?? false;
  const activeFilter = severityFilters?.querySelector(".filter-chip.active");
  const severity = activeFilter?.dataset?.severity ?? "all";

  const filtered = alertData.filter((alert) => {
    if (severity !== "all" && alert.severity !== severity) {
      return false;
    }
    if (activeOnly && alert.status !== "Active") {
      return false;
    }
    if (escalatedOnly && !alert.escalated) {
      return false;
    }
    if (!search) {
      return true;
    }
    const haystack = `${alert.title} ${alert.region} ${alert.id} ${alert.owner}`.toLowerCase();
    return haystack.includes(search);
  });

  renderAlerts(filtered);
  if (alertStatus) {
    alertStatus.textContent = filtered.some((alert) => alert.severity === "critical")
      ? "Status: Elevated"
      : "Status: Monitoring";
  }
  if (alertSync) {
    alertSync.textContent = `Last sync ${formatTime(new Date())}`;
  }
  if (alertRegion) {
    const regions = Array.from(new Set(filtered.map((alert) => alert.region)));
    alertRegion.textContent = regions.length ? regions.join(", ") : "Multi-region coverage";
  }
};

if (severityFilters) {
  severityFilters.querySelectorAll(".filter-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      severityFilters.querySelectorAll(".filter-chip").forEach((item) => {
        item.classList.remove("active");
      });
      chip.classList.add("active");
      applyFilters();
    });
  });
}

if (alertSearch) {
  alertSearch.addEventListener("input", applyFilters);
}

if (showActiveOnly) {
  showActiveOnly.addEventListener("change", applyFilters);
}

if (showEscalated) {
  showEscalated.addEventListener("change", applyFilters);
}

renderIncidents();
renderNotifications();
renderTimeline();
renderRecommendations();
renderWorkflow();
renderResponsePanel();
renderHistory();
renderResponseStatus();
updateKpis();
applyFilters();
setInterval(applyFilters, 15000);
