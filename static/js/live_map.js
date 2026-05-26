const mapFrame = document.getElementById("mapFrame");
const layerControls = document.getElementById("layerControls");
const regionFilters = document.getElementById("regionFilters");
const incidentCount = document.getElementById("incidentCount");
const highestRisk = document.getElementById("highestRisk");
const weatherAlert = document.getElementById("weatherAlert");
const weatherAlertMeta = document.getElementById("weatherAlertMeta");
const responsePosture = document.getElementById("responsePosture");
const responseMeta = document.getElementById("responseMeta");
const mapSyncStatus = document.getElementById("mapSyncStatus");
const mapLastUpdated = document.getElementById("mapLastUpdated");
const mapRegionLabel = document.getElementById("mapRegionLabel");
const intelOverlays = document.getElementById("intelOverlays");
const toggleFullscreen = document.getElementById("toggleFullscreen");
const mapShell = document.getElementById("mapShell");
const timelineSlider = document.getElementById("timelineSlider");
const timelineValue = document.getElementById("timelineValue");
const timelineSummary = document.getElementById("timelineSummary");

const baseParams = {
  heat: true,
  markers: true,
  zones: true,
  satellite: false,
  weather: false,
};

const intelFeed = [
  {
    title: "Aerial surveillance",
    detail: "Drone corridor active over Sierra Corridor",
  },
  {
    title: "Resource staging",
    detail: "Type-1 crews repositioned to Central Basin",
  },
  {
    title: "Critical infrastructure",
    detail: "Powerline corridor flagged near Coastal Ridge",
  },
  {
    title: "Evacuation readiness",
    detail: "Desert Edge shelters on standby",
  },
];

const alertFeed = [
  {
    title: "Wind surge advisory",
    meta: "Gusts 8.1 m/s",
  },
  {
    title: "Humidity drop watch",
    meta: "Moisture index below 20%",
  },
  {
    title: "Drought escalation",
    meta: "Soil dryness trending upward",
  },
];

const responseStates = [
  {
    title: "Elevated readiness",
    meta: "Resources staged: 18 units",
  },
  {
    title: "High alert",
    meta: "Resources staged: 24 units",
  },
  {
    title: "Monitoring",
    meta: "Resources staged: 12 units",
  },
];

const formatTime = (date) =>
  date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const updateMapSrc = () => {
  if (!mapFrame) {
    return;
  }
  const params = new URLSearchParams();
  Object.entries(baseParams).forEach(([key, value]) => {
    params.set(key, value ? "1" : "0");
  });
  mapFrame.src = `/map/wildfire?${params.toString()}`;
};

const updateRegions = () => {
  if (!regionFilters || !mapRegionLabel) {
    return;
  }
  const active = Array.from(regionFilters.querySelectorAll("input:checked")).map(
    (input) => input.dataset.region
  );
  mapRegionLabel.textContent = active.length
    ? `${active.join(", ")}`
    : "All regions";
};

const updateIntel = () => {
  if (!intelOverlays) {
    return;
  }
  intelOverlays.innerHTML = intelFeed
    .map(
      (item) => `
        <div class="intel-item">
          <strong>${item.title}</strong>
          <span class="muted">${item.detail}</span>
        </div>
      `
    )
    .join("");
};

const cycleStatus = () => {
  const alert = alertFeed[Math.floor(Math.random() * alertFeed.length)];
  const response = responseStates[Math.floor(Math.random() * responseStates.length)];
  if (weatherAlert) {
    weatherAlert.textContent = alert.title;
  }
  if (weatherAlertMeta) {
    weatherAlertMeta.textContent = alert.meta;
  }
  if (responsePosture) {
    responsePosture.textContent = response.title;
  }
  if (responseMeta) {
    responseMeta.textContent = response.meta;
  }
  if (incidentCount) {
    const count = Math.floor(8 + Math.random() * 10);
    incidentCount.textContent = `${count} active incidents`;
  }
  if (highestRisk) {
    const zones = ["Sierra Corridor", "Central Basin", "Coastal Ridge", "Desert Edge"];
    highestRisk.textContent = `Highest risk: ${zones[Math.floor(Math.random() * zones.length)]}`;
  }
  if (mapLastUpdated) {
    mapLastUpdated.textContent = `Last sync ${formatTime(new Date())}`;
  }
  if (mapSyncStatus) {
    mapSyncStatus.textContent = "Telemetry: Live";
  }
};

const updateTimeline = () => {
  if (!timelineSlider || !timelineValue || !timelineSummary) {
    return;
  }
  const hours = Number(timelineSlider.value);
  timelineValue.textContent = `${hours}h`;
  timelineSummary.querySelector("span").textContent =
    hours === 0
      ? "Streaming live incident telemetry"
      : `Filtering incidents within last ${hours}h`;
};

if (layerControls) {
  layerControls.querySelectorAll("input[data-layer]").forEach((input) => {
    baseParams[input.dataset.layer] = input.checked;
    input.addEventListener("change", () => {
      baseParams[input.dataset.layer] = input.checked;
      updateMapSrc();
    });
  });
}

if (regionFilters) {
  regionFilters.querySelectorAll("input[data-region]").forEach((input) => {
    input.addEventListener("change", updateRegions);
  });
}

if (toggleFullscreen && mapShell) {
  toggleFullscreen.addEventListener("click", () => {
    mapShell.classList.toggle("fullscreen");
    toggleFullscreen.textContent = mapShell.classList.contains("fullscreen")
      ? "Exit fullscreen"
      : "Fullscreen";
  });
}

if (timelineSlider) {
  timelineSlider.addEventListener("input", updateTimeline);
}

updateRegions();
updateIntel();
updateTimeline();
cycleStatus();
updateMapSrc();
setInterval(cycleStatus, 15000);
