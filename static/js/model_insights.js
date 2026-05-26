document.addEventListener('DOMContentLoaded', () => {
    console.log("Model Insights JS Loaded");

    const chartColors = {
        primary: 'rgba(255, 99, 132, 0.8)',
        secondary: 'rgba(54, 162, 235, 0.8)',
        tertiary: 'rgba(255, 206, 86, 0.8)',
        green: 'rgba(75, 192, 192, 0.8)',
        fire: 'rgba(255, 69, 0, 0.8)',
        shapPos: '#ff0051',
        shapNeg: '#008bfb',
        muted: 'rgba(255, 255, 255, 0.5)'
    };

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#e0e0e0' } }
        },
        scales: {
            x: {
                ticks: { color: '#e0e0e0' },
                grid: { color: 'rgba(255, 255, 255, 0.05)' }
            },
            y: {
                ticks: { color: '#e0e0e0' },
                grid: { color: 'rgba(255, 255, 255, 0.05)' }
            }
        }
    };

    // 1. Feature Importance Chart
    const fiCtx = document.getElementById('featureImportanceChart').getContext('2d');
    new Chart(fiCtx, {
        type: 'bar',
        data: {
            labels: ['VPD (Vegetation Dryness)', 'Wind Speed', 'Temperature', 'Soil Moisture', 'Relative Humidity', 'Elevation', 'Solar Radiation', 'Precipitation (7d)'],
            datasets: [{
                label: 'Relative Importance Score',
                data: [0.32, 0.18, 0.15, 0.12, 0.09, 0.06, 0.05, 0.03],
                backgroundColor: chartColors.secondary,
                borderWidth: 1,
                borderColor: chartColors.secondary
            }]
        },
        options: {
            ...commonOptions,
            indexAxis: 'y', // Makes it a horizontal bar chart
            plugins: {
                legend: { display: false }
            }
        }
    });

    // 2. SHAP Summary Chart (Simulated with Floating Bars / Bar charts with diverging colors)
    const shapCtx = document.getElementById('shapSummaryChart').getContext('2d');
    new Chart(shapCtx, {
        type: 'bar',
        data: {
            labels: ['VPD (High)', 'Wind Speed (High)', 'Temperature (High)', 'Soil Moisture (Low)', 'Rel. Humidity (Low)', 'Precipitation 7d (Zero)'],
            datasets: [
                {
                    label: 'Pushes prediction higher (+ Risk)',
                    data: [0.28, 0.22, 0.19, 0.14, 0.11, 0.05],
                    backgroundColor: chartColors.shapPos,
                },
                {
                    label: 'Pushes prediction lower (- Risk)',
                    data: [-0.05, -0.02, -0.04, -0.01, -0.03, 0],
                    backgroundColor: chartColors.shapNeg,
                }
            ]
        },
        options: {
            ...commonOptions,
            indexAxis: 'y',
            scales: {
                x: {
                    ...commonOptions.scales.x,
                    stacked: true,
                    title: { display: true, text: 'SHAP Value (Impact on Model Output)', color: '#e0e0e0' }
                },
                y: {
                    ...commonOptions.scales.y,
                    stacked: true
                }
            }
        }
    });

    // 3. Precision-Recall Curve
    const prCtx = document.getElementById('precisionRecallChart').getContext('2d');
    
    // Generate a typical PR curve data
    const prData = [];
    for(let i=0; i<=100; i+=5) {
        let recall = i/100;
        let precision = 1 - Math.pow(recall, 4) * 0.15; // Smooth drop-off
        // add some jitter to precision
        if (recall < 0.8) precision = Math.max(0.92, precision + (Math.random()*0.02 - 0.01));
        prData.push({x: recall, y: Math.min(1, precision)});
    }

    new Chart(prCtx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Precision-Recall Curve (XGB-LSTM)',
                data: prData,
                borderColor: chartColors.green,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                x: {
                    type: 'linear',
                    ...commonOptions.scales.x,
                    title: { display: true, text: 'Recall', color: '#e0e0e0' }
                },
                y: {
                    ...commonOptions.scales.y,
                    min: 0.6,
                    max: 1.05,
                    title: { display: true, text: 'Precision', color: '#e0e0e0' }
                }
            }
        }
    });
});
