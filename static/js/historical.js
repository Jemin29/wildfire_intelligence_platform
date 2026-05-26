import { fetchWithTimeout } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    console.log("Historical Wildfire Intelligence JS Loaded");

    // Chart instances
    let yearlyTrendsChart, seasonalPatternsChart, historicalHeatmapChart, regionWiseHistoryChart, historicalRiskForecastChart;

    // DOM Elements
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    const kpiTotalIncidents = document.getElementById('kpi-total-incidents');
    const kpiTotalAcres = document.getElementById('kpi-total-acres');
    const kpiTotalStructures = document.getElementById('kpi-total-structures');
    const kpiTotalCost = document.getElementById('kpi-total-cost');

    const chartColors = {
        primary: 'rgba(255, 99, 132, 0.8)',
        secondary: 'rgba(54, 162, 235, 0.8)',
        tertiary: 'rgba(255, 206, 86, 0.8)',
        quaternary: 'rgba(75, 192, 192, 0.8)',
        fire: 'rgba(255, 69, 0, 0.7)',
        smoke: 'rgba(169, 169, 169, 0.7)',
        orange: 'rgba(255, 159, 64, 0.8)',
    };

    const commonChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#e0e0e0'
                }
            }
        },
        scales: {
            x: {
                ticks: { color: '#e0e0e0' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            },
            y: {
                ticks: { color: '#e0e0e0' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            }
        }
    };

    // Mock Data Generator
    const generateMockData = (filters) => {
        const { yearRange, region, metric } = filters;
        const numYears = yearRange === 'all' ? 20 : parseInt(yearRange);
        const currentYear = new Date().getFullYear();
        
        const data = {
            kpis: {
                totalIncidents: Math.floor(Math.random() * 50000) + 10000,
                totalAcres: Math.floor(Math.random() * 10000000) + 2000000,
                totalStructures: Math.floor(Math.random() * 20000) + 5000,
                totalCost: Math.floor(Math.random() * 50) + 10, // In Billions
            },
            yearlyTrends: {
                labels: Array.from({ length: numYears }, (_, i) => currentYear - numYears + i + 1),
                datasets: [
                    {
                        label: 'Acres Burned (Millions)',
                        data: Array.from({ length: numYears }, () => (Math.random() * 10).toFixed(2)),
                        borderColor: chartColors.primary,
                        backgroundColor: chartColors.primary,
                        type: 'line',
                        yAxisID: 'y',
                    },
                    {
                        label: 'Incident Count',
                        data: Array.from({ length: numYears }, () => Math.floor(Math.random() * 8000) + 1000),
                        borderColor: chartColors.secondary,
                        backgroundColor: chartColors.secondary,
                        type: 'bar',
                        yAxisID: 'y1',
                    }
                ]
            },
            seasonalPatterns: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Average Monthly Incidents',
                    data: Array.from({ length: 12 }, () => Math.floor(Math.random() * 1500) + 100),
                    backgroundColor: chartColors.orange,
                }]
            },
            historicalHeatmap: {
                // This would be complex geo-data. We'll simulate with a bubble chart.
                datasets: [{
                    label: 'Wildfire Hotspots',
                    data: Array.from({ length: 50 }, () => ({
                        x: (Math.random() * 360 - 180).toFixed(2),
                        y: (Math.random() * 180 - 90).toFixed(2),
                        r: Math.floor(Math.random() * 20) + 5 // Radius represents intensity
                    })),
                    backgroundColor: chartColors.fire,
                }]
            },
            regionWiseHistory: {
                labels: ['California', 'Pacific NW', 'Southwest', 'Rockies', 'Australia'],
                datasets: [{
                    label: 'Total Incidents by Region',
                    data: Array.from({ length: 5 }, () => Math.floor(Math.random() * 10000) + 2000),
                    backgroundColor: [
                        chartColors.primary,
                        chartColors.secondary,
                        chartColors.tertiary,
                        chartColors.quaternary,
                        chartColors.orange,
                    ],
                }]
            },
            historicalRiskForecast: {
                labels: Array.from({ length: 12 }, (_, i) => `Q${Math.floor(i/3)+1} '${(currentYear - 3) + Math.floor(i/4)}`),
                datasets: [
                    {
                        label: 'Predicted Risk Level',
                        data: Array.from({ length: 12 }, () => Math.random() * 100),
                        borderColor: chartColors.secondary,
                        backgroundColor: 'transparent',
                        type: 'line',
                        tension: 0.4,
                    },
                    {
                        label: 'Actual Incidents',
                        data: Array.from({ length: 12 }, () => Math.random() * 100),
                        borderColor: chartColors.primary,
                        backgroundColor: 'transparent',
                        type: 'line',
                        tension: 0.4,
                    }
                ]
            }
        };
        return data;
    };

    const updateKpis = (data) => {
        kpiTotalIncidents.textContent = data.totalIncidents.toLocaleString();
        kpiTotalAcres.textContent = data.totalAcres.toLocaleString();
        kpiTotalStructures.textContent = data.totalStructures.toLocaleString();
        kpiTotalCost.textContent = `$${data.totalCost}B`;
    };

    const createOrUpdateChart = (chartInstance, chartId, config) => {
        const ctx = document.getElementById(chartId).getContext('2d');
        if (chartInstance) {
            chartInstance.data = config.data;
            chartInstance.options = config.options;
            chartInstance.update();
        } else {
            return new Chart(ctx, config);
        }
    };

    const renderCharts = (data) => {
        // Yearly Trends Chart
        yearlyTrendsChart = createOrUpdateChart(yearlyTrendsChart, 'yearlyTrendsChart', {
            type: 'bar',
            data: data.yearlyTrends,
            options: {
                ...commonChartOptions,
                scales: {
                    ...commonChartOptions.scales,
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Acres Burned (Millions)', color: '#e0e0e0' },
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Incident Count', color: '#e0e0e0' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });

        // Seasonal Patterns Chart
        seasonalPatternsChart = createOrUpdateChart(seasonalPatternsChart, 'seasonalPatternsChart', {
            type: 'bar',
            data: data.seasonalPatterns,
            options: { ...commonChartOptions, indexAxis: 'y' }
        });

        // Historical Heatmap (Bubble Chart)
        historicalHeatmapChart = createOrUpdateChart(historicalHeatmapChart, 'historicalHeatmapChart', {
            type: 'bubble',
            data: data.historicalHeatmap,
            options: {
                ...commonChartOptions,
                plugins: {
                    ...commonChartOptions.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Hotspot: (Lat: ${context.parsed.y}, Lon: ${context.parsed.x}), Intensity: ${context.parsed.r}`;
                            }
                        }
                    }
                },
                scales: {
                    x: { ...commonChartOptions.scales.x, title: { display: true, text: 'Longitude', color: '#e0e0e0' } },
                    y: { ...commonChartOptions.scales.y, title: { display: true, text: 'Latitude', color: '#e0e0e0' } }
                }
            }
        });

        // Region-wise History Chart
        regionWiseHistoryChart = createOrUpdateChart(regionWiseHistoryChart, 'regionWiseHistoryChart', {
            type: 'doughnut',
            data: data.regionWiseHistory,
            options: { ...commonChartOptions, scales: {} }
        });

        // Historical Risk Forecast Chart
        historicalRiskForecastChart = createOrUpdateChart(historicalRiskForecastChart, 'historicalRiskForecastChart', {
            type: 'line',
            data: data.historicalRiskForecast,
            options: commonChartOptions
        });
    };

    const fetchDataAndUpdateDashboard = async () => {
        const filters = {
            region: document.getElementById('region-filter').value,
            yearRange: document.getElementById('year-range-filter').value,
            metric: document.getElementById('data-metric-filter').value,
        };

        // In a real app, you would fetch from an API:
        // const data = await fetchWithTimeout(`/api/historical-wildfires?region=${filters.region}&years=${filters.yearRange}`);
        const mockData = generateMockData(filters);

        updateKpis(mockData.kpis);
        renderCharts(mockData);
    };

    // Event Listeners
    applyFiltersBtn.addEventListener('click', fetchDataAndUpdateDashboard);

    // Initial Load
    fetchDataAndUpdateDashboard();
});
